
from booking_flow import BookingFlow
from llm_agent import Agent
from menu_agent import MenuAgent
from router import route_message, Route


class Supervisor:
    def __init__(self):
        self.booking = BookingFlow()
        self.kitchen = Agent()
        self.menu = MenuAgent()
        self.session = {}   

    def handle(self, user_message):
        print(f"user_message: {user_message}")
        decision = route_message(user_message)
        print(f"  [routes → {[r.value for r in decision.routes]}: {decision.reason}]")

        responses = []
        for route in decision.routes:                       # actually loop the routes
            if route == Route.booking:
                responses.append(self.booking.handle(user_message, self.session))
            elif route == Route.menu:
                responses.append(self.menu.handle(user_message))
            elif route == Route.kitchen:
                responses.append(self.kitchen.handle(user_message))
            # 'other' falls through
        if not responses:
            return "I can help with reservations, the menu, or kitchen prep. What do you need?"
        return "\n\n".join(responses)         