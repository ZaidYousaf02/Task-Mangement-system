"""
User Repository - Data access for User entities
"""

from typing import List, Optional
from .base_repository import BaseRepository
from models.user import User


class UserRepository(BaseRepository[User]):
    """
    Repository for User entities with in-memory storage
    Implements the repository pattern for clean data access
    """
    
    def save(self, user: User) -> User:
        """Save a user to the repository"""
        if not user.id:
            user.id = self._generate_id()
        
        self._data[user.id] = user
        return user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self._data.get(user_id)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        for user in self._data.values():
            if user.username == username:
                return user
        return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        for user in self._data.values():
            if user.email == email:
                return user
        return None
    
    def get_all(self) -> List[User]:
        """Get all users"""
        return list(self._data.values())
    
    def delete(self, user_id: str) -> bool:
        """Delete a user by ID"""
        if user_id in self._data:
            del self._data[user_id]
            return True
        return False
    
    def get_by_role(self, role) -> List[User]:
        """Get all users with a specific role"""
        return [user for user in self._data.values() if user.role == role]
    
    def search_by_name(self, name_query: str) -> List[User]:
        """Search users by name (first name, last name, or full name)"""
        query_lower = name_query.lower()
        matching_users = []
        
        for user in self._data.values():
            if (query_lower in user.profile.first_name.lower() or
                query_lower in user.profile.last_name.lower() or
                query_lower in user.profile.full_name.lower()):
                matching_users.append(user)
        
        return matching_users
