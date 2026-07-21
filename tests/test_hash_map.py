import unittest
from src.models.user import User
from src.data_structures.hash_map import CustomHashMap


def make_user(name: str) -> User:
    return User(name)


def chain_length(hm: CustomHashMap, index: int) -> int:
    length = 0
    current = hm.buckets[index]
    while current is not None:
        length += 1
        current = current.next
    return length


class TestCustomHashMapInit(unittest.TestCase):

    def test_default_capacity(self):
        hm = CustomHashMap()
        self.assertEqual(hm.capacity, 10)

    def test_custom_capacity(self):
        hm = CustomHashMap(capacity=64)
        self.assertEqual(hm.capacity, 64)

    def test_all_buckets_are_none_at_start(self):
        hm = CustomHashMap(capacity=5)
        for bucket in hm.buckets:
            self.assertIsNone(bucket)

    def test_size_is_zero_at_start(self):
        hm = CustomHashMap()
        self.assertEqual(hm.size, 0)

    def test_invalid_capacity_raises_value_error(self):
        with self.assertRaises(ValueError):
            CustomHashMap(capacity=0)

    def test_negative_capacity_raises_value_error(self):
        with self.assertRaises(ValueError):
            CustomHashMap(capacity=-5)

    def test_non_integer_capacity_raises_value_error(self):
        with self.assertRaises(ValueError):
            CustomHashMap(capacity=3.5)  # type: ignore[arg-type]


class TestHashFunction(unittest.TestCase):

    def test_hash_returns_valid_index(self):
        hm = CustomHashMap(capacity=10)
        for name in ["alice", "bob", "carol", "dave", "eve"]:
            index = hm._hash(name)
            self.assertGreaterEqual(index, 0)
            self.assertLess(index, hm.capacity)

    def test_hash_is_deterministic(self):
        hm = CustomHashMap(capacity=10)
        self.assertEqual(hm._hash("alice"), hm._hash("alice"))

    def test_known_hash_values_capacity_10(self):
        hm = CustomHashMap(capacity=10)
        self.assertEqual(hm._hash("alice"), 0)
        self.assertEqual(hm._hash("bob"),   7)
        self.assertEqual(hm._hash("carol"), 9)

    def test_known_collision_capacity_2(self):
        hm = CustomHashMap(capacity=2)
        self.assertEqual(hm._hash("bob"), hm._hash("carol"))

    def test_hash_single_character_key(self):
        hm = CustomHashMap(capacity=10)
        index = hm._hash("a")
        self.assertGreaterEqual(index, 0)
        self.assertLess(index, hm.capacity)


class TestPutAndGet(unittest.TestCase):

    def setUp(self):
        self.hm = CustomHashMap()

    def test_put_and_get_single_user(self):
        user = make_user("alice")
        self.hm.put("alice", user)
        self.assertIs(self.hm.get("alice"), user)

    def test_get_returns_none_for_missing_key(self):
        self.assertIsNone(self.hm.get("nobody"))

    def test_put_multiple_distinct_users(self):
        names = ["alice", "bob", "carol", "dave"]
        users = {n: make_user(n) for n in names}
        for name, user in users.items():
            self.hm.put(name, user)
        for name, user in users.items():
            self.assertIs(self.hm.get(name), user)

    def test_put_increments_size(self):
        self.hm.put("alice", make_user("alice"))
        self.assertEqual(self.hm.size, 1)
        self.hm.put("bob", make_user("bob"))
        self.assertEqual(self.hm.size, 2)

    def test_put_same_key_twice_updates_value(self):
        original = make_user("alice")
        updated  = make_user("alice")
        self.hm.put("alice", original)
        self.hm.put("alice", updated)
        self.assertIs(self.hm.get("alice"), updated)

    def test_put_same_key_does_not_increase_size(self):
        self.hm.put("alice", make_user("alice"))
        self.hm.put("alice", make_user("alice"))
        self.assertEqual(self.hm.size, 1)


class TestSeparateChaining(unittest.TestCase):

    def setUp(self):
        self.hm = CustomHashMap(capacity=2)

    def test_two_keys_in_same_bucket_both_retrievable(self):
        bob   = make_user("bob")
        carol = make_user("carol")
        self.hm.put("bob",   bob)
        self.hm.put("carol", carol)

        self.assertIs(self.hm.get("bob"),   bob)
        self.assertIs(self.hm.get("carol"), carol)

    def test_collision_forms_a_chain_in_bucket(self):
        self.hm.put("bob",   make_user("bob"))
        self.hm.put("carol", make_user("carol"))

        colliding_bucket = self.hm._hash("bob")
        self.assertEqual(chain_length(self.hm, colliding_bucket), 2)

    def test_four_users_across_two_buckets(self):
        names = ["alice", "bob", "carol", "dave"]
        users = [make_user(n) for n in names]
        for u in users:
            self.hm.put(u.username, u)

        for u in users:
            self.assertIs(self.hm.get(u.username), u)

        self.assertEqual(chain_length(self.hm, 0), 2)
        self.assertEqual(chain_length(self.hm, 1), 2)

    def test_size_reflects_all_chained_entries(self):
        for name in ["alice", "bob", "carol", "dave"]:
            self.hm.put(name, make_user(name))
        self.assertEqual(self.hm.size, 4)

    def test_update_key_in_chain_does_not_change_chain_length(self):
        self.hm.put("bob",   make_user("bob"))
        self.hm.put("carol", make_user("carol"))
        bucket_idx = self.hm._hash("bob")

        new_bob = make_user("bob")
        self.hm.put("bob", new_bob)

        self.assertEqual(chain_length(self.hm, bucket_idx), 2)
        self.assertIs(self.hm.get("bob"), new_bob)


class TestDelete(unittest.TestCase):

    def setUp(self):
        self.hm = CustomHashMap()
        self.hm.put("alice", make_user("alice"))
        self.hm.put("bob",   make_user("bob"))

    def test_delete_existing_key_returns_true(self):
        self.assertTrue(self.hm.delete("alice"))

    def test_delete_removes_entry(self):
        self.hm.delete("alice")
        self.assertIsNone(self.hm.get("alice"))

    def test_delete_decrements_size(self):
        self.hm.delete("alice")
        self.assertEqual(self.hm.size, 1)

    def test_delete_nonexistent_key_returns_false(self):
        self.assertFalse(self.hm.delete("nobody"))

    def test_delete_nonexistent_does_not_change_size(self):
        self.hm.delete("nobody")
        self.assertEqual(self.hm.size, 2)

    def test_delete_head_of_chain(self):
        hm = CustomHashMap(capacity=2)
        hm.put("bob",   make_user("bob"))
        hm.put("carol", make_user("carol"))

        hm.delete("carol")
        self.assertIsNone(hm.get("carol"))
        self.assertIsNotNone(hm.get("bob"))

    def test_delete_non_head_node_in_chain(self):
        hm = CustomHashMap(capacity=2)
        hm.put("bob",   make_user("bob"))
        hm.put("carol", make_user("carol"))

        hm.delete("bob")
        self.assertIsNone(hm.get("bob"))
        self.assertIsNotNone(hm.get("carol"))

    def test_delete_all_entries(self):
        self.hm.delete("alice")
        self.hm.delete("bob")
        self.assertEqual(self.hm.size, 0)
        self.assertIsNone(self.hm.get("alice"))
        self.assertIsNone(self.hm.get("bob"))


class TestLoadFactor(unittest.TestCase):

    def test_load_factor_is_zero_when_empty(self):
        hm = CustomHashMap(capacity=10)
        self.assertAlmostEqual(hm.load_factor, 0.0)

    def test_load_factor_after_insertions(self):
        hm = CustomHashMap(capacity=10)
        for name in ["alice", "bob", "carol", "dave", "eve"]:
            hm.put(name, make_user(name))
        self.assertAlmostEqual(hm.load_factor, 0.5)

    def test_load_factor_equals_one_when_full(self):
        hm = CustomHashMap(capacity=3)
        hm.put("alice", make_user("alice"))
        hm.put("bob",   make_user("bob"))
        hm.put("carol", make_user("carol"))
        self.assertAlmostEqual(hm.load_factor, 1.0)

    def test_load_factor_can_exceed_one(self):
        hm = CustomHashMap(capacity=2)
        for name in ["alice", "bob", "carol", "dave"]:
            hm.put(name, make_user(name))
        self.assertGreater(hm.load_factor, 1.0)


class TestPythonProtocols(unittest.TestCase):

    def setUp(self):
        self.hm = CustomHashMap()
        self.hm.put("alice", make_user("alice"))
        self.hm.put("bob",   make_user("bob"))

    def test_len_returns_size(self):
        self.assertEqual(len(self.hm), 2)

    def test_len_after_delete(self):
        self.hm.delete("alice")
        self.assertEqual(len(self.hm), 1)

    def test_contains_present_key(self):
        self.assertIn("alice", self.hm)

    def test_contains_absent_key(self):
        self.assertNotIn("zara", self.hm)

    def test_repr_contains_capacity_and_size(self):
        text = repr(self.hm)
        self.assertIn("capacity=", text)
        self.assertIn("size=", text)


class TestAllUsers(unittest.TestCase):

    def test_all_users_empty_map(self):
        hm = CustomHashMap()
        self.assertEqual(hm.all_users(), [])

    def test_all_users_returns_correct_count(self):
        hm = CustomHashMap()
        names = ["alice", "bob", "carol"]
        for n in names:
            hm.put(n, make_user(n))
        self.assertEqual(len(hm.all_users()), 3)

    def test_all_users_contains_all_inserted_users(self):
        hm = CustomHashMap()
        names = ["alice", "bob", "carol"]
        for n in names:
            hm.put(n, make_user(n))
        retrieved_names = {u.username for u in hm.all_users()}
        self.assertEqual(retrieved_names, set(names))

    def test_all_users_works_with_collisions(self):
        hm = CustomHashMap(capacity=2)
        names = ["alice", "bob", "carol", "dave"]
        for n in names:
            hm.put(n, make_user(n))
        retrieved_names = {u.username for u in hm.all_users()}
        self.assertEqual(retrieved_names, set(names))


class TestIntegration(unittest.TestCase):

    def test_store_and_retrieve_user_with_friends(self):
        hm = CustomHashMap()
        alice = make_user("alice")
        alice.add_friend("bob")
        alice.add_friend("carol")
        hm.put("alice", alice)

        retrieved = hm.get("alice")
        self.assertIsNotNone(retrieved)
        self.assertIn("bob",   retrieved.friends)
        self.assertIn("carol", retrieved.friends)

    def test_update_user_friends_reflected_in_map(self):
        hm = CustomHashMap()
        alice = make_user("alice")
        hm.put("alice", alice)

        alice.add_friend("dave")

        retrieved = hm.get("alice")
        self.assertIn("dave", retrieved.friends)

    def test_full_workflow(self):
        hm = CustomHashMap(capacity=10)
        names = ["alice", "bob", "carol", "dave", "eve"]
        users = {n: make_user(n) for n in names}

        for n, u in users.items():
            hm.put(n, u)

        users["alice"].add_friend("bob")
        users["alice"].add_friend("carol")
        users["bob"].add_friend("alice")

        self.assertEqual(hm.get("alice").friend_count(), 2)
        self.assertEqual(hm.get("bob").friend_count(), 1)
        self.assertEqual(len(hm), 5)

        hm.delete("dave")
        hm.delete("eve")

        self.assertEqual(len(hm), 3)
        self.assertIsNone(hm.get("dave"))
        self.assertIsNone(hm.get("eve"))
        self.assertIsNotNone(hm.get("alice"))


if __name__ == "__main__":
    unittest.main()
