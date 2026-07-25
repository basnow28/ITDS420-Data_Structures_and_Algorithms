"""
src/algorithms/sorter.py
─────────────────────────
Custom QuickSort for ranking friend recommendations.

Algorithm: Lomuto partition scheme, in-place, descending order.
─────────────────────────────────────────────────────────────────
QuickSort is a divide-and-conquer algorithm:
  1. Pick a pivot element.
  2. Partition: rearrange the subarray so every element whose sort key
     is >= pivot sits left of pivot, and every element < pivot sits right.
  3. Recursively sort both halves.

The Lomuto scheme uses the LAST element of each subarray as the pivot and
sweeps a single left-to-right pass to build the partition boundary.

Visual walkthrough (descending by mutual_count):

  Input:  [("dave",1), ("charlie",3), ("eve",2), ("bob",4)]
  Pivot:  ("bob", 4)   ← arr[high]

  Pass:
    j=0  ("dave",1)    1 >= 4? No   → skip
    j=1  ("charlie",3) 3 >= 4? No   → skip
    j=2  ("eve",2)     2 >= 4? No   → skip

  Place pivot: swap arr[i+1]=arr[0] with arr[3]
  → [("bob",4), ("charlie",3), ("eve",2), ("dave",1)]
  Pivot index = 0

  Left recursion  (0, -1): base case (empty)
  Right recursion (1,  3): sort [("charlie",3), ("eve",2), ("dave",1)]
    → [("charlie",3), ("eve",2), ("dave",1)]

  Final: [("bob",4), ("charlie",3), ("eve",2), ("dave",1)] ✓

Complexity
──────────
  Average case: O(n log n) — pivot splits subarray into roughly equal halves.
  Worst  case:  O(n²)      — pivot is always the min/max element (sorted input).
  Space:        O(log n)   — recursion stack depth.

  The worst case is mitigated in practice because recommendation lists are
  small and not pre-sorted. For large datasets a median-of-three pivot
  selection would be the next enhancement.
"""

from __future__ import annotations


def quicksort_desc(items: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """
    Return a new list sorted by the integer element of each tuple, descending.

    The original list is NOT mutated (a copy is made first).

    Args:
        items: List of (username, mutual_friends_count) tuples.

    Returns:
        A new list sorted from highest to lowest mutual_friends_count.
    """
    arr = list(items)           # shallow copy — callers keep their original
    _quicksort(arr, 0, len(arr) - 1)
    return arr


# ── Private recursive worker ──────────────────────────────────────────────────

def _quicksort(arr: list[tuple[str, int]], low: int, high: int) -> None:
    """
    Recursively sort arr[low..high] in-place (descending by count).

    Base case: when low >= high the subarray has 0 or 1 element — already sorted.

    Args:
        arr:  The list being sorted (modified in-place).
        low:  Left boundary of the current subarray (inclusive).
        high: Right boundary of the current subarray (inclusive).
    """
    if low < high:
        pivot_index = _partition(arr, low, high)
        _quicksort(arr, low, pivot_index - 1)   # sort the "greater" left half
        _quicksort(arr, pivot_index + 1, high)  # sort the "smaller" right half


def _partition(arr: list[tuple[str, int]], low: int, high: int) -> int:
    """
    Lomuto partition for descending order.

    Designates arr[high] as the pivot, then sweeps j from low to high-1.
    Every element whose count is >= pivot_count is swapped into the left
    region (tracked by pointer i).  After the sweep, the pivot is placed
    at arr[i+1] — its final sorted position.

    Invariant after each iteration:
      arr[low .. i]        all have count >= pivot_count  (left region)
      arr[i+1 .. j-1]     all have count <  pivot_count  (right region)
      arr[j .. high-1]    not yet examined
      arr[high]           the pivot (untouched until end)

    Args:
        arr:  The list being partitioned.
        low:  Start index of the subarray.
        high: End index of the subarray; arr[high] is used as the pivot.

    Returns:
        The final index of the pivot element.
    """
    pivot_count: int = arr[high][1]   # sort key: mutual_friends_count
    i: int = low - 1                  # right boundary of the "≥ pivot" region

    for j in range(low, high):
        if arr[j][1] >= pivot_count:
            # This element belongs in the left (larger) partition.
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    # Place the pivot immediately after the last element of the left partition.
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
