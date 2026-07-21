# src/data_structures

This package provides the two building blocks of the user directory: a linked-list `Node` and the `CustomHashMap` that uses nodes for collision resolution.

## Files

| File | Class | Role |
|------|-------|------|
| `node.py` | `Node` | Singly-linked list node; one key-value pair per node |
| `hash_map.py` | `CustomHashMap` | Fixed-capacity hash map; maps usernames to `User` objects |

---

## `Node`

`Node` is the atomic unit of each bucket's linked list. It holds:

- `key: str` — the username string used for lookup
- `value: Any` — typed as `Any` so `CustomHashMap` can be reused beyond `User`
- `next: Node | None` — pointer to the next node in the same bucket chain; `None` signals the end of the chain

A freshly created node is isolated (`next = None`) until it is wired into a chain by `CustomHashMap.put()`.

### Chain visualisation

When three keys collide in the same bucket:

```
bucket[i] → Node("alice", alice_obj)
                 └─ next → Node("carol", carol_obj)
                                └─ next → Node("eve", eve_obj)
                                               └─ next → None
```

`__repr__` shows `'...'` for the `next` field when a successor exists (to avoid recursive printing of the whole chain) and `'None'` at the tail.

---

## `CustomHashMap`

A fixed-capacity hash map that stores `username → User` pairs using a plain Python `list` as the underlying array — explicitly **not** a `dict` or `set`. This is intentional: the implementation teaches the algorithm from scratch.

### Storage layout

`self.buckets` is a list of length `self.capacity`. Each slot is either `None` (empty bucket) or the **head `Node`** of a linked list chain. New entries are always **prepended** at the bucket head — O(1) — rather than appended (which would require walking the whole chain to find the tail).

### Hashing — Horner's method

```
hash = 0
for each character c in key:
    hash = hash * BASE + ord(c)
index = hash % capacity
```

`BASE = 31` because:
- It is a small prime, minimising the chance that two characters produce the same contribution.
- It is used by Java's `String.hashCode()` for the same reason.
- Odd primes avoid the clustering that even bases cause with the modulo operation.

Horner's method avoids computing large powers (`BASE^i` grows exponentially). Each iteration performs exactly one multiply and one add — O(len(key)) total.

### Collision resolution — Separate Chaining

When two keys produce the same bucket index, the new node is **prepended** to the existing chain. All entries in the chain remain retrievable; `get()` and `delete()` walk the chain comparing keys.

### Load factor

```
λ = size / capacity
```

| λ range | Average performance |
|---------|---------------------|
| 0.0 – 0.75 | Short chains; get/put average O(1) |
| 0.75 – 1.0 | Chains lengthen; performance begins to degrade |
| > 1.0 | Multiple keys per bucket guaranteed; average O(λ), worst O(n) |

A production hash map (e.g. Python's `dict`) auto-resizes at ~0.75 to keep O(1) average. Resizing is intentionally deferred in this implementation so the core algorithm stays readable. Prefer a prime capacity (e.g. 97, 101) to minimise clustering.

### CRUD operations

**`put(username, user_obj)` — upsert**

1. Hash `username` → bucket index.
2. Walk the chain comparing keys.
   - Match found: overwrite the value in place; return without incrementing `size`.
   - No match: prepend a new `Node` at the bucket head (`new_node.next = old_head`, `bucket = new_node`); increment `size`.

**`get(username)`**

Walk the chain at the hashed bucket; return the `User` on a key match, `None` if the chain is exhausted (miss).

**`delete(username)` — two-pointer pattern**

Maintain a `(previous, current)` pair as the chain is walked:

- `previous is None` → target is the head; point the bucket directly at `current.next`.
- Otherwise → bypass the target via `previous.next = current.next`.

Returns `True` on success, `False` if the key is not found.

### Python protocols

| Protocol | Behaviour |
|----------|-----------|
| `len(hm)` | Returns `size` |
| `'alice' in hm` | Delegates to `get()`; `True` if the key exists |
| `repr(hm)` | Full map dump with capacity, size, load factor, and all entries |
