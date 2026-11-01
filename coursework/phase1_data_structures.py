"""TrackSide Live: independent Phase 1 algorithms module.

Synthetic academic data only. This module does not connect to the Flask website.
"""
from __future__ import annotations

from dataclasses import dataclass
import heapq
from typing import Optional


@dataclass(frozen=True)
class Driver:
    driver_id: str
    name: str
    car_number: str


class DriverIndex:
    """Hash-table-backed lookup: expected O(1) insert and search."""
    def __init__(self) -> None:
        self._drivers: dict[str, Driver] = {}

    def add(self, driver: Driver) -> None:
        self._drivers[driver.driver_id] = driver

    def find(self, driver_id: str) -> Optional[Driver]:
        return self._drivers.get(driver_id)

    def __len__(self) -> int:
        return len(self._drivers)


class FastestLaps:
    """Min-heap: O(log n) add, O(1) fastest peek, O(log n) pop."""
    def __init__(self) -> None:
        self._heap: list[tuple[float, str]] = []

    def add(self, driver_id: str, seconds: float) -> None:
        if seconds <= 0:
            raise ValueError("Lap time must be positive")
        heapq.heappush(self._heap, (seconds, driver_id))

    def fastest(self) -> Optional[tuple[float, str]]:
        return self._heap[0] if self._heap else None

    def pop_fastest(self) -> Optional[tuple[float, str]]:
        return heapq.heappop(self._heap) if self._heap else None


@dataclass
class _Node:
    key: tuple[float, str]
    left: Optional["_Node"] = None
    right: Optional["_Node"] = None
    height: int = 1


def _height(node: Optional[_Node]) -> int:
    return node.height if node else 0


def _refresh(node: _Node) -> None:
    node.height = 1 + max(_height(node.left), _height(node.right))


def _rotate_right(y: _Node) -> _Node:
    x = y.left
    assert x is not None
    y.left = x.right
    x.right = y
    _refresh(y)
    _refresh(x)
    return x


def _rotate_left(x: _Node) -> _Node:
    y = x.right
    assert y is not None
    x.right = y.left
    y.left = x
    _refresh(x)
    _refresh(y)
    return y


def _rebalance(node: _Node) -> _Node:
    _refresh(node)
    balance = _height(node.left) - _height(node.right)
    if balance > 1:
        assert node.left is not None
        if _height(node.left.left) < _height(node.left.right):
            node.left = _rotate_left(node.left)
        return _rotate_right(node)
    if balance < -1:
        assert node.right is not None
        if _height(node.right.right) < _height(node.right.left):
            node.right = _rotate_right(node.right)
        return _rotate_left(node)
    return node


def _insert(node: Optional[_Node], key: tuple[float, str]) -> _Node:
    if node is None:
        return _Node(key)
    if key < node.key:
        node.left = _insert(node.left, key)
    elif key > node.key:
        node.right = _insert(node.right, key)
    return _rebalance(node)


def _minimum(node: _Node) -> _Node:
    while node.left is not None:
        node = node.left
    return node


def _delete(node: Optional[_Node], key: tuple[float, str]) -> Optional[_Node]:
    if node is None:
        return None
    if key < node.key:
        node.left = _delete(node.left, key)
    elif key > node.key:
        node.right = _delete(node.right, key)
    else:
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        successor = _minimum(node.right)
        node.key = successor.key
        node.right = _delete(node.right, successor.key)
    return _rebalance(node)


class LeaderboardAVL:
    """AVL leaderboard keyed by (best lap seconds, driver ID).

    O(log n) update/remove, O(n) full sorted traversal.
    The secondary driver ID provides deterministic ties.
    """
    def __init__(self) -> None:
        self._root: Optional[_Node] = None
        self._by_driver: dict[str, float] = {}

    def update(self, driver_id: str, best_lap_seconds: float) -> None:
        if best_lap_seconds <= 0:
            raise ValueError("Lap time must be positive")
        if driver_id in self._by_driver:
            self._root = _delete(self._root, (self._by_driver[driver_id], driver_id))
        self._root = _insert(self._root, (best_lap_seconds, driver_id))
        self._by_driver[driver_id] = best_lap_seconds

    def remove(self, driver_id: str) -> bool:
        previous = self._by_driver.pop(driver_id, None)
        if previous is None:
            return False
        self._root = _delete(self._root, (previous, driver_id))
        return True

    def rankings(self) -> list[tuple[float, str]]:
        result: list[tuple[float, str]] = []
        def walk(node: Optional[_Node]) -> None:
            if node is not None:
                walk(node.left)
                result.append(node.key)
                walk(node.right)
        walk(self._root)
        return result

    def __len__(self) -> int:
        return len(self._by_driver)


if __name__ == "__main__":
    index = DriverIndex()
    laps = FastestLaps()
    board = LeaderboardAVL()
    for driver_id, name, car, seconds in [
        ("d1", "Demo Racer One", "07", 17.45),
        ("d2", "Demo Racer Two", "88", 17.21),
        ("d3", "Demo Racer Three", "33", 17.60),
    ]:
        index.add(Driver(driver_id, name, car))
        laps.add(driver_id, seconds)
        board.update(driver_id, seconds)
    print("Driver lookup:", index.find("d1"))
    print("Fastest lap:", laps.fastest())
    print("Leaderboard:", board.rankings())
