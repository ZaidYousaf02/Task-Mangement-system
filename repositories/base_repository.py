"""
Base Repository - Abstract base class for all repositories
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository class defining the interface
    for all data repositories in the system
    """
    
    def __init__(self):
        self._data: Dict[str, T] = {}
        self._next_id = 1
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Save an entity to the repository"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get an entity by its ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities from the repository"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by its ID"""
        pass
    
    def exists(self, entity_id: str) -> bool:
        """Check if an entity exists by its ID"""
        return entity_id in self._data
    
    def count(self) -> int:
        """Get the total count of entities"""
        return len(self._data)
    
    def clear(self) -> None:
        """Clear all entities from the repository"""
        self._data.clear()
    
    def _generate_id(self) -> str:
        """Generate a unique ID for new entities"""
        entity_id = f"{self.__class__.__name__.lower()}_{self._next_id}"
        self._next_id += 1
        return entity_id
