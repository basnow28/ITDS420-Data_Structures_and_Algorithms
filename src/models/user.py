class User:

    def __init__(self, username: str) -> None:
        if not isinstance(username, str) or not username.strip():
            raise ValueError("username must be a non-empty string.")

        self.username: str = username.strip()
        self.friends: list[str] = []

    def add_friend(self, friend_username: str) -> None:
        if friend_username not in self.friends:
            self.friends.append(friend_username)

    def remove_friend(self, friend_username: str) -> None:
        if friend_username in self.friends:
            self.friends.remove(friend_username)

    def is_friend_with(self, friend_username: str) -> bool:
        return friend_username in self.friends

    def friend_count(self) -> int:
        return len(self.friends)

    def __repr__(self) -> str:
        return f"User(username={self.username!r}, friends={self.friends!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self.username == other.username
