from src.models.user import User
from src.data_structures.hash_map import CustomHashMap
from src.algorithms.recommender import get_recommendations


def separator(title: str) -> None:
    width = 60
    print(f"\n{'─' * width}")
    print(f"  {title}")
    print(f"{'─' * width}")


def print_bucket_layout(directory: CustomHashMap) -> None:
    print("  Bucket layout:")
    for i, bucket in enumerate(directory.buckets):
        if bucket is None:
            print(f"    [{i:02d}]  (empty)")
        else:
            chain = []
            current = bucket
            while current is not None:
                chain.append(current.key)
                current = current.next
            arrow = " → ".join(chain)
            print(f"    [{i:02d}]  {arrow}")


def main() -> None:

    separator("1. Create the user directory (capacity = 10)")
    directory = CustomHashMap(capacity=10)
    print(f"  Capacity : {directory.capacity}")
    print(f"  Size     : {len(directory)}")
    print(f"  Load (λ) : {directory.load_factor:.2f}")

    separator("2. Insert six users")
    user_data = ["alice", "bob", "carol", "dave", "eve", "frank"]
    for name in user_data:
        directory.put(name, User(name))
        print(f"  put({name!r})  →  bucket {directory._hash(name)}")

    print(f"\n  Size     : {len(directory)}")
    print(f"  Load (λ) : {directory.load_factor:.2f}  (ideal: < 0.75)")
    print_bucket_layout(directory)

    separator("3. Collision chains (capacity=10, base-31 hash)")
    print("  'alice', 'eve', and 'frank' all hash to bucket 0.")
    print("  They are chained via Node.next pointers (Separate Chaining).")
    bucket_0_len = 0
    cur = directory.buckets[0]
    while cur:
        bucket_0_len += 1
        cur = cur.next
    print(f"  Chain length at bucket 0: {bucket_0_len}")

    separator("4. Retrieve users")
    for name in ["alice", "bob", "nobody"]:
        result = directory.get(name)
        print(f"  get({name!r}) → {result}")

    separator("5. Build friendships")
    connections = [
        ("alice", "bob"),
        ("alice", "carol"),
        ("bob",   "carol"),
        ("carol", "dave"),
        ("dave",  "eve"),
    ]
    for a, b in connections:
        user_a = directory.get(a)
        user_b = directory.get(b)
        user_a.add_friend(b)
        user_b.add_friend(a)
        print(f"  {a} <-> {b}")

    print()
    for name in user_data:
        u = directory.get(name)
        print(f"  {u.username:8} friends: {u.friends}")

    separator("6. Upsert: put() on an existing key updates the value")
    original_alice = directory.get("alice")
    new_alice      = User("alice")
    new_alice.friends = ["zara"]
    directory.put("alice", new_alice)
    print(f"  Before: {original_alice}")
    print(f"  After : {directory.get('alice')}")
    print(f"  Size unchanged: {len(directory)}")

    separator("7. Delete a user")
    print(f"  'dave' in directory: {'dave' in directory}")
    directory.delete("dave")
    print(f"  After delete — 'dave' in directory: {'dave' in directory}")
    print(f"  Size: {len(directory)}")

    separator("8. Final directory state")
    print(f"  Size     : {len(directory)}")
    print(f"  Load (λ) : {directory.load_factor:.2f}")
    print_bucket_layout(directory)

    # ── Rebuild a clean graph for the recommendation demo ─────────
    separator("9. Rebuild graph for friend-recommendation demo")
    rec_dir = CustomHashMap(capacity=17)
    members = ["alice", "bob", "carol", "dave", "eve", "frank", "grace", "henry"]
    for name in members:
        rec_dir.put(name, User(name))

    def connect(a: str, b: str) -> None:
        rec_dir.get(a).add_friend(b)
        rec_dir.get(b).add_friend(a)

    connect("alice", "bob")
    connect("alice", "carol")
    connect("alice", "dave")
    connect("bob",   "eve")
    connect("bob",   "frank")
    connect("carol", "eve")
    connect("carol", "grace")
    connect("dave",  "frank")
    connect("dave",  "henry")

    print("  Friendship graph:")
    for name in members:
        u = rec_dir.get(name)
        print(f"    {u.username:8} → {u.friends}")

    separator("10. Run get_recommendations() for 'alice'")
    print("  2-level BFS via custom Queue:")
    print("    Level 1 (direct friends) : bob, carol, dave")
    print("    Level 2 (friends-of-friends, filtered):")
    print("      from bob   → eve, frank")
    print("      from carol → eve, grace")
    print("      from dave  → frank, henry")
    print()

    recommendations = get_recommendations("alice", rec_dir)
    print("  Ranked recommendations (QuickSort descending by mutual friends):")
    print(f"  {'Rank':<6} {'Username':<12} {'Mutual friends'}")
    print(f"  {'────':<6} {'────────':<12} {'──────────────'}")
    for rank, (username, mutual_count) in enumerate(recommendations, start=1):
        bar = "█" * mutual_count
        print(f"  {rank:<6} {username:<12} {mutual_count}  {bar}")

    separator("11. Verify recommendations for other users")
    for target in ["bob", "carol", "eve"]:
        recs = get_recommendations(target, rec_dir)
        names_and_scores = [(n, c) for n, c in recs]
        print(f"  {target:8} → {names_and_scores}")


if __name__ == "__main__":
    main()
