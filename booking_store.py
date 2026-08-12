import json, os

DB_FILE = "bookings.json"

MENU = [
    {"name": "Margherita Pizza", "price": 12, "tags": ["vegetarian"]},
    {"name": "Paneer Tikka",     "price": 14, "tags": ["vegetarian", "gluten-free"]},
    {"name": "Vegan Buddha Bowl", "price": 13, "tags": ["vegan", "gluten-free"]},
    {"name": "Grilled Salmon",   "price": 18, "tags": ["gluten-free"]},
    {"name": "Chicken Alfredo",  "price": 16, "tags": []},
]

INVENTORY = {   # ingredient -> units on hand
    "paneer_kg": 2, "salmon_kg": 3, "flour_kg": 8, "pasta_kg": 4,
    "chicken_kg": 2, "veg_kg": 6, "cheese_kg": 3,
}

RECIPES = {     # dish -> ingredients per single portion
    "Margherita Pizza":  {"flour_kg": 0.25, "cheese_kg": 0.15},
    "Paneer Tikka":      {"paneer_kg": 0.2,  "veg_kg": 0.1},
    "Vegan Buddha Bowl": {"veg_kg": 0.3,     "pasta_kg": 0.1},
    "Grilled Salmon":    {"salmon_kg": 0.25, "veg_kg": 0.15},
    "Chicken Alfredo":   {"chicken_kg": 0.25, "pasta_kg": 0.2, "cheese_kg": 0.1},
}

PURCHASE_ORDERS = []

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

def get_bookings(date):
    print(f"Bookings for date {date}: -> {BOOKINGS}...")

    print(f"All bookings {BOOKINGS}...")
    rows = [{"booking_id": bid, **b} for bid, b in BOOKINGS.items() if b["date"] == date]
    total = sum(r["party_size"] for r in rows)
    return {"date": date, "bookings": rows, "total_covers": total}

def get_inventory():
    return INVENTORY

def get_recipe(dish):
    r = RECIPES.get(dish)
    return {"dish": dish, "ingredients": r} if r else {"error": f"No recipe for {dish}."}

def create_purchase_order(items):   # items: {ingredient: qty}
    PURCHASE_ORDERS.append(items)
    return {"success": True, "ordered": items, "order_id": len(PURCHASE_ORDERS)}

def compute_prep_and_shortfall(covers_by_dish):
    """covers_by_dish: {dish_name: portions}. Does the exact math in Python."""
    needed = {}
    for dish, portions in covers_by_dish.items():
        for ing, per_portion in RECIPES.get(dish, {}).items():
            needed[ing] = round(needed.get(ing, 0) + per_portion * portions, 3)
    shortfall = {ing: round(qty - INVENTORY.get(ing, 0), 3)
                 for ing, qty in needed.items() if qty > INVENTORY.get(ing, 0)}
    return {"needed": needed, "on_hand": INVENTORY, "shortfall": shortfall}