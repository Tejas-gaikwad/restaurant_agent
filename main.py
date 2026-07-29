from booking_flow import BookingFlow

if __name__ == "__main__":

    flow = BookingFlow()
    # while True:
    #     user = input("> ")
    #     if user in ("quit", "exit"):
    #         break
    #     print(flow.handle(user))

    print(flow.handle("book a table for 6 tomorrow at 10pm, name is akash"))
    print(flow.handle("change it to 2 people"))            # → still need: name
    print(flow.handle("akash"))                           # merges name; still complete? modify needs name → done
    # print(flow.handle("book a table tomorrow at 10pm"))    # → still need: name, party_size
    # print(flow.handle("aditya, 4 people"))                 # → all 4 slots filled → books immediately
