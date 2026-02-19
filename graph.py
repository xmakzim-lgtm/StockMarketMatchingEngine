import heapq


class Graph:
    def __init__(self):
        self.adj = {}
    def add_node(self, node_id):
        if node_id not in self.adj:
            self.adj[node_id] = []
    def add_edge(self, src, dst, w):
        self.add_node(src)
        self.add_node(dst)
        self.adj[src].append((dst, w))
    def neighbors(self, node_id):
        return self.adj.get(node_id, [])
    def dijkstra(self, start):
        dist = {n: float("inf") for n in self.adj.keys()}
        if start not in self.adj:
            return dist
        dist[start] = 0.0
        pq = [(0.0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in self.neighbors(u):
                nd = d + w
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        return dist