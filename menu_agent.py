# menu_agent.py
from booking_store import get_menu

class MenuAgent:
    def handle(self, user_message):
        lines = [f"- {i['name']} (${i['price']}) {', '.join(i['tags'])}" for i in get_menu()]
        return "Here's our menu:\n" + "\n".join(lines)