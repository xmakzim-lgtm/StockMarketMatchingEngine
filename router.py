from Order import Order
from graph import Graph
from venue import Venue
from typing import List

PATH = 0.0001
LATENCY = 0.0001


def score_venue(venue, side, path_cost):
    top = venue.top_price(side)
    if top is None:
        return float("inf")
    latency_penalty = LATENCY * venue.latency
    fee = venue.fee_per_share
    return top + fee + latency_penalty + (path_cost * PATH)

def route_execute(order, venues, graph, origin):
    venue_map = {v.id: v for v in venues}
    dist = graph.dijkstra(origin)
    side = order.side.lower()
    scored = []
    for v in venues:
        path_cost = dist.get(v.id, float("inf"))
        score = score_venue(v, side, path_cost)
        scored.append((score, path_cost, v))
    scored.sort(key=lambda x:x[00])
    qty_left = order.quantity
    total_trades = []
    for score, path_cost, v in scored:
        if qty_left <= 0: break
        if path_cost == float("inf"): continue
        levels = v.available_liquidity(side, max_levels=5)
        avl = sum(q for p,q in levels)
        take = min(avl, qty_left)
        if take <= 0: continue
        slice_price = None if order.type == "MARKET" else (levels[0][0] if levels else None)
        o = Order(f"{order.id}-{v.id}", order.type, order.side, slice_price, take, order.timestamp, order.user_id, order.symbol)
        trades = v.submit_order(o)
        total_trades.extend(trades)
        filled = sum(t["quantity"] for t in trades)
        qty_left -= filled
    return total_trades