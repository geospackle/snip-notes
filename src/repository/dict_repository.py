from typing import List, Dict, Optional
from .interface import ResourceRepository, TaggedResource
from nltk.stem import PorterStemmer


class DictResourceRepository(ResourceRepository):
    """In-memory dictionary implementation of ResourceRepository"""

    def __init__(self):
        self._storage: Dict[str, TaggedResource] = {}
        self._stemmer = PorterStemmer()

    def _stem_word(self, word: str) -> str:
        """Apply stemming to a word"""
        return self._stemmer.stem(word.lower())

    def save(self, resource: TaggedResource) -> None:
        """Save a tagged resource"""
        self._storage[resource.id] = resource

    def find_by_tag(self, tag: str, user_email: str) -> List[TaggedResource]:
        """Find all resources that have the specified tag for a specific user (using stemming)"""
        search_stem = self._stem_word(tag)
        return [
            resource
            for resource in self._storage.values()
            if resource.user_email == user_email
            and any(search_stem == self._stem_word(t) for t in resource.tags)
        ]

    def get_all(self, user_email: str) -> List[TaggedResource]:
        """Get all resources for a specific user"""
        return [
            resource
            for resource in self._storage.values()
            if resource.user_email == user_email
        ]

    def get_by_id(self, resource_id: str, user_email: str) -> Optional[TaggedResource]:
        """Get a resource by ID for a specific user"""
        resource = self._storage.get(resource_id)
        if resource and resource.user_email == user_email:
            return resource
        return None
