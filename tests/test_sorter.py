"""
tests/test_sorter.py
─────────────────────
Unit tests for the custom QuickSort (descending by mutual_friends_count).

Every test uses only plain list operations to verify results — no sort()
or sorted() anywhere in this file.

Covers: empty list, single element, two-element cases, already-sorted input
        (both directions), mixed counts, equal counts, non-mutation of the
        original list, and a larger stress case.
"""

import unittest
from src.algorithms.sorter import quicksort_desc


class TestQuicksortDescBasicCases(unittest.TestCase):

    def test_empty_list_returns_empty(self):
        self.assertEqual(quicksort_desc([]), [])

    def test_single_element_returned_unchanged(self):
        result = quicksort_desc([("alice", 3)])
        self.assertEqual(result, [("alice", 3)])

    def test_two_elements_already_in_order(self):
        inp = [("alice", 5), ("bob", 2)]
        self.assertEqual(quicksort_desc(inp), [("alice", 5), ("bob", 2)])

    def test_two_elements_reversed_order(self):
        inp = [("bob", 2), ("alice", 5)]
        self.assertEqual(quicksort_desc(inp), [("alice", 5), ("bob", 2)])

    def test_two_elements_equal_counts(self):
        inp = [("alice", 3), ("bob", 3)]
        result = quicksort_desc(inp)
        # Both elements must be present; count values must all equal 3.
        self.assertEqual(len(result), 2)
        self.assertTrue(all(count == 3 for _, count in result))

    def test_three_elements_ascending_becomes_descending(self):
        inp = [("a", 1), ("b", 2), ("c", 3)]
        result = quicksort_desc(inp)
        counts = [count for _, count in result]
        self.assertEqual(counts, [3, 2, 1])

    def test_three_elements_already_descending_unchanged(self):
        inp = [("c", 3), ("b", 2), ("a", 1)]
        result = quicksort_desc(inp)
        counts = [count for _, count in result]
        self.assertEqual(counts, [3, 2, 1])


class TestQuicksortDescCorrectness(unittest.TestCase):
    """Verify that the correct username accompanies each count after sorting."""

    def test_usernames_move_with_their_counts(self):
        inp = [("dave", 1), ("charlie", 3), ("eve", 2)]
        result = quicksort_desc(inp)
        self.assertEqual(result[0], ("charlie", 3))
        self.assertEqual(result[1], ("eve", 2))
        self.assertEqual(result[2], ("dave", 1))

    def test_four_elements_mixed(self):
        inp = [("b", 1), ("a", 3), ("d", 5), ("c", 2)]
        result = quicksort_desc(inp)
        counts = [count for _, count in result]
        self.assertEqual(counts, [5, 3, 2, 1])
        # Spot-check: highest-count user is "d"
        self.assertEqual(result[0][0], "d")

    def test_large_distinct_counts(self):
        inp = [(str(i), i) for i in range(10)]   # counts 0..9
        result = quicksort_desc(inp)
        counts = [count for _, count in result]
        self.assertEqual(counts, list(range(9, -1, -1)))  # 9,8,7,...,0

    def test_equal_counts_all_present(self):
        """When all counts tie, every item must still be in the output."""
        inp = [("alice", 2), ("bob", 2), ("carol", 2)]
        result = quicksort_desc(inp)
        self.assertEqual(len(result), 3)
        names = {name for name, _ in result}
        self.assertEqual(names, {"alice", "bob", "carol"})

    def test_partial_ties(self):
        """One clear winner, two tied runners-up."""
        inp = [("alice", 1), ("bob", 3), ("carol", 1)]
        result = quicksort_desc(inp)
        # First place must be bob (count=3).
        self.assertEqual(result[0], ("bob", 3))
        # Remaining two must have count=1.
        tail_counts = [count for _, count in result[1:]]
        self.assertTrue(all(c == 1 for c in tail_counts))


class TestQuicksortDescNonMutation(unittest.TestCase):
    """quicksort_desc must not modify the caller's list."""

    def test_original_list_is_not_mutated(self):
        original = [("dave", 1), ("charlie", 3), ("eve", 2)]
        snapshot = list(original)
        quicksort_desc(original)
        self.assertEqual(original, snapshot)

    def test_returns_new_list_object(self):
        inp = [("alice", 1)]
        result = quicksort_desc(inp)
        self.assertIsNot(result, inp)


class TestQuicksortDescEdgeCases(unittest.TestCase):

    def test_all_same_count_length_preserved(self):
        inp = [("a", 7)] * 5
        result = quicksort_desc(inp)
        self.assertEqual(len(result), 5)

    def test_count_zero(self):
        inp = [("a", 0), ("b", 0)]
        result = quicksort_desc(inp)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(c == 0 for _, c in result))


if __name__ == "__main__":
    unittest.main()
