import heapq
from collections import deque
from PriceLevel import PriceLevel
class OrderBook:
    def __init__(self):
        self.bid_heap = []
        self.ask_heap = []
        self.price_map_bid = {}
        self.price_map_ask = {}
        self.id_map = {}
    def add_bid(self, order):
        price = order.price
        pl = self.price_map_bid.get(price)
        self.id_map[order.id] = order
        if pl is None:
            pl = PriceLevel(deque([order]), price)
            self.price_map_bid[price] = pl
            heapq.heappush(self.bid_heap, -price)
        else:
            pl.add_order(order)
    def top_bid_price(self):
        while self.bid_heap:
            price = -self.bid_heap[0]
            pl = self.price_map_bid.get(price)
            if pl is not None and not pl.is_empty():
                return price
            heapq.heappop(self.bid_heap)
        return None
    def best_bid(self):
        price = self.top_bid_price()
        if price is None:
            return None
        return self.price_map_bid[price].peek_front()

    def add_ask(self, order):
        price = order.price
        pl = self.price_map_ask.get(price)
        self.id_map[order.id] = order
        if pl is None:
            pl = PriceLevel(deque([order]), price)
            self.price_map_ask[price] = pl
            heapq.heappush(self.ask_heap, price)
        else:
            pl.add_order(order)
    def bottom_ask_price(self):
        while self.ask_heap:
            price = self.ask_heap[0]
            pl = self.price_map_ask.get(price)
            if pl is not None and not pl.is_empty():
                return price
            heapq.heappop(self.ask_heap)
        return None
    def best_ask(self):
        price = self.bottom_ask_price()
        if price is None:
            return None
        pl = self.price_map_ask.get(price)
        if pl is None:
            return None
        return pl.peek_front()
    def add_order(self, order):
        if order.side == "buy":
            self.add_bid(order)
        elif order.side == "sell" or order.side == "ask":
            self.add_ask(order)
        else:
            raise ValueError("Unknown side")
    def cancel_order(self, order_id):
        order = self.id_map.get(order_id)
        if order is None:
            return False
        if order.status in ("FILLED", "CANCELLED"):
            self.id_map.pop(order_id)
            return False
        price = order.price
        side = order.side or "".lower()
        if side == "buy":
            pl = self.price_map_bid.get(price)
        else:
            pl = self.price_map_ask.get(price)
        if pl is None:
            order.status = "CANCELED"
            self.id_map.pop(order.id)
            return True
        removed = False
        for o in list(pl.price_Deque):
            if o.id == order_id:
                try:
                    pl.price_Deque.remove(o)
                    removed = True
                except ValueError:
                    removed = False
                break
        if removed:
            order.status = "CANCELED"
            self.id_map.pop(order_id)
            if pl.is_empty():
                if side == "buy":
                    del self.price_map_bid[price]
                else:
                    del self.price_map_ask[price]
            return True
        order.status = "CANCELED"
        self.id_map.pop(order_id)
        return False