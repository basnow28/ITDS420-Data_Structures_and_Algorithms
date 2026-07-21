# Friend Recommendation System

This is **Task 1** of a larger friend-recommendation system. It establishes the core user directory — a custom hash map storing `username → User` mappings — and a bidirectional friendship graph on top of it.

## Directory structure

```
friend-recommendation/
├── main.py                      # Runnable demo of all Task 1 operations
├── src/
│   ├── data_structures/
│   │   ├── node.py              # Singly-linked list Node (separate chaining)
│   │   └── hash_map.py          # CustomHashMap: the user directory
│   └── models/
│       └── user.py              # User entity (username + friends list)
└── tests/
    ├── test_node.py
    ├── test_hash_map.py
    └── test_user.py
```

## How to run

```bash
# Demo script
python main.py

# Full test suite
python -m pytest tests/
```

## Demo walkthrough (`main.py`)

`main.py` runs eight labelled sections that exercise every feature built in Task 1:

| Section | What it demonstrates |
|---------|----------------------|
| 1 | Create a `CustomHashMap` with `capacity=10` |
| 2 | Insert six users; print each resolved bucket index |
| 3 | Collision chains — `alice`, `eve`, and `frank` all hash to bucket 0 with `BASE=31`, `capacity=10`; the chain length at bucket 0 is printed |
| 4 | Retrieve users by key, including a miss (`"nobody"`) |
| 5 | Build a bidirectional friendship graph; connections are added symmetrically (`user_a.add_friend(b)` and `user_b.add_friend(a)`) |
| 6 | Upsert — calling `put()` on an existing key replaces the value without changing `size` |
| 7 | Delete `dave` and verify that `in` (`__contains__`) reflects the removal |
| 8 | Print the final bucket layout and load factor |

The `print_bucket_layout()` helper traverses each bucket's linked list and prints the chain with ` → ` arrows.

## Architecture overview

The project is split into two concerns:

- **Infrastructure** (`src/data_structures/`) — the hash map and its node building block. Deliberately implemented with a plain Python `list`, not a `dict`, as a data-structures exercise.
- **Domain** (`src/models/`) — the `User` entity that the hash map stores.

Future tasks will add BFS/DFS graph traversal over the friendship edges for friend-of-friend recommendations, and potentially hash map resizing/rehashing.
