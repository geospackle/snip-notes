from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    """User model"""
    email: str
    hashed_password: str


class AuthRepository(ABC):
    """Interface for authentication data storage"""

    @abstractmethod
    def create_user(self, email: str, hashed_password: str) -> bool:
        """
        Create a new user.
        Returns True if successful, False if user already exists.
        """
        pass

    @abstractmethod
    def get_user(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        Returns User if found, None otherwise.
        """
        pass

    @abstractmethod
    def user_exists(self, email: str) -> bool:
        """Check if a user exists"""
        pass
