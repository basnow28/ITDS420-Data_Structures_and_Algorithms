# src/models

This package contains the domain entities for the friend-recommendation system.

## Files

| File | Class | Role |
|------|-------|------|
| `user.py` | `User` | Represents a single user: identity + social connections |

---

## `User`

`User` is the atomic social unit of the system. It is the value type stored in `CustomHashMap` (keyed by `username`).

### Attributes

| Attribute | Type | Notes |
|-----------|------|-------|
| `username` | `str` | Unique identifier; leading/trailing whitespace is stripped on init |
| `friends` | `list[str]` | Ordered list of usernames this user is directly connected to |

`friends` is a plain `list`, not a `set` or `dict`. This choice keeps insertion order and makes it straightforward to iterate for BFS/DFS graph traversal in future tasks.

### Input validation

`__init__` raises `ValueError` if:
- `username` is not a `str`
- `username` is empty or whitespace-only (after stripping)

### Friendship management

**`add_friend(friend_username)`**
Appends the username to `self.friends`. Idempotent: if the username is already present, it is a no-op — the list will never contain duplicates.

**`remove_friend(friend_username)`**
Removes the username from `self.friends`. Safe: silently does nothing if the username is not present, so callers do not need to track connection state.

**`is_friend_with(friend_username) → bool`**
Returns `True` if `friend_username` is in `self.friends`.

**`friend_count() → int`**
Returns `len(self.friends)`.

### Equality

Two `User` objects are equal (`==`) when their `username` strings match. The `friends` list is not considered. `__eq__` returns `NotImplemented` when compared against a non-`User` object, which lets Python fall back to identity comparison.
