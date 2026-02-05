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


class ResourceRepository(ABC):
    """Interface for storing and retrieving tagged resources"""

    @abstractmethod
    def save(self, resource: TaggedResource) -> None:
        """Save a tagged resource"""
        pass

    @abstractmethod
    def find_by_tag(self, tag: str) -> List[TaggedResource]:
        """Find all resources that have the specified tag"""
        pass

    @abstractmethod
    def get_all(self) -> List[TaggedResource]:
        """Get all resources"""
        pass

    @abstractmethod
    def get_by_id(self, resource_id: str) -> Optional[TaggedResource]:
        """Get a resource by ID"""
        pass
