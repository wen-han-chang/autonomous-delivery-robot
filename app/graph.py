from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import math
import heapq

@dataclass(frozen=True)
class Node2D:
    x: float
    y: float

class Graph:
    def __init__(self, nodes: Dict[str, Node2D], adj: Dict[str, List[Tuple[str, float]]]):
        self.nodes = nodes          # id -> (x,y)
        self.adj = adj              # id -> list[(neighbor, dist_cm)]

def euclid(a: Node2D, b: Node2D) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)

def build_graph(map_data) -> Graph:
    nodes = {n.id: Node2D(n.x, n.y) for n in map_data.nodes}
    adj: Dict[str, List[Tuple[str, float]]] = {nid: [] for nid in nodes.keys()}

    for e in map_data.edges:
        u, v = e.from_, e.to
        if u not in nodes or v not in nodes:
            raise ValueError(f"Edge refers to unknown node: {u}->{v}")

        dist = e.length if e.length is not None else euclid(nodes[u], nodes[v])
        adj[u].append((v, dist))
        if e.bidirectional:
            adj[v].append((u, dist))

    return Graph(nodes, adj)

def dijkstra(g: Graph, start: str, goal: str) -> Tuple[List[str], float]:
    if start not in g.adj or goal not in g.adj:
        raise ValueError("start/goal not in graph")

    dist: Dict[str, float] = {start: 0.0}
    prev: Dict[str, Optional[str]] = {start: None}
    pq: List[Tuple[float, str]] = [(0.0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if u == goal:
            break
        if d != dist.get(u, float("inf")):
            continue

        for v, w in g.adj[u]:
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if goal not in dist:
        raise ValueError("No path found")

    # reconstruct
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path, dist[goal]

def astar(g: Graph, start: str, goal: str) -> Tuple[List[str], float]:
    # optional later; 先放著也行
    def h(nid: str) -> float:
        return euclid(g.nodes[nid], g.nodes[goal])

    openpq: List[Tuple[float, str]] = [(h(start), start)]
    gscore: Dict[str, float] = {start: 0.0}
    prev: Dict[str, Optional[str]] = {start: None}

    while openpq:
        _, u = heapq.heappop(openpq)
        if u == goal:
            break
        for v, w in g.adj[u]:
            cand = gscore[u] + w
            if cand < gscore.get(v, float("inf")):
                gscore[v] = cand
                prev[v] = u
                heapq.heappush(openpq, (cand + h(v), v))

    if goal not in gscore:
        raise ValueError("No path found")

    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path, gscore[goal]
