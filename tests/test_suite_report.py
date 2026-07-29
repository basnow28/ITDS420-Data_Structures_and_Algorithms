"""
tests/test_suite_report.py
══════════════════════════════════════════════════════════════════════════════
QA Test Suite — Friend Recommendation System
Author  : QA Automation Engineer
Purpose : Academic report test suite with highly readable console output.

Run with:
    python -m unittest tests.test_suite_report -v
    — or —
    python tests/test_suite_report.py

Test classes
────────────
  1. TestHappyPath              — full pipeline, sorted recommendations
  2. TestEdgeCaseNoFriends      — 0-friend user, unknown user
  3. TestEdgeCaseNoMutuals      — dead-end graph, no friends-of-friends
  4. TestHashCollision          — separate chaining, bucket inspection,
                                  monkey-patch forced collision
  5. TestQuickSortStability     — tied mutual counts, non-mutation,
                                  no data loss, integrated pipeline
══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import sys
import unittest

from src.models.user import User
from src.data_structures.hash_map import CustomHashMap
from src.data_structures.queue import Queue
from src.algorithms.sorter import quicksort_desc
from src.algorithms.recommender import get_recommendations


# ─────────────────────────────────────────────────────────────────────────────
# Console formatting helpers
# ─────────────────────────────────────────────────────────────────────────────

_WIDE  = "=" * 68
_THIN  = "-" * 68
_BLOCK = "█" * 68


def _banner(title: str) -> None:
    """Print a bold section header for a test class."""
    print(f"\n{_WIDE}")
    print(f"  {title}")
    print(_WIDE)


def _sub(title: str) -> None:
    """Print a sub-header for an individual test method."""
    print(f"\n{_THIN}")
    print(f"  {title}")
    print(_THIN)


def _pass(msg: str) -> None:
    """Print a green-style PASS line."""
    print(f"  [PASS]  {msg}")


def _info(label: str, value) -> None:
    """Print a labelled data line."""
    print(f"  {label:<28}: {value}")


# ─────────────────────────────────────────────────────────────────────────────
# Shared fixture builder
#
#   Graph used in TestHappyPath and TestQuickSortStability integration test:
#
#       alice ──┬── bob   ──── eve, frank
#               ├── carol ──── eve, grace
#               └── dave  ──── frank, henry
#
#   Friends-of-friends for alice (excluding direct friends & self):
#       eve   seen via bob AND carol  → mutual count = 2
#       frank seen via bob AND dave   → mutual count = 2
#       grace seen via carol only     → mutual count = 1
#       henry seen via dave  only     → mutual count = 1
#
#   Expected sorted result:
#       [("eve", 2), ("frank", 2), ("grace", 1), ("henry", 1)]
#       (eve and frank are tied at the top)
# ─────────────────────────────────────────────────────────────────────────────

def _build_happy_path_map() -> CustomHashMap:
    """Return a populated CustomHashMap for the 8-user social graph."""
    adjacency: dict[str, list[str]] = {
        "alice": ["bob", "carol", "dave"],
        "bob":   ["alice", "eve", "frank"],
        "carol": ["alice", "eve", "grace"],
        "dave":  ["alice", "frank", "henry"],
        "eve":   ["bob", "carol"],
        "frank": ["bob", "dave"],
        "grace": ["carol"],
        "henry": ["dave"],
    }
    hm = CustomHashMap()
    for name, friends in adjacency.items():
        user = User(name)
        for f in friends:
            user.add_friend(f)
        hm.put(name, user)
    return hm


# ══════════════════════════════════════════════════════════════════════════════
#  TEST CLASS 1 — HAPPY PATH
# ══════════════════════════════════════════════════════════════════════════════

class TestHappyPath(unittest.TestCase):
    """
    Validates the complete, successful pipeline:
      Insert 8 users  →  establish bidirectional connections
      →  retrieve recommendations for 'alice'
      →  verify candidate set, mutual counts, and descending sort.
    """

    @classmethod
    def setUpClass(cls) -> None:
        _banner("TEST CLASS 1 — HAPPY PATH  (6 tests)")
        print("  Scenario : 8-user graph; alice has 3 direct friends,")
        print("             each of whom has additional contacts alice")
        print("             does not know yet.")
        cls.hm      = _build_happy_path_map()
        cls.results = get_recommendations("alice", cls.hm)
        print()
        _info("Hash map size",   f"{len(cls.hm)} users stored")
        _info("alice's friends", cls.hm.get("alice").friends)
        _info("Recommendations", cls.results)

    # ── 1-a ──────────────────────────────────────────────────────────────────
    def test_01_result_is_a_non_empty_list(self) -> None:
        _sub("Test 1-a  |  Recommendation list is non-empty")
        _info("Return type", type(self.results).__name__)
        _info("Result",      self.results)
        _info("Length",      len(self.results))

        self.assertIsInstance(self.results, list)
        self.assertGreater(
            len(self.results), 0,
            "Expected at least one recommendation but got an empty list.",
        )
        _pass("Result is a non-empty list.")

    # ── 1-b ──────────────────────────────────────────────────────────────────
    def test_02_candidate_set_is_correct(self) -> None:
        _sub("Test 1-b  |  Exactly the right candidates are returned")
        expected = {"eve", "frank", "grace", "henry"}
        actual   = {name for name, _ in self.results}

        _info("Expected candidates", sorted(expected))
        _info("Actual   candidates", sorted(actual))
        _info("Missing",             sorted(expected - actual) or "none")
        _info("Extra",               sorted(actual  - expected) or "none")

        self.assertEqual(
            actual, expected,
            f"Candidate mismatch. Missing: {expected-actual}  Extra: {actual-expected}",
        )
        _pass("Candidate set matches exactly — no missing, no extra entries.")

    # ── 1-c ──────────────────────────────────────────────────────────────────
    def test_03_mutual_friend_counts_are_accurate(self) -> None:
        _sub("Test 1-c  |  Mutual friend counts are correct for every candidate")
        scores = dict(self.results)

        _info("eve   (via bob + carol)", f"expected 2,  got {scores.get('eve',  'MISSING')}")
        _info("frank (via bob + dave )", f"expected 2,  got {scores.get('frank','MISSING')}")
        _info("grace (via carol only )", f"expected 1,  got {scores.get('grace','MISSING')}")
        _info("henry (via dave  only )", f"expected 1,  got {scores.get('henry','MISSING')}")

        self.assertEqual(scores["eve"],   2, "eve should have 2 mutual friends.")
        self.assertEqual(scores["frank"], 2, "frank should have 2 mutual friends.")
        self.assertEqual(scores["grace"], 1, "grace should have 1 mutual friend.")
        self.assertEqual(scores["henry"], 1, "henry should have 1 mutual friend.")
        _pass("All mutual counts are accurate.")

    # ── 1-d ──────────────────────────────────────────────────────────────────
    def test_04_list_is_sorted_descending(self) -> None:
        _sub("Test 1-d  |  Results are sorted highest-to-lowest by mutual count")
        counts = [count for _, count in self.results]

        _info("Count sequence", counts)

        for i in range(len(counts) - 1):
            self.assertGreaterEqual(
                counts[i], counts[i + 1],
                f"Sort violation at index {i}↔{i+1}: "
                f"{counts[i]} should be >= {counts[i+1]}.",
            )
        _pass(f"Count sequence {counts} is non-increasing.")

    # ── 1-e ──────────────────────────────────────────────────────────────────
    def test_05_direct_friends_are_excluded(self) -> None:
        _sub("Test 1-e  |  Alice's direct friends do NOT appear in recommendations")
        direct   = {"bob", "carol", "dave"}
        returned = {name for name, _ in self.results}
        overlap  = direct & returned

        _info("Alice's direct friends", sorted(direct))
        _info("Returned candidates",   sorted(returned))
        _info("Unwanted overlap",      sorted(overlap) or "none")

        self.assertEqual(
            overlap, set(),
            f"Direct friends found in recommendations: {overlap}",
        )
        _pass("No direct friend leaked into the recommendation list.")

    # ── 1-f ──────────────────────────────────────────────────────────────────
    def test_06_target_absent_from_own_recommendations(self) -> None:
        _sub("Test 1-f  |  Alice is NOT recommended to herself")
        names = [name for name, _ in self.results]

        _info("Returned names", names)
        _info("'alice' present", "alice" in names)

        self.assertNotIn(
            "alice", names,
            "The target user 'alice' must never appear in her own recommendations.",
        )
        _pass("'alice' is correctly absent from her own recommendation list.")


# ══════════════════════════════════════════════════════════════════════════════
#  TEST CLASS 2 — EDGE CASE: USER WITH NO FRIENDS
# ══════════════════════════════════════════════════════════════════════════════

class TestEdgeCaseNoFriends(unittest.TestCase):
    """
    A user stored in the map but with an empty friends list.
    The pipeline must return [] gracefully without raising any exception.
    Also covers the completely-unknown-user path.
    """

    @classmethod
    def setUpClass(cls) -> None:
        _banner("TEST CLASS 2 — EDGE CASE: USER WITH NO FRIENDS  (4 tests)")
        print("  Scenario : 'lonely' is present in the map but has")
        print("             zero friends.  A ghost username 'phantom'")
        print("             has never been inserted at all.")
        cls.hm = CustomHashMap()
        lonely = User("lonely")
        cls.hm.put("lonely", lonely)

        print()
        _info("Map size",              len(cls.hm))
        _info("lonely.friend_count()", lonely.friend_count())
        _info("lonely.friends",        lonely.friends)

    # ── 2-a ──────────────────────────────────────────────────────────────────
    def test_07_no_exception_raised_for_friendless_user(self) -> None:
        _sub("Test 2-a  |  No exception when a friendless user requests recs")
        try:
            result = get_recommendations("lonely", self.hm)
            _info("Result", result)
            _pass("get_recommendations('lonely') completed without exception.")
        except Exception as exc:  # pragma: no cover
            self.fail(f"Unexpected exception raised: {type(exc).__name__}: {exc}")

    # ── 2-b ──────────────────────────────────────────────────────────────────
    def test_08_empty_list_returned_for_friendless_user(self) -> None:
        _sub("Test 2-b  |  Return value is an empty list (not None, not an error)")
        result = get_recommendations("lonely", self.hm)

        _info("Return type", type(result).__name__)
        _info("Result",      repr(result))
        _info("Length",      len(result))

        self.assertIsInstance(result, list, "Return value must be a list, not None.")
        self.assertEqual(
            len(result), 0,
            f"Expected [], got {result}.",
        )
        _pass("Returned [] as expected — friendless user handled safely.")

    # ── 2-c ──────────────────────────────────────────────────────────────────
    def test_09_completely_unknown_user_returns_empty_list(self) -> None:
        _sub("Test 2-c  |  Username that was never inserted also returns []")
        result = get_recommendations("phantom", self.hm)

        _info("Username queried",  "'phantom' (never inserted)")
        _info("Result",            repr(result))

        self.assertEqual(
            result, [],
            f"Unknown user must return [], got {result}.",
        )
        _pass("Unknown username 'phantom' returned [] without crashing.")

    # ── 2-d ──────────────────────────────────────────────────────────────────
    def test_10_queue_stays_empty_when_user_has_no_friends(self) -> None:
        _sub("Test 2-d  |  BFS Queue never receives any items when friends list is empty")
        lonely = self.hm.get("lonely")
        q = Queue()

        for friend_name in lonely.friends:   # iterates zero times
            q.enqueue(friend_name)

        _info("lonely.friends",       lonely.friends)
        _info("Items enqueued",       len(q))
        _info("q.is_empty()",         q.is_empty())

        self.assertTrue(
            q.is_empty(),
            "Queue should remain empty when the user has no friends to enqueue.",
        )
        self.assertEqual(len(q), 0)
        _pass("Queue stays empty — no friends to enqueue, BFS has nothing to process.")


# ══════════════════════════════════════════════════════════════════════════════
#  TEST CLASS 3 — EDGE CASE: FRIENDS EXIST BUT NO MUTUAL FRIENDS
# ══════════════════════════════════════════════════════════════════════════════

class TestEdgeCaseNoMutuals(unittest.TestCase):
    """
    The target user has direct friends, but every direct friend is a
    dead-end (their own friends lists are empty).  The friends-of-friends
    pool is therefore empty → recommendation list must be [].
    """

    @classmethod
    def setUpClass(cls) -> None:
        _banner("TEST CLASS 3 — EDGE CASE: NO MUTUAL FRIENDS (DEAD-END GRAPH)  (4 tests)")
        print("  Scenario : alice → [bob, carol]")
        print("             bob.friends   = []   (dead end)")
        print("             carol.friends = []   (dead end)")
        print("             No friends-of-friends exist, so the candidate")
        print("             pool is empty after BFS completes.")
        cls.hm = CustomHashMap()
        alice = User("alice")
        alice.add_friend("bob")
        alice.add_friend("carol")
        bob   = User("bob")    # intentionally no friends
        carol = User("carol")  # intentionally no friends
        for u in (alice, bob, carol):
            cls.hm.put(u.username, u)
        cls.alice = alice
        cls.bob   = bob
        cls.carol = carol
        print()
        _info("alice.friends", alice.friends)
        _info("bob.friends",   bob.friends)
        _info("carol.friends", carol.friends)
        _info("Map size",      len(cls.hm))

    # ── 3-a ──────────────────────────────────────────────────────────────────
    def test_11_returns_empty_list_for_dead_end_graph(self) -> None:
        _sub("Test 3-a  |  Empty recommendation list when friends have no friends")
        result = get_recommendations("alice", self.hm)

        _info("Result", repr(result))

        self.assertEqual(
            result, [],
            f"Expected [], got {result}.",
        )
        _pass("Dead-end graph correctly returns [] — no candidates to score.")

    # ── 3-b ──────────────────────────────────────────────────────────────────
    def test_12_direct_friends_are_still_in_the_map(self) -> None:
        _sub("Test 3-b  |  The problem is graph topology, not missing data")
        bob_retrieved   = self.hm.get("bob")
        carol_retrieved = self.hm.get("carol")

        _info("get('bob')",   bob_retrieved)
        _info("get('carol')", carol_retrieved)

        self.assertIsNotNone(bob_retrieved,   "'bob' must be in the map.")
        self.assertIsNotNone(carol_retrieved, "'carol' must be in the map.")
        _pass("Both friends are retrievable — zero-recommendation result is due to graph structure.")

    # ── 3-c ──────────────────────────────────────────────────────────────────
    def test_13_no_exception_raised_for_dead_end_graph(self) -> None:
        _sub("Test 3-c  |  No exception raised when BFS finds no level-2 candidates")
        try:
            result = get_recommendations("alice", self.hm)
            _info("Result", result)
            _pass("get_recommendations completed without raising an exception.")
        except Exception as exc:  # pragma: no cover
            self.fail(f"Unexpected exception: {type(exc).__name__}: {exc}")

    # ── 3-d ──────────────────────────────────────────────────────────────────
    def test_14_bfs_queue_drains_completely_with_no_output(self) -> None:
        _sub("Test 3-d  |  Queue is fully drained but yields zero candidates")
        q = Queue()
        alice = self.hm.get("alice")
        for f in alice.friends:
            q.enqueue(f)

        _info("Queue length after enqueueing alice's friends", len(q))

        candidates: list[str] = []
        while not q.is_empty():
            f_name = q.dequeue()
            f_user = self.hm.get(f_name)
            if f_user is None:
                continue
            for fof in f_user.friends:
                if fof != "alice" and fof not in alice.friends:
                    candidates.append(fof)

        _info("Queue empty after BFS",  q.is_empty())
        _info("Candidates collected",   candidates)

        self.assertTrue(q.is_empty(), "Queue must be fully drained.")
        self.assertEqual(candidates, [], "No candidates should be collected from dead-end friends.")
        _pass("Queue fully drained; candidate list is empty as expected.")


# ══════════════════════════════════════════════════════════════════════════════
#  TEST CLASS 4 — HASH COLLISION & SEPARATE CHAINING
# ══════════════════════════════════════════════════════════════════════════════

class TestHashCollision(unittest.TestCase):
    """
    Forces deterministic hash collisions and verifies that the
    Separate Chaining implementation stores and retrieves all entries
    without any data loss, regardless of bucket congestion.

    Collision strategy A (natural):
        capacity=2 causes 'bob' and 'carol' to both hash to bucket 1.
        (Verified offline using Horner's method with base-31.)

    Collision strategy B (monkey-patch):
        Instance attribute _hash is replaced with a lambda that always
        returns 3, forcing every insertion into the same bucket regardless
        of the username.
    """

    @classmethod
    def setUpClass(cls) -> None:
        _banner("TEST CLASS 4 — HASH COLLISION & SEPARATE CHAINING  (6 tests)")
        print("  Strategy A : capacity=2  →  'bob' and 'carol' both hash to bucket 1")
        print("               (Horner base-31, verified independently).")
        print("  Strategy B : instance._hash monkey-patched to lambda key: 3")
        print("               to force a collision for arbitrary usernames.")

        # ── Strategy A ──────────────────────────────────────────────────────
        cls.hm_a = CustomHashMap(capacity=2)
        cls.bob_user   = User("bob")
        cls.carol_user = User("carol")
        cls.bob_user.add_friend("alice")
        cls.carol_user.add_friend("dave")
        cls.hm_a.put("bob",   cls.bob_user)
        cls.hm_a.put("carol", cls.carol_user)
        cls.hash_bob   = cls.hm_a._hash("bob")
        cls.hash_carol = cls.hm_a._hash("carol")

        print()
        _info("capacity",              cls.hm_a.capacity)
        _info("_hash('bob')",          cls.hash_bob)
        _info("_hash('carol')",        cls.hash_carol)
        _info("Collision?",            cls.hash_bob == cls.hash_carol)
        _info("Map size after inserts", len(cls.hm_a))

    # ── 4-a ──────────────────────────────────────────────────────────────────
    def test_15_natural_collision_is_confirmed(self) -> None:
        _sub("Test 4-a  |  'bob' and 'carol' hash to the SAME bucket at capacity=2")
        _info("_hash('bob')",   self.hash_bob)
        _info("_hash('carol')", self.hash_carol)
        _info("Same bucket?",   self.hash_bob == self.hash_carol)

        self.assertEqual(
            self.hash_bob, self.hash_carol,
            f"Expected a collision: 'bob'→{self.hash_bob}, 'carol'→{self.hash_carol}.",
        )
        _pass(f"Collision confirmed — both keys map to bucket {self.hash_bob}.")

    # ── 4-b ──────────────────────────────────────────────────────────────────
    def test_16_both_colliding_users_are_retrievable(self) -> None:
        _sub("Test 4-b  |  get() returns the correct User for each colliding key")
        bob_ret   = self.hm_a.get("bob")
        carol_ret = self.hm_a.get("carol")

        _info("get('bob')",   bob_ret)
        _info("get('carol')", carol_ret)

        self.assertIsNotNone(bob_ret,   "'bob' must be retrievable after collision.")
        self.assertIsNotNone(carol_ret, "'carol' must be retrievable after collision.")
        _pass("Both colliding users retrieved successfully via Separate Chaining.")

    # ── 4-c ──────────────────────────────────────────────────────────────────
    def test_17_retrieved_data_is_intact(self) -> None:
        _sub("Test 4-c  |  Retrieved User objects carry the correct field values")
        bob_ret   = self.hm_a.get("bob")
        carol_ret = self.hm_a.get("carol")

        _info("bob.username",   bob_ret.username)
        _info("bob.friends",    bob_ret.friends)
        _info("carol.username", carol_ret.username)
        _info("carol.friends",  carol_ret.friends)

        self.assertEqual(bob_ret.username,   "bob")
        self.assertEqual(bob_ret.friends,    ["alice"])
        self.assertEqual(carol_ret.username, "carol")
        self.assertEqual(carol_ret.friends,  ["dave"])
        _pass("username and friends fields are intact after chained retrieval.")

    # ── 4-d ──────────────────────────────────────────────────────────────────
    def test_18_map_size_reflects_both_users(self) -> None:
        _sub("Test 4-d  |  size counter correctly tracks both entries despite collision")
        _info("len(hm_a)", len(self.hm_a))

        self.assertEqual(
            len(self.hm_a), 2,
            f"Expected size 2 but got {len(self.hm_a)}.",
        )
        _pass("size == 2 — collision does not corrupt the counter.")

    # ── 4-e ──────────────────────────────────────────────────────────────────
    def test_19_bucket_chain_holds_both_nodes(self) -> None:
        _sub("Test 4-e  |  Inspecting the raw bucket confirms a chain of length 2")
        bucket_idx = self.hash_bob        # == self.hash_carol
        head_node  = self.hm_a.buckets[bucket_idx]

        chain_keys: list[str] = []
        current = head_node
        while current is not None:
            chain_keys.append(current.key)
            current = current.next

        _info("Bucket index",   bucket_idx)
        _info("Chain keys",     chain_keys)
        _info("Chain length",   len(chain_keys))

        self.assertIn("bob",   chain_keys, "'bob' must be in the chain.")
        self.assertIn("carol", chain_keys, "'carol' must be in the chain.")
        self.assertEqual(
            len(chain_keys), 2,
            f"Chain should have exactly 2 nodes, found {len(chain_keys)}.",
        )
        _pass("Bucket chain contains both 'bob' and 'carol' — Separate Chaining works.")

    # ── 4-f ──────────────────────────────────────────────────────────────────
    def test_20_monkey_patched_hash_forces_arbitrary_collision(self) -> None:
        _sub("Test 4-f  |  Monkey-patched _hash forces ALL keys into one bucket")
        hm2 = CustomHashMap(capacity=10)

        # Override the instance's _hash so every key maps to bucket 3.
        # Python resolves self._hash by finding this instance attribute before
        # the class method, so put() and get() both honour the patch.
        hm2._hash = lambda key: 3   # type: ignore[method-assign]

        xavier  = User("xavier")
        yvonne  = User("yvonne")
        xavier.add_friend("alice")
        yvonne.add_friend("bob")

        hm2.put("xavier", xavier)
        hm2.put("yvonne", yvonne)

        _info("Patched _hash('xavier')", hm2._hash("xavier"))
        _info("Patched _hash('yvonne')", hm2._hash("yvonne"))
        _info("Map size after inserts",  len(hm2))

        xavier_ret = hm2.get("xavier")
        yvonne_ret = hm2.get("yvonne")

        _info("get('xavier')", xavier_ret)
        _info("get('yvonne')", yvonne_ret)

        self.assertIsNotNone(xavier_ret, "'xavier' must survive monkey-patch collision.")
        self.assertIsNotNone(yvonne_ret, "'yvonne' must survive monkey-patch collision.")
        self.assertEqual(xavier_ret.username, "xavier")
        self.assertEqual(yvonne_ret.username, "yvonne")
        self.assertEqual(len(hm2), 2)
        _pass("Monkey-patched collision resolved — both arbitrary users retrieved correctly.")


# ══════════════════════════════════════════════════════════════════════════════
#  TEST CLASS 5 — QUICKSORT STABILITY WITH TIED MUTUAL COUNTS
# ══════════════════════════════════════════════════════════════════════════════

class TestQuickSortStability(unittest.TestCase):
    """
    Validates quicksort_desc behaviour when multiple candidates share
    the same mutual-friend count (ties).  Key guarantees:
      • Every entry in the input survives in the output (no data loss).
      • Output is non-increasing (descending).
      • The original input list is NOT mutated.
      • No duplicate entries appear in the output.
      • Tied entries from a real recommendation pipeline are all present.
    """

    @classmethod
    def setUpClass(cls) -> None:
        _banner("TEST CLASS 5 — QUICKSORT STABILITY WITH TIED COUNTS  (6 tests)")
        print("  Focus : quicksort_desc correctness when two or more candidates")
        print("          share the same mutual-friend score.")

    # ── 5-a ──────────────────────────────────────────────────────────────────
    def test_21_all_equal_counts_no_entries_dropped(self) -> None:
        _sub("Test 5-a  |  All entries survive when every count is identical")
        data   = [("alice", 3), ("bob", 3), ("carol", 3), ("dave", 3)]
        result = quicksort_desc(data)

        input_names  = {n for n, _ in data}
        result_names = {n for n, _ in result}

        _info("Input",         data)
        _info("Output",        result)
        _info("Input length",  len(data))
        _info("Output length", len(result))

        self.assertEqual(len(result), 4, "All 4 entries must be present in the output.")
        self.assertEqual(
            result_names, input_names,
            f"Name set mismatch. Missing: {input_names - result_names}",
        )
        _pass("All 4 entries present — no data loss under all-equal scenario.")

    # ── 5-b ──────────────────────────────────────────────────────────────────
    def test_22_all_equal_counts_order_is_non_increasing(self) -> None:
        _sub("Test 5-b  |  All-equal input produces a non-increasing output sequence")
        data   = [("alice", 5), ("bob", 5), ("carol", 5)]
        result = quicksort_desc(data)
        counts = [c for _, c in result]

        _info("Input counts",  [c for _, c in data])
        _info("Output counts", counts)

        for i in range(len(counts) - 1):
            self.assertGreaterEqual(
                counts[i], counts[i + 1],
                f"Non-monotone at index {i}: {counts[i]} < {counts[i+1]}.",
            )
        _pass(f"Count sequence {counts} is non-increasing.")

    # ── 5-c ──────────────────────────────────────────────────────────────────
    def test_23_mixed_counts_with_multiple_ties(self) -> None:
        _sub("Test 5-c  |  Distinct tiers: one top, two mid, three low — all sorted")
        data = [
            ("joe",   5),
            ("eve",   3),
            ("frank", 3),
            ("grace", 1),
            ("henry", 1),
            ("iris",  1),
        ]
        result = quicksort_desc(data)
        counts = [c for _, c in result]

        _info("Input",  data)
        _info("Output", result)

        # Verify descending order
        for i in range(len(counts) - 1):
            self.assertGreaterEqual(
                counts[i], counts[i + 1],
                f"Sort violation at index {i}: {counts[i]} < {counts[i+1]}.",
            )

        # Verify all names are present
        result_names = {n for n, _ in result}
        input_names  = {n for n, _ in data}
        self.assertEqual(result_names, input_names)

        # Verify highest-scored entry is first
        self.assertEqual(
            result[0][0], "joe",
            f"'joe' (score=5) must be at index 0, found {result[0]}.",
        )
        _info("Highest-scored (index 0)", result[0])
        _pass("All 6 entries sorted correctly; 'joe' is at position 0.")

    # ── 5-d ──────────────────────────────────────────────────────────────────
    def test_24_original_list_is_not_mutated(self) -> None:
        _sub("Test 5-d  |  quicksort_desc must not mutate the caller's original list")
        original  = [("eve", 2), ("frank", 2), ("grace", 1), ("henry", 1)]
        snapshot  = list(original)          # deep enough for (str, int) tuples

        _info("Original before sort", original)
        _ = quicksort_desc(original)
        _info("Original after sort",  original)

        self.assertEqual(
            original, snapshot,
            "The caller's list was mutated — quicksort_desc must return a copy.",
        )
        _pass("Original list is unchanged — quicksort_desc returns a new list.")

    # ── 5-e ──────────────────────────────────────────────────────────────────
    def test_25_no_duplicate_entries_in_sorted_output(self) -> None:
        _sub("Test 5-e  |  No duplicate names appear in the sorted output")
        data   = [("alice", 4), ("bob", 4), ("carol", 2), ("dave", 2), ("eve", 1)]
        result = quicksort_desc(data)

        all_names    = [n for n, _ in result]
        unique_names = list(dict.fromkeys(all_names))  # preserves order, removes dupes

        _info("Input",             data)
        _info("Output",            result)
        _info("Duplicate names?",  len(all_names) != len(unique_names))

        self.assertEqual(
            len(all_names), len(unique_names),
            f"Duplicates detected in output: {all_names}.",
        )
        _pass("No duplicate entries — each candidate appears exactly once.")

    # ── 5-f ──────────────────────────────────────────────────────────────────
    def test_26_tied_top_candidates_via_full_pipeline(self) -> None:
        _sub("Test 5-f  |  Full pipeline: tied top-2 candidates both present at correct score")
        print("  Graph: alice → [bob, carol, dave]")
        print("         bob   → [alice, eve, frank]")
        print("         carol → [alice, eve, grace]")
        print("         dave  → [alice, frank, henry]")

        hm     = _build_happy_path_map()
        result = get_recommendations("alice", hm)

        top_score      = result[0][1]
        tied_at_top    = [(n, c) for n, c in result if c == top_score]
        tied_names     = [n for n, _ in tied_at_top]

        _info("Full result",  result)
        _info("Top score",    top_score)
        _info("Tied entries", tied_at_top)

        self.assertEqual(top_score, 2, f"Expected top score 2, got {top_score}.")
        self.assertIn("eve",   tied_names, "'eve' must be in the tied top group.")
        self.assertIn("frank", tied_names, "'frank' must be in the tied top group.")
        self.assertEqual(
            len(tied_at_top), 2,
            f"Exactly 2 candidates should be tied at score 2, got {tied_at_top}.",
        )
        _pass("Both tied candidates (eve, frank) present with correct score of 2.")


# ══════════════════════════════════════════════════════════════════════════════
#  Custom entry-point runner
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n{_BLOCK}")
    print("  FRIEND RECOMMENDATION SYSTEM — QA TEST SUITE")
    print("  Components tested: CustomHashMap · Queue BFS · QuickSort")
    print(f"{_BLOCK}")

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    for cls in [
        TestHappyPath,
        TestEdgeCaseNoFriends,
        TestEdgeCaseNoMutuals,
        TestHashCollision,
        TestQuickSortStability,
    ]:
        suite.addTest(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print(f"\n{_BLOCK}")
    total = result.testsRun
    if result.wasSuccessful():
        print(f"  ALL {total} TESTS PASSED")
    else:
        fails  = len(result.failures)
        errors = len(result.errors)
        passed = total - fails - errors
        print(f"  PASSED  : {passed}/{total}")
        print(f"  FAILED  : {fails}")
        print(f"  ERRORS  : {errors}")
    print(f"{_BLOCK}\n")
