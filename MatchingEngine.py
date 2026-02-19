from Order import Order
from OrderBook import OrderBook
from PriceLevel import PriceLevel
import time

class MatchEngine:
    def __init__(self, orderbook):
        self.ob = orderbook
        self.trade_history = []
    def trade_record(self, buy, sell, price, qty):
        return {
            "buy_order_id": buy.id,
            "sell_order_id": sell.id,
            "symbol": buy.symbol or sell.symbol,
            "price": price,
            "quantity": qty,
            "timestamp": time.time(),
        }
    def match_trade(self, incoming):
        trades = []
        incoming.side = incoming.side.lower()
        incoming.type = incoming.type.upper()
        while incoming.quantity > 0:
            resting = self.top_resting_order(incoming.side)
            if resting is None:
                break
            if not self.price_crosses(incoming, resting):
                break
            trade = self.match_once(incoming, resting)
            trades.append(trade)
            self.trade_history.append(trade)
        self.finalize(incoming)
        return trades

    def top_resting_order(self, incoming_side):
        if incoming_side == "buy":
            return self.ob.best_ask()
        else:
            return self.ob.best_bid()

    def price_crosses(self, incoming, resting):
        if incoming.type == "MARKET" or incoming.price is None:
            return True
        if incoming.side == "buy":
            return incoming.price >= resting.price
        else:
            return incoming.price <= resting.price

    def match_once(self, incoming, resting):
        trade_qty = min(incoming.quantity, resting.quantity)
        trade_price = resting.price
        incoming.quantity -= trade_qty
        incoming.filled += trade_qty
        resting.quantity -= trade_qty
        resting.filled += trade_qty

        if incoming.side == "buy":
            buy_order = incoming
            ask_order = resting
        else:
            buy_order = resting
            ask_order = incoming
        trade = self.trade_record(buy_order, ask_order, trade_price, trade_qty)
        if resting.quantity == 0:
            self.handling(resting)
            resting.status = "FILLED"
        else:
            resting.status = "PARTIAL"

        return trade

    def handling(self, resting):
        if resting.side.lower() in ("sell", "ask"):
            pl = self.ob.price_map_ask.get(resting.price)
            if pl:
                try:
                    pl.price_Deque.popleft()
                except IndexError:
                    pass
                if pl.is_empty():
                    del self.ob.price_map_ask[resting.price]
        else:
            pl = self.ob.price_map_bid.get(resting.price)
            if pl:
                try:
                    pl.price_Deque.popleft()
                except IndexError:
                    pass
                if pl.is_empty():
                    del self.ob.price_map_bid[resting.price]
        if resting.id in self.ob.id_map:
            del self.ob.id_map[resting.id]

    def finalize(self, incoming):
        if incoming.quantity == 0:
            incoming.status = "FILLED"
        elif incoming.filled > 0:
            incoming.status = "PARTIAL"
        else:
            incoming.status = "OPEN"

    def execute_trade(self, order):
        trades = self.match_trade(order)
        if order.quantity > 0 and order.type == "LIMIT":
            self.ob.id_map[order.id] = order
            self.ob.add_order(order)
        return trades

    def printTrade(self):
        for order in self.trade_history:
            print(order)

        


