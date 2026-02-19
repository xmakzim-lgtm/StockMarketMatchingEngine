import json
import time
from Order import Order
from router import route_execute
from venue_config import make_venues, make_graph

def prep_initial_orders(venues):
    """
    Optional: populate some initial orders on each venue.
    """
    import time
    venues[0].submit_order(Order("s_v1_1","LIMIT","sell", 10.0, 100, time.time(), "u1", "TST"))
    venues[1].submit_order(Order("s_v2_1","LIMIT","sell", 10.5, 200, time.time(), "u2", "TST"))
    venues[2].submit_order(Order("s_v3_1","LIMIT","sell", 11.0, 500, time.time(), "u3", "TST"))

def process_order_stream(path, venues, graph, origin="BKR", speed=1.0):
    """
    Reads orders from JSONL file and routes them across venues using your graph.
    """
    with open(path, "r") as f:
        for line in f:
            rec = json.loads(line)
            action = rec.get("action")
            if action == "submit":
                o = rec["order"]
                order = Order(
                    o["id"],
                    o.get("type","LIMIT"),
                    o["side"],
                    o.get("price", None),
                    o["quantity"],
                    o.get("timestamp", time.time()),
                    o.get("user_id","demo"),
                    symbol=o.get("symbol")
                )
                trades = route_execute(order, venues, graph, origin)
                if trades:
                    print("Trades:", trades)
                else:
                    print(f"Inserted/queued order {order.id} {order.side} {order.quantity}@{order.price}")
            elif action == "cancel":
                oid = rec["order_id"]
                cancelled = False
                # Try cancelling on all venues
                for v in venues:
                    if v.book.cancel_order(oid):
                        cancelled = True
                print(f"Cancel {oid} -> {cancelled}")
            time.sleep(0.2 / speed)

def print_top_of_book(venues):
    print("\nTop-of-book per venue:")
    for v in venues:
        bid = v.book.best_bid()
        ask = v.book.best_ask()
        print(f"{v.id}: Best bid: {bid.price if bid else None}, Best ask: {ask.price if ask else None}")

if __name__ == "__main__":
    venues = make_venues()
    graph = make_graph()
    prep_initial_orders(venues)  # optional

    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "demo_stream.jsonl"
    process_order_stream(path, venues, graph, origin="BKR")

    print_top_of_book(venues)