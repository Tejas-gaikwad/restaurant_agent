TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_menu",
            "description": "Get the full restaurant menu with dish names, prices, and dietary tags.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check whether a table is free for a given date, time, and party size. Call this before booking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date for which to check availability, in YYYY-MM-DD format."
                    },
                    "time": {
                        "type": "string",
                        "description": "The time for which to check availability, in HH:MM format."
                    },
                    "party_size": {
                        "type": "integer",
                        "description": "The number of people in the party."
                    }
                },
                "required": ["date", "time", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_table",
            "description": "Book a table for a given date, time, and party size. Call this after checking availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date for which to book the table, in YYYY-MM-DD format."
                    },
                    "time": {
                        "type": "string",
                        "description": "The time for which to book the table, in HH:MM format."
                    },
                    "party_size": {"type": "integer", "description": "The number of people in the party."},
                    "name": {"type": "string", "description": "Name for the reservation"}
                },
                "required": ["date", "time", "party_size", "name"]
            }
        }
    },
    {
            "type": "function", "function": {
            "name": "modify_booking",
            "description": "Change an existing reservation's party size, date, or time. Use this when a guest wants to alter a booking they already made — do not create a new booking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "integer", "description": "The id returned when the booking was created"},
                    "party_size": {"type": "integer", "description": "New number of guests. Omit if unchanged."},
                    "date": {"type": "string", "description": "New date, YYYY-MM-DD. Omit if unchanged."},
                    "time": {"type": "string", "description": "New time, 24h HH:MM. Omit if unchanged."}
                },
            "required": ["booking_id"]
            }
        }
    },
    {"type": "function", "function": {
        "name": "cancel_booking",
        "description": "Cancel an existing reservation entirely.",
        "parameters": {
            "type": "object",
            "properties": {"booking_id": {"type": "integer"}},
            "required": ["booking_id"]
        }
    }},
    {"type": "function", "function": {
        "name": "find_booking",
        "description": "Find a booking by the guest's name.",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"]
        }
    }},
    {"type": "function", "function": {
    "name": "get_bookings",
    "description": "Get all reservations for a given date and the total number of covers (guests).",
    "parameters": {"type": "object",
        "properties": {"date": {"type": "string", "description": "Date, YYYY-MM-DD"}},
        "required": ["date"]}}},
    {"type": "function", "function": {
        "name": "get_inventory",
        "description": "Get current ingredient stock levels, in kg on hand.",
        "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_recipe",
        "description": "Get the ingredients needed per single portion of a given menu dish.",
        "parameters": {"type": "object",
            "properties": {"dish": {"type": "string", "description": "Exact dish name from the menu"}},
            "required": ["dish"]}}},
    {"type": "function", "function": {
        "name": "create_purchase_order",
        "description": "Place an order for ingredients that are short. Only call once, after computing the full shortfall.",
        "parameters": {"type": "object",
            "properties": {"items": {"type": "object",
                "description": "Map of ingredient name to quantity to order, e.g. {\"paneer_kg\": 3}"}},
            "required": ["items"]}}},
    {"type": "function", "function": {
        "name": "compute_prep_and_shortfall",
        "description": "Given how many portions of each dish are needed, compute exact ingredient requirements and the shortfall vs current stock. Use this for ALL quantity math — never calculate ingredient totals yourself.",
        "parameters": {"type": "object",
            "properties": {"covers_by_dish": {"type": "object",
                "description": "Map of dish name to number of portions, e.g. {\"Paneer Tikka\": 8}"}},
            "required": ["covers_by_dish"]}}},
]


RISK = {
    "get_menu": "low",              # read-only, no side effect
    "check_availability": "low",
    "find_booking": "low",
    "get_bookings": "low",
    "get_inventory": "low",
    "get_recipe": "low",
    "book_table": "medium",         # writes state, but reversible
    "modify_booking": "medium",
    "compute_prep_and_shortfall": "low",
    "cancel_booking": "high",       # irreversible-ish, destroys data
    "create_purchase_order": "high", # spends money, real-world effect
}