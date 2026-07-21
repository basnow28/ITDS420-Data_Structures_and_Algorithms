from __future__ import annotations
from typing import Any


class Node:

    def __init__(self, key: str, value: Any) -> None:
        self.key: str = key
        self.value: Any = value
        self.next: Node | None = None

    def __repr__(self) -> str:
        has_next = self.next is not None
        return (
            f"Node(key={self.key!r}, value={self.value!r}, "
            f"next={'...' if has_next else 'None'})"
        )
