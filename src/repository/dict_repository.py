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

    def find_by_tag(self, tag: str) -> List[TaggedResource]:
        """Find all resources that have the specified tag (using stemming)"""
        search_stem = self._stem_word(tag)
        return [
            resource
            for resource in self._storage.values()
            if any(search_stem == self._stem_word(t) for t in resource.tags)
        ]

    def get_all(self) -> List[TaggedResource]:
        """Get all resources"""
        return list(self._storage.values())

    def get_by_id(self, resource_id: str) -> Optional[TaggedResource]:
        """Get a resource by ID"""
        return self._storage.get(resource_id)
