"""
src/algorithms/recommender.py
──────────────────────────────
Friend recommendation engine.

Algorithm: 2-level BFS (Breadth-First Search) using a custom Queue.
────────────────────────────────────────────────────────────────────
The social graph is stored implicitly: each User holds a friends list,
and users are looked up by username via CustomHashMap.get().

Traversal strategy
──────────────────
Level 0 (root)  : the target user.
Level 1          : target's direct friends  → enqueued into a FIFO Queue.
Level 2          : each level-1 friend's friends  → the candidate pool.

For each candidate we count how many of the target's direct friends also
know them. That count is the "mutual friends" score used for ranking.

Why a Queue (not a Stack)?
  A Stack would give DFS order — irrelevant here because we always stop at
  exactly depth 2. A Queue makes the BFS structure explicit and prepares
  the codebase for a generalised n-hop BFS in future tasks.

Filtering rules applied to level-2 candidates:
  1. Exclude the target user themselves.
  2. Exclude users already in the target's direct friends list.

Counting method
───────────────
Candidates are collected into a plain list — duplicates are intentional.
If "dave" appears three times, three of the target's friends know dave,
meaning dave has 3 mutual friends with the target.

  candidates = ["dave", "eve", "dave", "frank", "dave"]
  → dave: 3 mutual friends
  → eve:  1 mutual friend
  → frank: 1 mutual friend

Counting is done with list.count() — O(n) per unique name, O(n²) total.
For the expected size of a social-network recommendation list (typically
< 100 candidates) this is negligible. A hash-based counter would be O(n)
overall but would reintroduce dict, which is intentionally avoided here.
"""

from __future__ import annotations

from src.data_structures.queue import Queue
from src.data_structures.hash_map import CustomHashMap
from src.algorithms.sorter import quicksort_desc


def get_recommendations(
    target_username: str,
    hash_map: CustomHashMap,
) -> list[tuple[str, int]]:
    """
    Return friend recommendations for *target_username*, ranked by the
    number of mutual friends (descending).

    Pipeline
    ────────
      1. Look up the target user; return [] immediately if not found.
      2. Enqueue every direct friend into a FIFO Queue (level-1 pass).
      3. Dequeue each level-1 friend; collect their friends as candidates
         (level-2 pass), applying the two filter rules above.
      4. Count candidate frequencies (= mutual-friend scores).
      5. Sort with QuickSort descending; return the result.

    Args:
        target_username: The username whose recommendations we want.
        hash_map:        The CustomHashMap acting as the user directory.

    Returns:
        A list of (username, mutual_friends_count) tuples sorted from most
        mutual friends to fewest.  Empty list when no recommendations exist.
    """
    # ── Step 1: Resolve the target user ──────────────────────────────────
    target_user = hash_map.get(target_username)
    if target_user is None:
        return []

    direct_friends: list[str] = target_user.friends  # level-1 reference set

    # ── Step 2: Load level-1 friends into the Queue ───────────────────────
    queue: Queue = Queue()
    for friend_name in direct_friends:
        queue.enqueue(friend_name)

    # ── Step 3: BFS level-2 — collect candidates ─────────────────────────
    # Each appearance of a username in `candidates` represents one mutual
    # friend shared with the target.  Duplicates are intentional.
    candidates: list[str] = []

    while not queue.is_empty():
        friend_name: str = queue.dequeue()

        # Graceful handling: skip ghost references (friend listed but absent
        # from the directory, e.g. a deleted account).
        friend_user = hash_map.get(friend_name)
        if friend_user is None:
            continue

        for fof_name in friend_user.friends:
            if fof_name == target_username:
                continue                           # rule 1: exclude self
            if fof_name in direct_friends:
                continue                           # rule 2: exclude existing friends
            candidates.append(fof_name)

    # ── Step 4: Count mutual-friend frequency ─────────────────────────────
    # `seen` prevents counting the same name twice when iterating.
    # list.count() scans `candidates` linearly — O(n) per unique name.
    seen: list[str] = []
    scored: list[tuple[str, int]] = []

    for name in candidates:
        if name in seen:
            continue
        mutual_count: int = candidates.count(name)
        scored.append((name, mutual_count))
        seen.append(name)

    # ── Step 5: Rank with QuickSort (descending by mutual_count) ─────────
    return quicksort_desc(scored)
