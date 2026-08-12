from booking_flow import BookingFlow
from booking_store import book_table
from datetime import date
from llm_agent import Agent, make_plan, execute_plan
from supervisor import Supervisor
from datetime import date
from llm_agent import guarded_dispatch

if __name__ == "__main__":

    # flow = BookingFlow()
    # while True:
    #     user = input("> ")
    #     if user in ("quit", "exit"):
    #         break
    #     print(flow.handle(user))

    # print(flow.handle("book a table for 6 tomorrow at 10pm, name is akash"))
    # print(flow.handle("change it to 2 people"))            # → still need: name
    # print(flow.handle("akash"))                           # merges name; still complete? modify needs name → done
    # print(flow.handle("book a table tomorrow at 10pm"))    # → still need: name, party_size
    # print(flow.handle("aditya, 4 people"))                 # → all 4 slots filled → books immediately


    # today = date.today().isoformat()
    # book_table(today, "20:00", 8, "Akash")
    # book_table(today, "20:00", 6, "Priya")

    # agent = Agent()
    # print(agent.chat(
    #     f"We have bookings for tonight ({today}). Assume each guest orders one main, "
    #     f"split evenly across the menu. Work out what to prep and order what we're short on."
    # ))

    # plan = make_plan(f"Plan tonight's prep and ordering for {today}. Assume one main per guest, even split.")
    # print(f"\nPLAN ({len(plan.steps)} steps):")
    # for s in plan.steps:
    #     print(f"  - {s.tool}: {s.reason}")
    # execute_plan(plan)
    supervisor = Supervisor()
    # print(supervisor.handle("book a table for 4 tomorrow at 8pm, name Tejas"))
    # print(supervisor.handle("what vegan dishes do you have?"))
    # print(supervisor.handle("plan tonight's prep and ordering for today"))
    # print(supervisor.handle("hey there"))
    # print("Result: \n", supervisor.handle("book a table for 4 tomorrow at 8pm, name Tejas, and tell me the vegan options"))
    
    # print(supervisor.handle("change it to 6 people"))
    # print(supervisor.handle("change it to 6 people"))

     # seed a booking for TODAY so the prep goal finds real covers
    book_table(date.today().isoformat(), "20:00", 10, "GuardTest")

    supervisor = Supervisor()
    # print(supervisor.handle("plan tonight's prep and ordering for today"))
    print(guarded_dispatch("create_purchase_order", {"items": {"paneer_kg": 5, "chicken_kg": 3}}))
    while True:
        user = input("> ")
        if user in ("quit", "exit"):
            break
        print(supervisor.handle(user))

