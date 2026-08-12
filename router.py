from pydantic import BaseModel
from enum import Enum
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


class Route(str, Enum):
    booking = "booking"   # book / modify / cancel / availability
    kitchen = "kitchen"   # prep, inventory, purchasing, forecasting
    menu    = "menu"      # menu items, prices, dietary questions
    other   = "other"     # greetings, anything off-topic

class RoutingDecision(BaseModel):
    routes: list[Route]
    reason: str

def route_message(user_message, session=None) -> RoutingDecision:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",          # cheap model — routing is easy
        messages=[
            {"role": "system", "content":
                "Identify ALL distinct intents in the user's message and return every matching lane. "
                "A single message often spans multiple lanes — e.g. 'book a table and show the vegan "
                "options' is BOTH booking AND menu. Do not collapse to one; return all that apply.\n"
                "- booking: reservations (make/change/cancel/check a table)\n"
                "- menu: dishes, prices, dietary/allergen questions\n"
                "- kitchen: prep, inventory, ingredient ordering, forecasting\n"
                "- other: greetings or anything unrelated"},
            {"role": "user", "content": user_message},
        ],
        response_format=RoutingDecision,
    )
    return completion.choices[0].message.parsed