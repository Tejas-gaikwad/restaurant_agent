import json, os

DB_FILE = "bookings.json"

MENU = [
    {"name": "Margherita Pizza", "price": 12, "tags": ["vegetarian"]},
    {"name": "Paneer Tikka",     "price": 14, "tags": ["vegetarian", "gluten-free"]},
    {"name": "Vegan Buddha Bowl", "price": 13, "tags": ["vegan", "gluten-free"]},
    {"name": "Grilled Salmon",   "price": 18, "tags": ["gluten-free"]},
    {"name": "Chicken Alfredo",  "price": 16, "tags": []},
]

CAPACITY = 20   # seats available per slot


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


def find_booking(name):
    matches = [{"booking_id": bid, **b} for bid, b in BOOKINGS.items()
               if b["name"].strip().lower() == name.strip().lower()]
    if not matches:
        return {"found": False, "bookings": [],
                "message": f"No reservation found under '{name}'."}
    return {"found": True, "bookings": matches}

def get_menu(): 
    return MENU

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
