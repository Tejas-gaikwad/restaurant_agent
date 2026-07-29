
import json, os
from datetime import date, datetime
from dotenv import load_dotenv
from tools import TOOLS
from openai import OpenAI

load_dotenv()

client = OpenAI()
DB_FILE = "bookings.json"


def _load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            data = json.load(f)
            return {int(k): v for k, v in data["bookings"].items()}, data["next_id"]
    return {}, 1

def _save():
    with open(DB_FILE, "w") as f:
        json.dump({"bookings": BOOKINGS, "next_id": _next_id[0]}, f, indent=2)

BOOKINGS, _start = _load()
_next_id = [_start]

class Agent:
    def __init__(self):
        system = f"""You are a restaurant concierge. Today is {date.today().isoformat()}.
            Never invent a guest's name — ask for it.
            Only ask for information that the tool you are about to call actually requires.
            When a guest wants to change or cancel a reservation, call find_booking with just
            their name first. Do not ask for date, time, or booking id up front — find_booking
            returns the booking id for you.
            If find_booking returns found: false, tell the guest no reservation exists and
            offer to make a new one. Do not ask for the same detail twice.
            When find_booking returns found: false, say so ONCE, then move on and help with a new
            booking. Never repeat a tool result you have already reported.
            Once you have name, date, time, and party_size, call check_availability and then
            book_table immediately. Do not ask the guest to confirm details they have already given.
            A reply of "yes" is confirmation — act on it, never ask again."""
        
        self.messages = [{"role": "system", "content": system}]
   
    def chat(self, user_message):

        if user_message == "/dump":
            for m in self.messages: print(m)
            return "---"
        if user_message == "/reset":
            self.messages = self.messages[:1]   # keep system prompt
            return "context cleared"

        self.messages.append({"role":"user", "content": user_message})

        for _ in range(10):
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                tools=TOOLS,
                max_tokens=500,
                temperature=0.7,
            )

            msg = resp.choices[0].message

            if not msg.tool_calls:
                # model is done — return its final text
                print("  (no tool call)")
                return msg.content

            # model wants to call one or more tools
            self.messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
            })

            for tool_call in msg.tool_calls:
                tool_input = json.loads(tool_call.function.arguments)
                print(f"  → calling {tool_call.function.name}({tool_input})")   # watch it think
                out = dispatch(tool_call.function.name, tool_input)
                print(f"  ← {out}")
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(out),
                })

                if tool_call.function.name == "book_table" and out.get("success"):
                    return out["message"]
        return "Stopped: hit max iterations."

MENU = [
    {"name": "Margherita Pizza", "price": 12, "tags": ["vegetarian"]},
    {"name": "Paneer Tikka",     "price": 14, "tags": ["vegetarian", "gluten-free"]},
    {"name": "Vegan Buddha Bowl", "price": 13, "tags": ["vegan", "gluten-free"]},
    {"name": "Grilled Salmon",   "price": 18, "tags": ["gluten-free"]},
    {"name": "Chicken Alfredo",  "price": 16, "tags": []},
]

BOOKED = set()

def find_booking(name):
    matches = [{"booking_id": bid, **b} for bid, b in BOOKINGS.items()
               if b["name"].strip().lower() == name.strip().lower()]
    if not matches:
        return {"found": False, "bookings": [],
                "message": f"No reservation found under '{name}'."}
    return {"found": True, "bookings": matches}

def get_menu(): 
    return MENU

CAPACITY = 20   # seats available per slot

BOOKINGS = {}   # {booking_id: {"date":..., "time":..., "party_size":..., "name":...}}
_next_id = [1]

def seats_taken(date, time, exclude_id=None):
    return sum(b["party_size"] for bid, b in BOOKINGS.items()
               if b["date"] == date and b["time"] == time and bid != exclude_id)

def check_availability(date, time, party_size, exclude_booking_id=None):
    if party_size > 12:
        return {"available": False, "reason": "Max party size is 12."}
    free = CAPACITY - seats_taken(date, time, exclude_booking_id)
    return {"available": party_size <= free, "seats_free": free}
def modify_booking(booking_id, party_size=None, date=None, time=None):
    b = BOOKINGS.get(booking_id)
    if not b:
        return {"success": False, "reason": "No such booking."}
    new = {**b, **{k: v for k, v in
                   {"party_size": party_size, "date": date, "time": time}.items() if v}}
    avail = check_availability(new["date"], new["time"], new["party_size"], exclude_booking_id=booking_id)
    if not avail["available"]:
        return {"success": False, "reason": avail.get("reason", "Not enough seats."), **avail}
    BOOKINGS[booking_id] = new
    _save()
    return {"success": True, "booking": new}

def book_table(date, time, party_size, name):
    bid = _next_id[0]; _next_id[0] += 1
    BOOKINGS[bid] = {"date": date, "time": time, "party_size": party_size, "name": name}
    _save()
    return {"success": True, "booking_id": bid,
            "message": f"Table for {party_size} booked for {name} on {date} at {time}."}

def cancel_booking(booking_id):
    _save()
    return {"success": bool(BOOKINGS.pop(booking_id, None))}

def dispatch(tool_name, tool_input):
    if tool_name == "get_menu":
        return get_menu()
    elif tool_name == "check_availability":
        return check_availability(**tool_input)
    elif tool_name == "book_table":
        return book_table(**tool_input)
    elif tool_name == "modify_booking":
        return modify_booking(**tool_input)
    elif tool_name == "cancel_booking":
        return cancel_booking(**tool_input)
    elif tool_name == "find_booking":
        return find_booking(**tool_input)
    else:
        return {"error": f"Unknown tool: {tool_name}"}


if __name__ == "__main__":
    agent = Agent()
    while True:
        user = input("> ")
        if user in ("quit", "exit"):
            break
        print(agent.chat(user))