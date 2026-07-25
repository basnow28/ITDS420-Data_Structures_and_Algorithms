"""
tests/test_recommender.py
──────────────────────────
Unit tests for get_recommendations().

Each test builds a small, hand-crafted social graph inside a CustomHashMap,
calls get_recommendations(), and verifies correctness of both the candidates
and their mutual-friend scores.

Graph notation used in docstrings:
  A — B   means A and B are mutual friends (edge is bidirectional unless noted).
"""

import unittest
from src.models.user import User
from src.data_structures.hash_map import CustomHashMap
from src.algorithms.recommender import get_recommendations


# ── Graph builder helpers ─────────────────────────────────────────────────────

def build_directory(*usernames: str) -> CustomHashMap:
    """Create a CustomHashMap pre-populated with User objects (no friends yet)."""
    hm = CustomHashMap(capacity=17)   # prime capacity keeps λ low in tests
    for name in usernames:
        hm.put(name, User(name))
    return hm


def connect(hm: CustomHashMap, a: str, b: str) -> None:
    """Add a bidirectional friendship edge between users a and b."""
    hm.get(a).add_friend(b)
    hm.get(b).add_friend(a)


def result_as_dict(recommendations: list[tuple[str, int]]) -> dict[str, int]:
    """
    Convert [(name, count), ...] to {name: count} for assertion convenience.
    Uses a plain dict only in test helpers — not in production code.
    """
    return {name: count for name, count in recommendations}


# ── Target-lookup edge cases ──────────────────────────────────────────────────

class TestTargetLookupEdgeCases(unittest.TestCase):

    def test_target_not_in_directory_returns_empty(self):
        hm = build_directory("alice", "bob")
        self.assertEqual(get_recommendations("nobody", hm), [])

    def test_target_has_no_friends_returns_empty(self):
        hm = build_directory("alice", "bob")
        # alice exists but has zero friends
        self.assertEqual(get_recommendations("alice", hm), [])

    def test_ghost_friend_reference_does_not_crash(self):
        """
        A username stored in alice's friends list may not be in the directory
        (deleted account, data inconsistency).  The engine must skip it silently.

        Graph: alice.friends = ["ghost"]   ghost is NOT in hash_map
        """
        hm = build_directory("alice")
        hm.get("alice").add_friend("ghost")   # ghost not added to hash_map
        self.assertEqual(get_recommendations("alice", hm), [])

    def test_friend_with_empty_friends_list_returns_empty(self):
        """
        alice — bob, but bob has no other friends.
        No 2nd-degree candidates exist.
        """
        hm = build_directory("alice", "bob")
        connect(hm, "alice", "bob")
        self.assertEqual(get_recommendations("alice", hm), [])


# ── Filtering rules ───────────────────────────────────────────────────────────

class TestFilteringRules(unittest.TestCase):

    def test_target_user_not_recommended_to_themselves(self):
        """
        alice — bob — alice (cycle)
        bob's friends include alice, who is the target.  alice must not appear
        in the recommendations.
        """
        hm = build_directory("alice", "bob", "carol")
        connect(hm, "alice", "bob")
        connect(hm, "bob",   "carol")
        # bob also knows alice, but alice is the target → filtered

        result = result_as_dict(get_recommendations("alice", hm))
        self.assertNotIn("alice", result)
        self.assertIn("carol", result)

    def test_existing_direct_friend_excluded(self):
        """
        alice — bob — carol
        alice — carol  (carol is already a direct friend!)

        carol must NOT appear in recommendations even though she is bob's friend.
        """
        hm = build_directory("alice", "bob", "carol")
        connect(hm, "alice", "bob")
        connect(hm, "alice", "carol")   # carol is already direct
        connect(hm, "bob",   "carol")

        result = result_as_dict(get_recommendations("alice", hm))
        self.assertNotIn("carol", result)

    def test_all_fof_are_already_direct_friends_returns_empty(self):
        """
        alice — bob — carol
        alice — carol (also direct)
        alice — dave
        bob — alice, carol, dave  (all already alice's friends)
        → nothing to recommend
        """
        hm = build_directory("alice", "bob", "carol", "dave")
        connect(hm, "alice", "bob")
        connect(hm, "alice", "carol")
        connect(hm, "alice", "dave")
        connect(hm, "bob",   "carol")
        connect(hm, "bob",   "dave")

        self.assertEqual(get_recommendations("alice", hm), [])


# ── Mutual-friend scoring ─────────────────────────────────────────────────────

class TestMutualFriendCounting(unittest.TestCase):

    def test_single_candidate_with_one_mutual_friend(self):
        """
        alice — bob — dave
        Expected: dave with 1 mutual friend (bob).
        """
        hm = build_directory("alice", "bob", "dave")
        connect(hm, "alice", "bob")
        connect(hm, "bob",   "dave")

        result = result_as_dict(get_recommendations("alice", hm))
        self.assertEqual(result, {"dave": 1})

    def test_single_candidate_with_two_mutual_friends(self):
        """
        alice — bob ─┐
        alice — carol ┴─ dave
        dave is friends with both bob and carol.
        Expected: dave with 2 mutual friends.
        """
        hm = build_directory("alice", "bob", "carol", "dave")
        connect(hm, "alice", "bob")
        connect(hm, "alice", "carol")
        connect(hm, "bob",   "dave")
        connect(hm, "carol", "dave")

        result = result_as_dict(get_recommendations("alice", hm))
        self.assertEqual(result, {"dave": 2})

    def test_single_candidate_with_three_mutual_friends(self):
        """
        alice — bob, carol, frank  (three direct friends)
        All three are also friends with dave.
        Expected: dave with 3 mutual friends.
        """
        hm = build_directory("alice", "bob", "carol", "frank", "dave")
        connect(hm, "alice", "bob")
        connect(hm, "alice", "carol")
        connect(hm, "alice", "frank")
        connect(hm, "bob",   "dave")
        connect(hm, "carol", "dave")
        connect(hm, "frank", "dave")

        result = result_as_dict(get_recommendations("alice", hm))
        self.assertEqual(result["dave"], 3)

    def test_multiple_candidates_different_scores(self):
        """
        alice — bob, carol
        bob   — alice, dave, eve
        carol — alice, dave

        candidates raw: [dave, eve, dave]
        dave: 2 mutual friends (bob + carol)
        eve:  1 mutual friend  (bob only)
        """
        hm = build_directory("alice", "bob", "carol", "dave", "eve")
        connect(hm, "alice", "bob")
        connect(hm, "alice", "carol")
        connect(hm, "bob",   "dave")
        connect(hm, "bob",   "eve")
        connect(hm, "carol", "dave")

        result = result_as_dict(get_recommendations("alice", hm))
        self.assertEqual(result["dave"], 2)
        self.assertEqual(result["eve"],  1)


# ── Ranking (QuickSort integration) ──────────────────────────────────────────

class TestRankingOrder(unittest.TestCase):

    def test_result_sorted_descending_by_mutual_count(self):
        """
        alice — bob, carol, frank
        bob   — alice, dave, eve
        carol — alice, dave
        frank — alice, eve, grace

        dave:  2 mutual (bob, carol)
        eve:   2 mutual (bob, frank)
        grace: 1 mutual (frank)

        Top result must have the highest count.
        """
        hm = build_directory("alice", "bob", "carol", "frank", "dave", "eve", "grace")
        connect(hm, "alice", "bob")
        connect(hm, "alice", "carol")
        connect(hm, "alice", "frank")
        connect(hm, "bob",   "dave")
        connect(hm, "bob",   "eve")
        connect(hm, "carol", "dave")
        connect(hm, "frank", "eve")
        connect(hm, "frank", "grace")

        recommendations = get_recommendations("alice", hm)

        # Verify strict descending order
        counts = [count for _, count in recommendations]
        for i in range(len(counts) - 1):
            self.assertGreaterEqual(counts[i], counts[i + 1])

    def test_highest_mutual_count_is_first(self):
        """
        Simplest possible ranking check: the candidate with more mutual
        friends must appear before candidates with fewer.
        """
        hm = build_directory("alice", "bob", "carol", "dave", "eve")
        connect(hm, "alice", "bob")
        connect(hm, "alice", "carol")
        connect(hm, "bob",   "dave")
        connect(hm, "carol", "dave")
        connect(hm, "bob",   "eve")     # eve has only 1 mutual friend (bob)

        recommendations = get_recommendations("alice", hm)
        self.assertEqual(recommendations[0][0], "dave")   # 2 mutuals → rank 1
        self.assertEqual(recommendations[0][1], 2)

    def test_all_usernames_present_in_result(self):
        """Every eligible 2nd-degree connection must appear exactly once."""
        hm = build_directory("alice", "bob", "carol", "dave", "eve")
        connect(hm, "alice", "bob")
        connect(hm, "alice", "carol")
        connect(hm, "bob",   "dave")
        connect(hm, "carol", "eve")

        names = {name for name, _ in get_recommendations("alice", hm)}
        self.assertEqual(names, {"dave", "eve"})

    def test_no_duplicate_usernames_in_result(self):
        """Each recommended username must appear exactly once, not once per path."""
        hm = build_directory("alice", "bob", "carol", "dave")
        connect(hm, "alice", "bob")
        connect(hm, "alice", "carol")
        connect(hm, "bob",   "dave")
        connect(hm, "carol", "dave")   # dave reachable via two paths

        names = [name for name, _ in get_recommendations("alice", hm)]
        self.assertEqual(len(names), len(set(names)))  # no duplicates


# ── Return-type contract ──────────────────────────────────────────────────────

class TestReturnTypeContract(unittest.TestCase):

    def test_returns_a_list(self):
        hm = build_directory("alice")
        self.assertIsInstance(get_recommendations("alice", hm), list)

    def test_each_element_is_a_tuple_of_str_and_int(self):
        hm = build_directory("alice", "bob", "dave")
        connect(hm, "alice", "bob")
        connect(hm, "bob",   "dave")
        for item in get_recommendations("alice", hm):
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[0], str)
            self.assertIsInstance(item[1], int)

    def test_mutual_count_is_positive(self):
        hm = build_directory("alice", "bob", "dave")
        connect(hm, "alice", "bob")
        connect(hm, "bob",   "dave")
        for _, count in get_recommendations("alice", hm):
            self.assertGreater(count, 0)


# ── Integration: larger graph ─────────────────────────────────────────────────

class TestIntegrationLargerGraph(unittest.TestCase):
    """
    Network topology:
        alice — bob, carol, dave
        bob   — alice, eve, frank
        carol — alice, eve, grace
        dave  — alice, frank, henry

    2nd-degree candidates for alice:
        from bob:   eve, frank
        from carol: eve, grace
        from dave:  frank, henry

    Mutual-friend counts:
        eve:   2  (bob, carol)
        frank: 2  (bob, dave)
        grace: 1  (carol)
        henry: 1  (dave)
    """

    def setUp(self):
        names = ["alice", "bob", "carol", "dave", "eve", "frank", "grace", "henry"]
        self.hm = build_directory(*names)
        connect(self.hm, "alice", "bob")
        connect(self.hm, "alice", "carol")
        connect(self.hm, "alice", "dave")
        connect(self.hm, "bob",   "eve")
        connect(self.hm, "bob",   "frank")
        connect(self.hm, "carol", "eve")
        connect(self.hm, "carol", "grace")
        connect(self.hm, "dave",  "frank")
        connect(self.hm, "dave",  "henry")

    def test_correct_candidate_set(self):
        names = {n for n, _ in get_recommendations("alice", self.hm)}
        self.assertEqual(names, {"eve", "frank", "grace", "henry"})

    def test_correct_mutual_friend_scores(self):
        scores = result_as_dict(get_recommendations("alice", self.hm))
        self.assertEqual(scores["eve"],   2)
        self.assertEqual(scores["frank"], 2)
        self.assertEqual(scores["grace"], 1)
        self.assertEqual(scores["henry"], 1)

    def test_top_recommendations_have_highest_score(self):
        recommendations = get_recommendations("alice", self.hm)
        # First two must have count=2
        self.assertEqual(recommendations[0][1], 2)
        self.assertEqual(recommendations[1][1], 2)
        # Last two must have count=1
        self.assertEqual(recommendations[2][1], 1)
        self.assertEqual(recommendations[3][1], 1)

    def test_existing_direct_friends_absent(self):
        names = {n for n, _ in get_recommendations("alice", self.hm)}
        for direct in ["bob", "carol", "dave"]:
            self.assertNotIn(direct, names)

    def test_alice_not_in_own_recommendations(self):
        names = {n for n, _ in get_recommendations("alice", self.hm)}
        self.assertNotIn("alice", names)


if __name__ == "__main__":
    unittest.main()
