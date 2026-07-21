from __future__ import annotations
from typing import Optional

from src.models.user import User
from src.data_structures.node import Node


class CustomHashMap:

    DEFAULT_CAPACITY: int = 10

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be a positive integer.")

        self.capacity: int = capacity
        self.buckets: list[Optional[Node]] = [None] * self.capacity
        self.size: int = 0

    def _hash(self, key: str) -> int:
        BASE = 31
        raw_hash = 0
        for char in key:
            raw_hash = raw_hash * BASE + ord(char)
        return raw_hash % self.capacity

    def put(self, username: str, user_obj: User) -> None:
        index: int = self._hash(username)
        current: Optional[Node] = self.buckets[index]

        while current is not None:
            if current.key == username:
                current.value = user_obj
                return
            current = current.next

        new_node = Node(username, user_obj)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.size += 1

    def get(self, username: str) -> Optional[User]:
        index: int = self._hash(username)
        current: Optional[Node] = self.buckets[index]

        while current is not None:
            if current.key == username:
                return current.value
            current = current.next

        return None

    def delete(self, username: str) -> bool:
        index: int = self._hash(username)
        current: Optional[Node] = self.buckets[index]
        previous: Optional[Node] = None

        while current is not None:
            if current.key == username:
                if previous is None:
                    self.buckets[index] = current.next
                else:
                    previous.next = current.next
                self.size -= 1
                return True

            previous = current
            current = current.next

        return False

    @property
    def load_factor(self) -> float:
        return self.size / self.capacity

    def all_users(self) -> list[User]:
        result: list[User] = []
        for bucket in self.buckets:
            current = bucket
            while current is not None:
                result.append(current.value)
                current = current.next
        return result

    def __len__(self) -> int:
        return self.size

    def __contains__(self, username: str) -> bool:
        return self.get(username) is not None

    def __repr__(self) -> str:
        pairs: list[str] = []
        for bucket in self.buckets:
            current = bucket
            while current is not None:
                pairs.append(f"{current.key!r}: {current.value!r}")
                current = current.next
        inner = ", ".join(pairs)
        return (
            f"CustomHashMap(capacity={self.capacity}, "
            f"size={self.size}, load_factor={self.load_factor:.2f}, "
            f"entries={{{inner}}})"
        )
