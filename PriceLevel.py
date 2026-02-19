from collections import deque

class PriceLevel:
    def __init__(self, price_Deque, price):
        self.price_Deque = price_Deque if price_Deque is not None else deque()
        self.price = price
    def add_order(self, order):
        self.price_Deque.append(order)
    def remove_order(self, order_id):
        for o in list(self.price_Deque):
            if o.id == order_id:
                self.price_Deque.remove(o)
                return True
        return False
    def peek_front(self):
        if not self.price_Deque:
            return None
        return self.price_Deque[0]
    def is_empty(self):
        if len(self.price_Deque) == 0:
            return True
        return False
    def volume(self):
        qty = 0
        for orders in self.price_Deque:
            qty += orders.quantity
        return qty