from flask import Flask, request
from heapq import heappush, heappop
from math import isfinite
from helpers import rest_response, rest_error

app = Flask(__name__)

def validate_graph(graph: dict):
    """
    Validates that graph is a dict[str, dict[str, number]] with non-negative weights.
    Returns (ok: bool, message: str).
    """
    if not isinstance(graph, dict):
        return False, "graph must be an object mapping node -> neighbor map"
    for node, nbrs in graph.items():
        if not isinstance(node, str):
            return False, "all node ids must be strings"
        if not isinstance(nbrs, dict):
            return False, f"neighbors for node '{node}' must be an object"
        for nbr, w in nbrs.items():
            if not isinstance(nbr, str):
                return False, f"neighbor ids for node '{node}' must be strings"
            if not (isinstance(w, int) or isinstance(w, float)):
                return False, f"edge weight {node}->{nbr} must be a number"
            if w < 0:
                return False, f"edge weight {node}->{nbr} must be non-negative"
    return True, "ok"

def dijkstra(graph: dict, start: str, end: str):
    """
    Dijkstra on a directed adjacency list: {node: {neighbor: weight}}.
    Returns (path: list[str], total_cost: float) or (None, None) if unreachable.
    """
    dist = {n: float("inf") for n in graph}
    prev = {n: None for n in graph}
    dist[start] = 0.0

    pq = []
    heappush(pq, (0.0, start))

    while pq:
        d, u = heappop(pq)
        if d > dist[u]:
            continue
        if u == end:
            break
        for v, w in graph.get(u, {}).items():
            nd = d + float(w)
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heappush(pq, (nd, v))

    if not isfinite(dist[end]):
        return None, None

    # Reconstruct path
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    total = dist[end]
    # Make it an int if it's mathematically an integer to avoid a trailing .0
    if float(total).is_integer():
        total = int(total)

    return path, total

@app.post("/shortest-path")
def shortest_path():
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            return rest_error("Expected JSON body.")

        graph = payload.get("graph")
        start = payload.get("start")
        end = payload.get("end")

        # Basic presence checks
        if graph is None or start is None or end is None:
            return rest_error("Missing required fields: 'graph', 'start', and 'end'.")

        # Validate graph shape
        ok, msg = validate_graph(graph)
        if not ok:
            return rest_error(msg)

        # Node existence
        if start not in graph:
            return rest_error(f"Start node '{start}' not found in graph.")
        if end not in graph:
            return rest_error(f"End node '{end}' not found in graph.")

        # Run Dijkstra
        path, cost = dijkstra(graph, start, end)
        if path is None:
            return rest_error(f"No path found from '{start}' to '{end}'.")

        return rest_response({
            "path": path,
            "total_cost": cost
        })

    except Exception as e:
        return rest_error(f"Internal error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
