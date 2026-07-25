"""
src/data_structures/queue.py
─────────────────────────────
A generic FIFO Queue backed by a singly-linked list.

Why a linked list instead of a plain Python list?
─────────────────────────────────────────────────
  list.pop(0) is O(n) because every remaining element shifts left in memory.
  A linked-list dequeue is O(1): we only advance the head pointer one step.
  For BFS traversal — where dequeue is called once per visited node — that
  constant factor matters.

Memory layout for a queue holding ["alice", "bob", "carol"]:

      enqueue end                        dequeue end
      (TAIL)                             (HEAD)
        ↓                                  ↓
    [carol] ← [bob] ← [alice] ← None   ← HEAD

  dequeue → returns "alice"
  enqueue("dave") → dave becomes the new TAIL
"""

from __future__ import annotations
from typing import Any


class Queue:
    """
    Generic FIFO Queue.

    Public interface
    ────────────────
      enqueue(item)  – add to back;              O(1)
      dequeue()      – remove and return front;  O(1)
      peek()         – inspect front (no remove); O(1)
      is_empty()     – True when size == 0;       O(1)
      len(q)         – number of items;           O(1)
    """

    # ── Internal node ─────────────────────────────────────────────────────

    class _Node:
        """
        Private linked-list node.

        __slots__ skips the per-instance __dict__, saving ~50 bytes per node.
        That matters when thousands of nodes co-exist during BFS.
        """
        __slots__ = ("data", "next")

        def __init__(self, data: Any) -> None:
            self.data: Any = data
            self.next: Queue._Node | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def __init__(self) -> None:
        """Initialise an empty queue."""
        self._head: Queue._Node | None = None  # front – next to dequeue
        self._tail: Queue._Node | None = None  # back  – last enqueued
        self._size: int = 0

    # ── Core operations ───────────────────────────────────────────────────

    def enqueue(self, item: Any) -> None:
        """
        Add *item* to the back of the queue.

        Steps:
          1. Wrap item in a new _Node (next = None, it will be the tail).
          2. If queue is empty → head and tail both point to this node.
             Otherwise → current tail's next points to new node; tail advances.

        Args:
            item: Any Python object.
        """
        node = Queue._Node(item)

        if self._tail is None:
            # First item: head and tail converge on the single node.
            self._head = node
            self._tail = node
        else:
            # Attach after the current tail, then advance tail.
            self._tail.next = node
            self._tail = node

        self._size += 1

    def dequeue(self) -> Any:
        """
        Remove and return the item at the front of the queue.

        Steps:
          1. Capture data from head node.
          2. Advance head to head.next.
          3. If head is now None the queue is empty – clear tail too.

        Returns:
            The oldest item in the queue (FIFO order).

        Raises:
            IndexError: Queue is empty.
        """
        if self._head is None:
            raise IndexError("dequeue from an empty queue")

        data = self._head.data
        self._head = self._head.next  # advance; old head is now unreferenced

        if self._head is None:
            self._tail = None  # queue drained – tail must also be reset

        self._size -= 1
        return data

    def peek(self) -> Any:
        """
        Return the front item without removing it.

        Returns:
            The item that would be returned by the next dequeue().

        Raises:
            IndexError: Queue is empty.
        """
        if self._head is None:
            raise IndexError("peek into an empty queue")
        return self._head.data

    # ── Queries ───────────────────────────────────────────────────────────

    def is_empty(self) -> bool:
        """Return True when the queue holds no items."""
        return self._size == 0

    def __len__(self) -> int:
        """Enable len(queue)."""
        return self._size

    # ── Representation ────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """
        Visualise queue contents from front (HEAD) to back (TAIL).

        Example:
            Queue(HEAD → ['alice', 'bob', 'carol'] ← TAIL)
        """
        items: list[str] = []
        current = self._head
        while current is not None:
            items.append(repr(current.data))
            current = current.next
        return f"Queue(HEAD → [{', '.join(items)}] ← TAIL)"
