import json
from pathlib import Path
from typing import Optional
import hashlib

from .interface import AuthRepository, User


class FileAuthRepository(AuthRepository):
    """File-based implementation of AuthRepository"""

    def __init__(self, storage_file: str = "users.json"):
        self.storage_path = Path(storage_file)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create storage file if it doesn't exist"""
        if not self.storage_path.exists():
            self.storage_path.write_text(json.dumps({}))

    def _read_users(self) -> dict:
        """Read all users from file"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_users(self, users: dict):
        """Write all users to file"""
        with open(self.storage_path, 'w') as f:
            json.dump(users, f, indent=2)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, email: str, hashed_password: str) -> bool:
        """Create a new user. Returns True if successful, False if user exists"""
        users = self._read_users()

        if email in users:
            return False

        users[email] = {
            "email": email,
            "hashed_password": hashed_password
        }

        self._write_users(users)
        return True

    def get_user(self, email: str) -> Optional[User]:
        """Get a user by email"""
        users = self._read_users()

        if email not in users:
            return None

        user_data = users[email]
        return User(
            email=user_data["email"],
            hashed_password=user_data["hashed_password"]
        )

    def user_exists(self, email: str) -> bool:
        """Check if a user exists"""
        users = self._read_users()
        return email in users
