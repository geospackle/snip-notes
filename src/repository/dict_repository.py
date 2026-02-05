from typing import List, Dict, Optional
from .interface import ResourceRepository, TaggedResource


class DictResourceRepository(ResourceRepository):
    """In-memory dictionary implementation of ResourceRepository"""

    def __init__(self):
        self._storage: Dict[str, TaggedResource] = {}

    def save(self, resource: TaggedResource) -> None:
        """Save a tagged resource"""
        self._storage[resource.id] = resource

    def find_by_tag(self, tag: str) -> List[TaggedResource]:
        """Find all resources that have the specified tag"""
        tag_lower = tag.lower()
        return [
            resource
            for resource in self._storage.values()
            if tag_lower in [t.lower() for t in resource.tags]
        ]

    def get_all(self) -> List[TaggedResource]:
        """Get all resources"""
        return list(self._storage.values())

    def get_by_id(self, resource_id: str) -> Optional[TaggedResource]:
        """Get a resource by ID"""
        return self._storage.get(resource_id)
