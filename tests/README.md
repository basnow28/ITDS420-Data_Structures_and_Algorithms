# tests

Unit tests for all components of the friend-recommendation system (Task 1). Each file maps directly to one source module.

## Files

| File | Covers |
|------|--------|
| `test_node.py` | `Node` initialisation, next-pointer wiring, chain traversal, `__repr__` |
| `test_hash_map.py` | `CustomHashMap` init, hashing, put/get, separate chaining, delete, load factor, `all_users`, Python protocols, integration |
| `test_user.py` | `User` init, `add_friend`, `remove_friend`, helper methods, equality, input validation |

Run all tests from the project root:

```bash
python -m pytest tests/
```

---

## Known hash values

Several tests engineer **deliberate collisions** by choosing names whose hash values are known in advance. The table below documents those values.

### capacity = 10, BASE = 31

| Username | Bucket index |
|----------|-------------|
| `"alice"` | 0 |
| `"bob"` | 7 |
| `"carol"` | 9 |
| `"dave"` | 0 |
| `"eve"` | 0 |
| `"frank"` | 0 |
| `"zara"` | 0 |

### capacity = 2, BASE = 31

| Username | Bucket index |
|----------|-------------|
| `"alice"` | 0 |
| `"dave"` | 0 |
| `"bob"` | 1 |
| `"carol"` | 1 |

These values are treated as regression constants in `TestHashFunction.test_known_hash_values_capacity_10`. Any change to the hash function must be reflected here.

---

## Test class summary

### `test_node.py`

| Class | What it tests |
|-------|--------------|
| `TestNodeInit` | Key/value stored correctly; `next` is `None` on creation |
| `TestNodeNextPointer` | Manual pointer assignment, tail is `None`, reset to `None` |
| `TestNodeChaining` | 3-node chain (`alice → bob → carol → None`): traversal, length, head value, tail termination |
| `TestNodeRepr` | Contains key; shows `"None"` for no-next, `"..."` for has-next |

### `test_hash_map.py`

| Class | What it tests |
|-------|--------------|
| `TestCustomHashMapInit` | Default/custom capacity; all buckets `None`; size 0; `ValueError` on bad capacity |
| `TestHashFunction` | In-range output; determinism; regression values; known collision at `capacity=2` |
| `TestPutAndGet` | Single/multiple inserts; miss returns `None`; size increments; upsert replaces value without growing size |
| `TestSeparateChaining` | Both colliding keys retrievable; bucket chain length after collision; 4 users across 2 buckets (2 per bucket); upsert in chain keeps chain length |
| `TestDelete` | Returns `True`/`False`; entry removed; size decremented; deleting head of chain; deleting non-head node; deleting all entries |
| `TestLoadFactor` | 0.0 when empty; correct ratio; equals 1.0 when full; can exceed 1.0 with separate chaining |
| `TestPythonProtocols` | `len()`, `in` operator, `repr` format |
| `TestAllUsers` | Empty map returns `[]`; correct count and usernames; works with collisions |
| `TestIntegration` | Store user with friends; mutate after insertion reflected on retrieval; full workflow (insert 5, add friendships, delete 2, verify) |

### `test_user.py`

| Class | What it tests |
|-------|--------------|
| `TestUserInit` | Username stored; friends empty; whitespace stripped; `ValueError` on empty/whitespace/non-string |
| `TestUserAddFriend` | Appends; multiple friends; duplicate is idempotent (`count == 1`); `friend_count` increments |
| `TestUserRemoveFriend` | Removes correctly; safe on non-existent; other friends unaffected; `friend_count` decrements |
| `TestUserHelpers` | `is_friend_with` true/false; `friend_count` empty; equality by username; inequality; `NotImplemented` for non-User; `repr` contains username and friends |
