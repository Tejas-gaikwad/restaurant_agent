from extract_intent import extract_intent
from booking_store import check_availability, book_table, find_booking, modify_booking, cancel_booking, get_menu

REQUIRED = {"book": ["name", "date", "time", "party_size"], "modify": ["name"], "cancel": ["name"]}




class BookingFlow:
    def __init__(self):
        self.slots = {}          # accumulated across turns, in Python — not in model context
        self.intent = None

    def _reset(self):
        self.slots = {}
        self.intent = None

    def handle(self, user_message, session=None):
        print("Handling...")
        parsed = extract_intent(user_message, self.slots)
        print( parsed)
        new_intent = parsed.intent.value
        if self.intent is None or self.intent not in REQUIRED:
        # no active multi-turn flow → take the fresh classification
            self.intent = new_intent
        elif new_intent in REQUIRED and new_intent != self.intent:
        # user clearly started a *different* booking action → restart cleanly
            self._reset()
            self.intent = new_intent

        # merge any newly-provided fields into our slot state
        for field in ("name", "date", "time", "party_size"):
            val = getattr(parsed, field)
            if val is not None:
                self.slots[field] = val

        if self.intent in ("modify", "cancel") and "name" not in self.slots:
            if session and "last_name" in session:
                self.slots["name"] = session["last_name"] 

        missing = [f for f in REQUIRED.get(self.intent, []) if f not in self.slots]

        if missing:
            return f"To {self.intent} your table I still need: {', '.join(missing)}."

        # all required slots present → Python fires the action, deterministically, exactly once
        if self.intent == "book":
            avail = check_availability(self.slots["date"], self.slots["time"], self.slots["party_size"])
            if not avail["available"]:
                return avail.get("reason", "That slot isn't available.")
            result = book_table(**{k: self.slots[k] for k in REQUIRED["book"]})
            if session is not None:
                session["last_booking_id"] = result["booking_id"]
                session["last_name"] = self.slots["name"]
            self.slots = {}                       # reset for next booking
            # print("Booking result:", result)
            return result["message"]

        if self.intent == "modify":
            found = find_booking(self.slots["name"])
            if not found["found"]:
                self.slots = {}
                return found["message"]
            booking_id = found["bookings"][0]["booking_id"]
            result = modify_booking(
                booking_id,
                party_size=self.slots.get("party_size"),
                date=self.slots.get("date"),
                time=self.slots.get("time"),
            )
            self.slots = {}
            if not result["success"]:
                return result.get("reason", "Couldn't modify that booking.")
            return f"Updated your reservation: {result['booking']}"

        if self.intent == "cancel":
            found = find_booking(self.slots["name"])
            if not found["found"]:
                self.slots = {}
                return found["message"]
            booking_id = found["bookings"][0]["booking_id"]
            result = cancel_booking(booking_id)
            self.slots = {}
            return "Your reservation has been cancelled." if result["success"] else "Couldn't cancel that booking."

        if self.intent == "menu":
            lines = [f"- {item['name']} (${item['price']})" for item in get_menu()]
            return "Here's our menu:\n" + "\n".join(lines)

        return "I can help you book, modify, or cancel a table, or show you the menu — what would you like?"
