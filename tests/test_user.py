import unittest
from src.models.user import User


class TestUserInit(unittest.TestCase):

    def test_username_is_stored(self):
        user = User("alice")
        self.assertEqual(user.username, "alice")

    def test_friends_list_starts_empty(self):
        user = User("alice")
        self.assertEqual(user.friends, [])
        self.assertIsInstance(user.friends, list)

    def test_whitespace_is_stripped_from_username(self):
        user = User("  bob  ")
        self.assertEqual(user.username, "bob")

    def test_empty_username_raises_value_error(self):
        with self.assertRaises(ValueError):
            User("")

    def test_whitespace_only_username_raises_value_error(self):
        with self.assertRaises(ValueError):
            User("   ")

    def test_non_string_username_raises_value_error(self):
        with self.assertRaises(ValueError):
            User(42)  # type: ignore[arg-type]


class TestUserAddFriend(unittest.TestCase):

    def setUp(self):
        self.alice = User("alice")

    def test_add_friend_appends_to_list(self):
        self.alice.add_friend("bob")
        self.assertIn("bob", self.alice.friends)

    def test_add_multiple_friends(self):
        self.alice.add_friend("bob")
        self.alice.add_friend("carol")
        self.assertEqual(self.alice.friends, ["bob", "carol"])

    def test_add_duplicate_friend_is_idempotent(self):
        self.alice.add_friend("bob")
        self.alice.add_friend("bob")
        self.assertEqual(self.alice.friends.count("bob"), 1)

    def test_friend_count_increments(self):
        self.alice.add_friend("bob")
        self.alice.add_friend("carol")
        self.assertEqual(self.alice.friend_count(), 2)


class TestUserRemoveFriend(unittest.TestCase):

    def setUp(self):
        self.alice = User("alice")
        self.alice.add_friend("bob")
        self.alice.add_friend("carol")

    def test_remove_existing_friend(self):
        self.alice.remove_friend("bob")
        self.assertNotIn("bob", self.alice.friends)

    def test_remove_nonexistent_friend_is_safe(self):
        try:
            self.alice.remove_friend("zara")
        except Exception as exc:
            self.fail(f"remove_friend raised unexpectedly: {exc}")

    def test_other_friends_unaffected_after_removal(self):
        self.alice.remove_friend("bob")
        self.assertIn("carol", self.alice.friends)

    def test_friend_count_decrements(self):
        self.alice.remove_friend("bob")
        self.assertEqual(self.alice.friend_count(), 1)


class TestUserHelpers(unittest.TestCase):

    def test_is_friend_with_true(self):
        alice = User("alice")
        alice.add_friend("bob")
        self.assertTrue(alice.is_friend_with("bob"))

    def test_is_friend_with_false(self):
        alice = User("alice")
        self.assertFalse(alice.is_friend_with("bob"))

    def test_friend_count_empty(self):
        alice = User("alice")
        self.assertEqual(alice.friend_count(), 0)

    def test_equality_same_username(self):
        u1 = User("alice")
        u2 = User("alice")
        self.assertEqual(u1, u2)

    def test_inequality_different_username(self):
        u1 = User("alice")
        u2 = User("bob")
        self.assertNotEqual(u1, u2)

    def test_equality_against_non_user_returns_not_implemented(self):
        alice = User("alice")
        self.assertNotEqual(alice, "alice")

    def test_repr_contains_username(self):
        alice = User("alice")
        self.assertIn("alice", repr(alice))

    def test_repr_contains_friends(self):
        alice = User("alice")
        alice.add_friend("bob")
        self.assertIn("bob", repr(alice))


if __name__ == "__main__":
    unittest.main()
