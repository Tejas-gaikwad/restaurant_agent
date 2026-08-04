import json
from datetime import date
from dotenv import load_dotenv
from tool_specs import TOOLS
from openai import OpenAI
from booking_store import get_menu, check_availability, book_table, modify_booking, cancel_booking, find_booking, get_bookings, get_inventory, get_recipe, create_purchase_order, compute_prep_and_shortfall
from pydantic import BaseModel
from typing import Optional

load_dotenv()

client = OpenAI()


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

        print("User messaged :", user_message)

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
    elif tool_name == "get_bookings":          
        return get_bookings(**tool_input)
    elif tool_name == "get_inventory":         
        return get_inventory()
    elif tool_name == "get_recipe":            
        return get_recipe(**tool_input)
    elif tool_name == "create_purchase_order": 
        return create_purchase_order(**tool_input)
    elif tool_name == "compute_prep_and_shortfall":
        return compute_prep_and_shortfall(**tool_input)
    else:
        return {"error": f"Unknown tool: {tool_name}"}



class PlanStep(BaseModel):
    tool: str
    args_json: str          # JSON-encoded dict of args — structured outputs can't do free-form dicts
    reason: str            # why this step — for auditability

    @property
    def args(self) -> dict:
        return json.loads(self.args_json)

class Plan(BaseModel):
    goal: str
    steps: list[PlanStep]

def make_plan(goal: str) -> Plan:
    """One LLM call. The model designs the whole plan; it does NOT execute anything."""
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content":
                "You are a planning module. Given a goal, output an ordered list of steps "
                "as tool calls. Available tools: get_bookings(date), get_menu(), "
                "get_inventory(), compute_prep_and_shortfall(covers_by_dish), "
                "create_purchase_order(items). Do NOT execute — only plan. Each step's args_json "
                "must be a JSON-encoded object string (e.g. '{\"date\": \"2026-08-03\"}') holding "
                "that tool's arguments. It may reference the goal but you won't have results yet, "
                "so plan the structure."
                "When a step needs data produced by an earlier step, do not guess it. Reference the earlier step as '$stepN' (e.g. the argument for a later step might be '$step1')."
                },
            {"role": "user", "content": goal},
        ],
        response_format=Plan,
    )
    return completion.choices[0].message.parsed

def resolve(value, results):
    """Replace any '$stepN' reference with that step's actual result."""
    if isinstance(value, str) and value.startswith("$step"):
        idx = int(value[5:]) - 1          # "$step1" -> results[0]
        return results[idx]
    if isinstance(value, dict):
        return {k: resolve(v, results) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v, results) for v in value]
    return value

def execute_plan(plan: Plan):
    """Deterministic executor. No LLM in this loop — it just runs the steps."""
    results = []
    for i, step in enumerate(plan.steps, 1):
        args = resolve(step.args, results)
        print(f"  [{i}] {step.tool}({args})  — {step.reason}")
        out = dispatch(step.tool, args)
        print(f"      ← {out}")
        results.append(out)
    return results