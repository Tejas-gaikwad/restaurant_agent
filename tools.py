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
    {"type": "function", "function": {
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
    }},
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
        }}
]
