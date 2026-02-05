from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class TaggedResource:
    """Represents a tagged resource (web link or text)"""
    id: str
    content: str
    resource_type: str  # 'web' or 'text'
    tags: List[str]
    description: str
    user_email: str  # Owner of this resource


class ResourceRepository(ABC):
    """Interface for storing and retrieving tagged resources"""

    @abstractmethod
    def save(self, resource: TaggedResource) -> None:
        """Save a tagged resource"""
        pass

    @abstractmethod
    def find_by_tag(self, tag: str, user_email: str) -> List[TaggedResource]:
        """Find all resources that have the specified tag for a specific user"""
        pass

    @abstractmethod
    def get_all(self, user_email: str) -> List[TaggedResource]:
        """Get all resources for a specific user"""
        pass

    @abstractmethod
    def get_by_id(self, resource_id: str, user_email: str) -> Optional[TaggedResource]:
        """Get a resource by ID for a specific user"""
        pass
