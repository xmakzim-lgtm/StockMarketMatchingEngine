from venue import Venue
from graph import Graph

def make_venues():
    v1 = Venue("V1", fee_per_share=0.01, latency=5)
    v2 = Venue("V2", fee_per_share=0.02, latency=10)
    v3 = Venue("V3", fee_per_share=0.00, latency=20)
    return [v1, v2, v3]

def make_graph():
    g = Graph()
    for nid in ["BKR", "V1", "V2", "V3"]:
        g.add_node(nid)
    g.add_edge("BKR", "V1", 5)
    g.add_edge("BKR", "V2", 10)
    g.add_edge("BKR", "V3", 20)
    g.add_edge("V1", "V2", 6)
    g.add_edge("V2", "V3", 8)
    return g