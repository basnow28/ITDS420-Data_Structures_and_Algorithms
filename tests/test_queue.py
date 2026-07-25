"""
tests/test_queue.py
────────────────────
Unit tests for the custom FIFO Queue.

Covers: initialisation, enqueue/dequeue order, peek, empty-state guards,
        size tracking, and repr.
"""

import unittest
from src.data_structures.queue import Queue


class TestQueueInit(unittest.TestCase):

    def test_new_queue_is_empty(self):
        q = Queue()
        self.assertTrue(q.is_empty())

    def test_new_queue_has_size_zero(self):
        q = Queue()
        self.assertEqual(len(q), 0)

    def test_head_and_tail_are_none(self):
        q = Queue()
        self.assertIsNone(q._head)
        self.assertIsNone(q._tail)


class TestEnqueue(unittest.TestCase):

    def test_enqueue_single_item(self):
        q = Queue()
        q.enqueue("alice")
        self.assertEqual(len(q), 1)
        self.assertFalse(q.is_empty())

    def test_enqueue_multiple_items(self):
        q = Queue()
        for name in ["alice", "bob", "carol"]:
            q.enqueue(name)
        self.assertEqual(len(q), 3)

    def test_enqueue_any_type(self):
        q = Queue()
        q.enqueue(42)
        q.enqueue(3.14)
        q.enqueue(None)
        self.assertEqual(len(q), 3)

    def test_head_is_first_enqueued(self):
        """The head must always point to the oldest (first enqueued) item."""
        q = Queue()
        q.enqueue("first")
        q.enqueue("second")
        self.assertEqual(q._head.data, "first")

    def test_tail_is_last_enqueued(self):
        """The tail must always point to the newest (last enqueued) item."""
        q = Queue()
        q.enqueue("first")
        q.enqueue("last")
        self.assertEqual(q._tail.data, "last")


class TestDequeue(unittest.TestCase):

    def test_dequeue_single_item(self):
        q = Queue()
        q.enqueue("alice")
        self.assertEqual(q.dequeue(), "alice")

    def test_dequeue_returns_fifo_order(self):
        """Core invariant: items must come out in the order they went in."""
        q = Queue()
        names = ["alice", "bob", "carol", "dave"]
        for name in names:
            q.enqueue(name)
        result = [q.dequeue() for _ in range(len(names))]
        self.assertEqual(result, names)

    def test_dequeue_decrements_size(self):
        q = Queue()
        q.enqueue("alice")
        q.enqueue("bob")
        q.dequeue()
        self.assertEqual(len(q), 1)

    def test_dequeue_last_item_empties_queue(self):
        q = Queue()
        q.enqueue("alice")
        q.dequeue()
        self.assertTrue(q.is_empty())
        self.assertIsNone(q._head)
        self.assertIsNone(q._tail)

    def test_dequeue_empty_queue_raises_index_error(self):
        q = Queue()
        with self.assertRaises(IndexError):
            q.dequeue()

    def test_dequeue_after_all_items_raises_index_error(self):
        q = Queue()
        q.enqueue("alice")
        q.dequeue()
        with self.assertRaises(IndexError):
            q.dequeue()

    def test_enqueue_after_drain_works_correctly(self):
        """Queue must be reusable after being fully drained."""
        q = Queue()
        q.enqueue("alice")
        q.dequeue()
        q.enqueue("bob")            # fresh enqueue after drain
        self.assertEqual(q.peek(), "bob")
        self.assertEqual(len(q), 1)


class TestPeek(unittest.TestCase):

    def test_peek_returns_front_item(self):
        q = Queue()
        q.enqueue("alice")
        q.enqueue("bob")
        self.assertEqual(q.peek(), "alice")

    def test_peek_does_not_remove_item(self):
        q = Queue()
        q.enqueue("alice")
        q.peek()
        self.assertEqual(len(q), 1)
        self.assertEqual(q.dequeue(), "alice")

    def test_peek_empty_queue_raises_index_error(self):
        q = Queue()
        with self.assertRaises(IndexError):
            q.peek()


class TestIsEmptyAndLen(unittest.TestCase):

    def test_is_empty_true_when_new(self):
        self.assertTrue(Queue().is_empty())

    def test_is_empty_false_after_enqueue(self):
        q = Queue()
        q.enqueue("x")
        self.assertFalse(q.is_empty())

    def test_is_empty_true_after_full_drain(self):
        q = Queue()
        q.enqueue("x")
        q.dequeue()
        self.assertTrue(q.is_empty())

    def test_len_tracks_enqueue_and_dequeue(self):
        q = Queue()
        self.assertEqual(len(q), 0)
        q.enqueue("a")
        self.assertEqual(len(q), 1)
        q.enqueue("b")
        self.assertEqual(len(q), 2)
        q.dequeue()
        self.assertEqual(len(q), 1)
        q.dequeue()
        self.assertEqual(len(q), 0)


class TestRepr(unittest.TestCase):

    def test_repr_empty(self):
        q = Queue()
        self.assertIn("HEAD", repr(q))
        self.assertIn("TAIL", repr(q))

    def test_repr_shows_items_in_fifo_order(self):
        q = Queue()
        q.enqueue("alice")
        q.enqueue("bob")
        r = repr(q)
        # "alice" must appear before "bob" (front to back)
        self.assertLess(r.index("alice"), r.index("bob"))


if __name__ == "__main__":
    unittest.main()
