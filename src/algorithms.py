from __future__ import annotations

import heapq
from collections import deque
from typing import Any


def sorting_trace(name: str, values: list[int]) -> list[dict[str, Any]]:
    a = values.copy()
    steps: list[dict[str, Any]] = [{"array": a.copy(), "active": [], "sorted": [], "message": "Initial array"}]
    n = len(a)
    if name == "Bubble Sort":
        for end in range(n - 1, 0, -1):
            swapped = False
            for j in range(end):
                steps.append({"array": a.copy(), "active": [j, j + 1], "sorted": list(range(end + 1, n)), "message": f"Compare {a[j]} and {a[j + 1]}"})
                if a[j] > a[j + 1]:
                    a[j], a[j + 1] = a[j + 1], a[j]
                    swapped = True
                    steps.append({"array": a.copy(), "active": [j, j + 1], "sorted": list(range(end + 1, n)), "message": "Swap adjacent elements"})
            if not swapped:
                break
        steps.append({"array": a.copy(), "active": [], "sorted": list(range(n)), "message": "Array is sorted"})
    elif name == "Selection Sort":
        for i in range(n):
            m = i
            for j in range(i + 1, n):
                steps.append({"array": a.copy(), "active": [m, j], "sorted": list(range(i)), "message": f"Compare current minimum {a[m]} with {a[j]}"})
                if a[j] < a[m]:
                    m = j
            if m != i:
                a[i], a[m] = a[m], a[i]
                steps.append({"array": a.copy(), "active": [i, m], "sorted": list(range(i)), "message": f"Place minimum value {a[i]} at position {i}"})
        steps.append({"array": a.copy(), "active": [], "sorted": list(range(n)), "message": "Array is sorted"})
    elif name == "Insertion Sort":
        for i in range(1, n):
            key = a[i]
            j = i - 1
            while j >= 0 and a[j] > key:
                steps.append({"array": a.copy(), "active": [j, j + 1], "sorted": list(range(i)), "message": f"Shift {a[j]} one position right"})
                a[j + 1] = a[j]
                j -= 1
            a[j + 1] = key
            steps.append({"array": a.copy(), "active": [j + 1], "sorted": list(range(i + 1)), "message": f"Insert {key} into its sorted position"})
        steps.append({"array": a.copy(), "active": [], "sorted": list(range(n)), "message": "Array is sorted"})
    elif name == "Merge Sort":
        def merge_sort(lo: int, hi: int) -> None:
            if hi - lo <= 1:
                return
            mid = (lo + hi) // 2
            steps.append({"array": a.copy(), "active": list(range(lo, hi)), "sorted": [], "message": f"Divide range [{lo}, {hi}) at midpoint {mid}"})
            merge_sort(lo, mid)
            merge_sort(mid, hi)
            left, right = a[lo:mid], a[mid:hi]
            i = j = 0
            merged = []
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    merged.append(left[i]); i += 1
                else:
                    merged.append(right[j]); j += 1
            merged.extend(left[i:]); merged.extend(right[j:])
            a[lo:hi] = merged
            steps.append({"array": a.copy(), "active": list(range(lo, hi)), "sorted": [], "message": f"Merge the two sorted halves into [{lo}, {hi})"})
        merge_sort(0, n)
        steps.append({"array": a.copy(), "active": [], "sorted": list(range(n)), "message": "Array is sorted"})
    elif name == "Quick Sort":
        def quick_sort(lo: int, hi: int) -> None:
            if lo >= hi:
                return
            pivot = a[hi]
            i = lo
            steps.append({"array": a.copy(), "active": [hi], "sorted": [], "message": f"Choose {pivot} as the pivot"})
            for j in range(lo, hi):
                steps.append({"array": a.copy(), "active": [j, hi], "sorted": [], "message": f"Compare {a[j]} with pivot {pivot}"})
                if a[j] <= pivot:
                    a[i], a[j] = a[j], a[i]
                    steps.append({"array": a.copy(), "active": [i, j], "sorted": [], "message": "Move value into the lower partition"})
                    i += 1
            a[i], a[hi] = a[hi], a[i]
            steps.append({"array": a.copy(), "active": [i], "sorted": [], "message": f"Place pivot {pivot} in its final position"})
            quick_sort(lo, i - 1)
            quick_sort(i + 1, hi)
        quick_sort(0, n - 1)
        steps.append({"array": a.copy(), "active": [], "sorted": list(range(n)), "message": "Array is sorted"})
    else:
        raise ValueError(f"Unknown sorting algorithm: {name}")
    return steps


def array_search_trace(name: str, values: list[int], target: int) -> list[dict[str, Any]]:
    steps = [{"array": values.copy(), "active": [], "found": [], "message": f"Search for {target}"}]
    if name == "Linear Search":
        for i, value in enumerate(values):
            steps.append({"array": values.copy(), "active": [i], "found": [], "message": f"Check index {i}: {value}"})
            if value == target:
                steps.append({"array": values.copy(), "active": [], "found": [i], "message": f"Found {target} at index {i}"})
                return steps
        steps.append({"array": values.copy(), "active": [], "found": [], "message": f"{target} is not in the array"})
    elif name == "Binary Search":
        a = sorted(values)
        lo, hi = 0, len(a) - 1
        steps = [{"array": a.copy(), "active": list(range(len(a))), "found": [], "message": "Binary Search requires sorted input; values are shown in sorted order"}]
        while lo <= hi:
            mid = (lo + hi) // 2
            steps.append({"array": a.copy(), "active": [mid], "found": [], "message": f"Check midpoint index {mid}: {a[mid]}"})
            if a[mid] == target:
                steps.append({"array": a.copy(), "active": [], "found": [mid], "message": f"Found {target} at index {mid}"})
                return steps
            if a[mid] < target:
                lo = mid + 1
                steps.append({"array": a.copy(), "active": list(range(lo, hi + 1)), "found": [], "message": "Discard the left half"})
            else:
                hi = mid - 1
                steps.append({"array": a.copy(), "active": list(range(lo, hi + 1)), "found": [], "message": "Discard the right half"})
        steps.append({"array": a.copy(), "active": [], "found": [], "message": f"{target} is not in the array"})
    else:
        raise ValueError(f"Unknown search algorithm: {name}")
    return steps


def graph_trace(name: str, graph: dict[str, dict[str, float]], start: str, goal: str) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    visited: set[str] = set()
    parent: dict[str, str] = {}
    distance = {node: float("inf") for node in graph}
    distance[start] = 0
    frontier: list[tuple[float, str]] = [(0, start)]
    queue = deque([start])
    stack = [start]
    g_score = {node: float("inf") for node in graph}
    g_score[start] = 0
    f_score = {node: float("inf") for node in graph}
    f_score[start] = _heuristic(start, goal)
    astar_frontier = [(f_score[start], start)]

    def record(current: str, message: str, path: list[str] | None = None) -> None:
        steps.append({"current": current, "visited": sorted(visited), "frontier": [x[1] for x in (frontier if name == "Dijkstra's" else astar_frontier)] if name in {"Dijkstra's", "A* Search"} else (list(queue) if name == "Breadth-First Search" else stack.copy()), "parent": parent.copy(), "distances": distance.copy() if name == "Dijkstra's" else g_score.copy(), "message": message, "path": path or []})

    if name == "Breadth-First Search":
        while queue:
            u = queue.popleft()
            if u in visited:
                continue
            visited.add(u); record(u, f"Visit node {u}")
            if u == goal:
                break
            for v in graph[u]:
                if v not in visited and v not in parent and v != start:
                    parent[v] = u; queue.append(v); record(u, f"Discover {v} from {u}")
    elif name == "Depth-First Search":
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u); record(u, f"Visit node {u}")
            if u == goal:
                break
            for v in reversed(list(graph[u])):
                if v not in visited and v not in parent and v != start:
                    parent[v] = u; stack.append(v); record(u, f"Add {v} to the DFS stack")
    elif name == "Dijkstra's":
        while frontier:
            d, u = heapq.heappop(frontier)
            if u in visited:
                continue
            visited.add(u); record(u, f"Finalize {u} with distance {d:g}")
            if u == goal:
                break
            for v, w in graph[u].items():
                nd = d + w
                if nd < distance[v]:
                    distance[v] = nd; parent[v] = u; heapq.heappush(frontier, (nd, v)); record(u, f"Relax edge {u} → {v}; new distance {nd:g}")
    elif name == "A* Search":
        while astar_frontier:
            _, u = heapq.heappop(astar_frontier)
            if u in visited:
                continue
            visited.add(u); record(u, f"Expand {u}; f = g + h = {g_score[u]:g} + {_heuristic(u, goal):g}")
            if u == goal:
                break
            for v, w in graph[u].items():
                tentative = g_score[u] + w
                if tentative < g_score[v]:
                    parent[v] = u; g_score[v] = tentative; f_score[v] = tentative + _heuristic(v, goal)
                    heapq.heappush(astar_frontier, (f_score[v], v)); record(u, f"Update {v}: g = {tentative:g}, f = {f_score[v]:g}")
    else:
        raise ValueError(f"Unknown graph algorithm: {name}")

    path = _reconstruct(parent, start, goal) if goal == start or goal in parent else []
    if steps:
        steps.append({**steps[-1], "current": goal, "message": f"Path found: {' → '.join(path)}" if path else "No path to the selected goal", "path": path})
    return steps


def _heuristic(node: str, goal: str) -> float:
    coords = {"A": (0, 2), "B": (2, 3), "C": (2, 1), "D": (4, 3), "E": (4, 1), "F": (6, 2), "G": (2, 5), "H": (4, 5)}
    x1, y1 = coords.get(node, (0, 0)); x2, y2 = coords.get(goal, (0, 0))
    return 0.5 * (((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)


def _reconstruct(parent: dict[str, str], start: str, goal: str) -> list[str]:
    path = [goal]
    while path[-1] != start and path[-1] in parent:
        path.append(parent[path[-1]])
    return list(reversed(path)) if path[-1] == start else []


SAMPLE_GRAPH = {
    "A": {"B": 2, "C": 3, "G": 2},
    "B": {"A": 2, "C": 2, "D": 3, "H": 3},
    "C": {"A": 3, "B": 2, "E": 2},
    "D": {"B": 3, "E": 2, "F": 3, "H": 2},
    "E": {"C": 2, "D": 2, "F": 2},
    "F": {"D": 3, "E": 2},
    "G": {"A": 2, "H": 2},
    "H": {"G": 2, "B": 3, "D": 2},
}
