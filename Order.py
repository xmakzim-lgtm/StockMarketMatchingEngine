
class Order:
    def __init__(self, id, type, side, price, quantity, timestamp, user_id, symbol=None):
        self.id = id
        self.type = type
        self.side = side
        self.price = price
        self.quantity = quantity
        self.orig_quantity = quantity
        self.filled = 0
        self.status = "OPEN"
        self.timestamp = timestamp
        self.user_id = user_id
        self.symbol = symbol

    def orderPrint(self):
        return f"{self.id}, {self.type}, {self.side}, {self.price}, {self.quantity}, {self.timestamp}, {self.user_id}"