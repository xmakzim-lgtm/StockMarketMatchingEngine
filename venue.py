from OrderBook import OrderBook
from MatchingEngine import MatchEngine

class Venue:
    def __init__(self, id, fee_per_share = 0.0, latency = 10):
        self.id = id
        self.fee_per_share = fee_per_share
        self.latency = latency
        self.book = OrderBook()
        self.engine = MatchEngine(self.book)

    def top_price(self, side):
        if side == "buy":
            ask = self.book.best_ask()
            return ask.price if ask else None
        else:
            bid = self.book.best_bid()
            return bid.price if bid else None

    def available_liquidity(self, side, max_levels = 5):
            if side == "buy":
                price_map = self.book.price_map_ask
                price_levels = sorted(price_map.keys())
            else:
                price_map = self.book.price_map_bid
                price_levels = sorted(price_map.keys(), reverse=True)
            liquidity = []
            count = min(max_levels, len(price_levels))
            for i in range(count):
                price = price_levels[i]
                pl = price_map[price]
                qty = pl.volume()
                liquidity.append((price, qty))
            return liquidity

    def submit_order(self, order):
        return self.engine.execute_trade(order)