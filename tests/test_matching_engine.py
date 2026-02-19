# tests/test_matching_engine.py
import time
import pytest

from Order import Order
from OrderBook import OrderBook
from MatchingEngine import MatchEngine

def make_order(id, typ, side, price, qty, user="u"):
    return Order(id, typ, side, price, qty, time.time(), user, symbol="TST")

def test_exact_fill_removes_both():
    ob = OrderBook()
    me = MatchEngine(ob)

    sell = make_order("s1", "LIMIT", "sell", 10.0, 100)
    buy  = make_order("b1", "LIMIT", "buy", 10.0, 100)

    # put seller resting first
    me.execute_trade(sell)
    trades = me.execute_trade(buy)

    assert len(trades) == 1
    t = trades[0]
    assert t["quantity"] == 100
    # s1 and b1 should be removed from id_map
    assert "s1" not in ob.id_map
    assert "b1" not in ob.id_map
    # book should have no best bid/ask
    assert ob.best_bid() is None
    assert ob.best_ask() is None

def test_partial_fill_remaining():
    ob = OrderBook()
    me = MatchEngine(ob)

    sell = make_order("s2", "LIMIT", "sell", 12.0, 100)
    buy  = make_order("b2", "LIMIT", "buy", 12.0, 150)

    me.execute_trade(sell)
    trades = me.execute_trade(buy)

    assert len(trades) == 1
    t = trades[0]
    assert t["quantity"] == 100
    # buy should remain with 50
    assert "b2" in ob.id_map
    remaining = ob.id_map["b2"].quantity
    assert remaining == 50

def test_multi_level_fill():
    ob = OrderBook()
    me = MatchEngine(ob)

    # two asks at different prices
    a1 = make_order("a1","LIMIT","sell", 10.0, 100)
    a2 = make_order("a2","LIMIT","sell", 11.0, 200)
    me.execute_trade(a1)
    me.execute_trade(a2)

    # market buy that consumes both price levels partially
    mb = make_order("mb1","MARKET","buy", None, 250)
    trades = me.execute_trade(mb)

    assert len(trades) == 2
    assert trades[0]["quantity"] == 100
    assert trades[1]["quantity"] == 150

    # a1 should be removed (fully filled). a2 should remain with 50 shares.
    assert "a1" not in ob.id_map
    assert "a2" in ob.id_map
    assert ob.id_map["a2"].quantity == 50

def test_cancel_middle_order():
    ob = OrderBook()
    me = MatchEngine(ob)

    # three buys at same price
    o1 = make_order("o1","LIMIT","buy", 9.0, 50)
    o2 = make_order("o2","LIMIT","buy", 9.0, 60)
    o3 = make_order("o3","LIMIT","buy", 9.0, 70)
    me.execute_trade(o1)
    me.execute_trade(o2)
    me.execute_trade(o3)

    # cancel middle
    assert ob.cancel_order("o2") is True
    # ensure o2 removed and others remain
    assert "o2" not in ob.id_map
    assert "o1" in ob.id_map
    assert "o3" in ob.id_map
    # volumes reflect removal
    pl = ob.price_map_bid.get(9.0)
    total_volume = pl.volume() if pl else 0
    assert total_volume == (50 + 70)

def test_no_self_match_when_executing_incoming():
    ob = OrderBook()
    me = MatchEngine(ob)
    # incoming order should not self-match: we send an order that would match itself only if pre-inserted incorrectly
    o = make_order("x1","LIMIT","buy", 5.0, 10)
    trades = me.execute_trade(o)
    # no trades since book empty
    assert trades == []
    # now add opposing resting sell order
    s = make_order("sX","LIMIT","sell", 5.0, 10)
    trades_s = me.execute_trade(s)
    # the trade should have executed when the sell came in (matching against the resting buy)
    assert len(trades_s) == 1

    # alternatively, ensure a new buy order will match against the resting sell:
    # insert a fresh sell and a fresh buy and verify match happens on incoming buy call
    ob2 = OrderBook()
    me2 = MatchEngine(ob2)
    # make fresh orders
    sell = make_order("sY","LIMIT","sell", 7.0, 10)
    me2.execute_trade(sell)
    buy = make_order("bY","LIMIT","buy", 7.0, 10)
    trades2 = me2.execute_trade(buy)
    assert len(trades2) == 1