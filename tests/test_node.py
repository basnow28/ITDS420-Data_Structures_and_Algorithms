import unittest
from src.models.user import User
from src.data_structures.node import Node


class TestNodeInit(unittest.TestCase):

    def setUp(self):
        self.user = User("alice")
        self.node = Node("alice", self.user)

    def test_key_is_stored(self):
        self.assertEqual(self.node.key, "alice")

    def test_value_is_stored(self):
        self.assertIs(self.node.value, self.user)

    def test_next_is_none_on_creation(self):
        self.assertIsNone(self.node.next)


class TestNodeNextPointer(unittest.TestCase):

    def test_set_next_to_another_node(self):
        node_a = Node("alice", User("alice"))
        node_b = Node("bob", User("bob"))
        node_a.next = node_b
        self.assertIs(node_a.next, node_b)

    def test_next_of_tail_is_none(self):
        node_a = Node("alice", User("alice"))
        node_b = Node("bob", User("bob"))
        node_a.next = node_b
        self.assertIsNone(node_b.next)

    def test_reset_next_to_none(self):
        node_a = Node("alice", User("alice"))
        node_b = Node("bob", User("bob"))
        node_a.next = node_b
        node_a.next = None
        self.assertIsNone(node_a.next)


class TestNodeChaining(unittest.TestCase):

    def setUp(self):
        self.alice = Node("alice", User("alice"))
        self.bob   = Node("bob",   User("bob"))
        self.carol = Node("carol", User("carol"))

        self.alice.next = self.bob
        self.bob.next   = self.carol

    def test_chain_traversal_visits_all_nodes(self):
        keys = []
        current = self.alice
        while current is not None:
            keys.append(current.key)
            current = current.next
        self.assertEqual(keys, ["alice", "bob", "carol"])

    def test_chain_length_is_three(self):
        length = 0
        current = self.alice
        while current is not None:
            length += 1
            current = current.next
        self.assertEqual(length, 3)

    def test_head_value_is_alice(self):
        self.assertEqual(self.alice.value.username, "alice")

    def test_tail_next_is_none(self):
        self.assertIsNone(self.carol.next)


class TestNodeRepr(unittest.TestCase):

    def test_repr_contains_key(self):
        node = Node("alice", User("alice"))
        self.assertIn("alice", repr(node))

    def test_repr_shows_none_when_no_next(self):
        node = Node("alice", User("alice"))
        self.assertIn("None", repr(node))

    def test_repr_shows_ellipsis_when_has_next(self):
        node_a = Node("alice", User("alice"))
        node_a.next = Node("bob", User("bob"))
        self.assertIn("...", repr(node_a))


if __name__ == "__main__":
    unittest.main()
