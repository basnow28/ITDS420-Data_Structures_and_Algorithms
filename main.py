from src.models.user import User
from src.data_structures.hash_map import CustomHashMap


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


if __name__ == "__main__":
    main()
