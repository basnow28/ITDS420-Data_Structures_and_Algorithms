# Friend Recommendation System

A from-scratch implementation of a social-network friend-recommendation engine,
built as a multi-task data-structures and algorithms project.
No built-in `dict`, `queue`, `sort`, or `sorted` are used in any core module.

---

## Directory structure

```
friend-recommendation/
├── main.py                          # Runnable end-to-end demo
├── src/
│   ├── models/
│   │   └── user.py                  # User entity (username + friends list)
│   ├── data_structures/
│   │   ├── node.py                  # Linked-list Node (hash-map chaining)
│   │   ├── hash_map.py              # CustomHashMap — the user directory
│   │   └── queue.py                 # Custom FIFO Queue (BFS traversal)
│   └── algorithms/
│       ├── recommender.py           # get_recommendations() — 2-level BFS
│       └── sorter.py                # quicksort_desc() — Lomuto QuickSort
└── tests/
    ├── test_user.py
    ├── test_node.py
    ├── test_hash_map.py
    ├── test_queue.py
    ├── test_sorter.py
    └── test_recommender.py
```

---

## How to run

```bash
# End-to-end demo
python main.py

# Full test suite (stdlib unittest)
python -m unittest discover -s tests -v
```

---

## User directory (`CustomHashMap`)

### Data structures

| Component | File | Role |
|-----------|------|------|
| `User` | `src/models/user.py` | Domain entity: stores `username` and a `friends: list[str]` |
| `Node` | `src/data_structures/node.py` | Singly-linked list node; holds `key`, `value`, `next` |
| `CustomHashMap` | `src/data_structures/hash_map.py` | Fixed-capacity hash map; array of `Node` chain heads |

### Hash function — Horner's method

```
hash = 0
for each character c in key:
    hash = hash × 31 + ord(c)
index = hash % capacity
```

Base `31` is a small prime used by Java's `String.hashCode()`.
Horner's method avoids computing `31^i` (exponential growth) by
accumulating one multiply-and-add per character — O(len(key)) total.

### Collision resolution — Separate Chaining

When two keys map to the same bucket index, the new `Node` is **prepended**
at the bucket head (O(1)). Retrieval walks the chain comparing keys.

```
bucket[0] → Node("frank") → Node("eve") → Node("alice") → None
```

### Load factor

```
λ = size / capacity
```

| λ range | Effect |
|---------|--------|
| 0 – 0.75 | Short chains; get/put average **O(1)** |
| 0.75 – 1.0 | Chains lengthen; performance degrades |
| > 1.0 | Guaranteed collisions; approaches **O(n)** worst case |

---

## Recommendation engine

### Queue (`src/data_structures/queue.py`)

A generic FIFO Queue backed by a singly-linked list.

```
enqueue end (TAIL)                   dequeue end (HEAD)
      ↓                                     ↓
  [henry] ← [grace] ← [frank] ← [eve] ← HEAD
```

| Operation | Time complexity | Notes |
|-----------|----------------|-------|
| `enqueue` | O(1) | Tail pointer avoids traversal |
| `dequeue` | O(1) | Advance head pointer one step |
| `peek`    | O(1) | Read head data without removal |
| `is_empty`| O(1) | |

`list.pop(0)` would be O(n) — the linked list implementation avoids that.

### Friend recommendation — 2-level BFS (`src/algorithms/recommender.py`)

```
get_recommendations(target_username, hash_map)
```

**Steps:**

```
Step 1  Look up target user.  Return [] if not found.

Step 2  Enqueue all of target's direct friends → Queue
        (these are the level-1 nodes)

Step 3  While queue is not empty:
            friend ← dequeue()
            for each of friend's friends (fof):
                skip if fof == target          ← filter rule 1
                skip if fof in direct_friends  ← filter rule 2
                candidates.append(fof)         ← duplicates intentional

Step 4  Count frequencies in `candidates`:
            dave appears 3× → 3 mutual friends

Step 5  Sort with QuickSort descending → return
```

**Why duplicates encode mutual-friend count:**

```
candidates = ["dave", "eve", "dave", "frank", "dave"]
              ↑ from bob   ↑ from carol        ↑ from frank

dave.count(candidates) == 3  →  3 mutual friends
```

**Example graph and output:**

```
alice — bob, carol, dave
bob   — alice, eve, frank
carol — alice, eve, grace
dave  — alice, frank, henry

Recommendations for alice:
  Rank  Username     Mutual friends
  ────  ────────     ──────────────
  1     eve          2  ██
  2     frank        2  ██
  3     grace        1  █
  4     henry        1  █
```

### QuickSort — descending (`src/algorithms/sorter.py`)

Sorts `list[tuple[str, int]]` by the integer element, highest first.
Returns a **new list**; the original is never mutated.

**Lomuto partition scheme:**

The last element of the subarray is chosen as the pivot.
A single left-to-right sweep moves elements `≥ pivot` into the left
partition, then places the pivot at its final position.

```
Partition step (descending, subarray shown):

  [("dave",1), ("charlie",3), ("eve",2)]   pivot = ("eve",2)

  j=0  ("dave",1):    1 ≥ 2?  No   → skip
  j=1  ("charlie",3): 3 ≥ 2?  Yes  → swap arr[0] ↔ arr[1]
       → [("charlie",3), ("dave",1), ("eve",2)]

  Place pivot: swap arr[i+1]=arr[1] ↔ arr[high]=arr[2]
       → [("charlie",3), ("eve",2), ("dave",1)]   ← sorted ✓
```

**Complexity:**

| Case | Time | Notes |
|------|------|-------|
| Average | O(n log n) | Pivot splits array roughly in half |
| Worst | O(n²) | Pivot is always min or max (already-sorted input) |
| Space | O(log n) | Recursion stack depth |

The worst case is unlikely in practice because recommendation lists are
small and arrive in an arbitrary order.

---

## Architecture

```
         ┌──────────────┐
         │   main.py    │  orchestration / demo
         └──────┬───────┘
                │ uses
     ┌──────────┴──────────┐
     │  src/algorithms/    │
     │  recommender.py     │  2-level BFS  →  QuickSort
     │  sorter.py          │
     └──────────┬──────────┘
                │ uses
     ┌──────────┴──────────────────┐
     │  src/data_structures/       │
     │  hash_map.py  (directory)   │
     │  queue.py     (BFS engine)  │
     │  node.py      (chaining)    │
     └──────────┬──────────────────┘
                │ stores
     ┌──────────┴──────────┐
     │  src/models/        │
     │  user.py            │
     └─────────────────────┘
```
