# dijkstra-flask
A Flask service implementation of Dijkstra's algorithm.

## Request

POST /shortest-path

```
{
  "graph": {
    "A": {"B": 5, "C": 2},
    "B": {"A": 5, "C": 1, "D": 3},
    "C": {"A": 2, "B": 1, "D": 7},
    "D": {"B": 3, "C": 7}
  },
  "start": "A",
  "end": "D"
}
```

## Response

```
{
  "status": "OK",
  "result": {
    "path": ["A", "C", "B", "D"],
    "total_cost": 6
  }
}
```
