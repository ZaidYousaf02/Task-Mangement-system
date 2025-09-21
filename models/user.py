
import re
import hashlib
import secrets
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


@dataclass
class UserProfile:
    first_name: str = ""
    last_name: str = ""
    bio: str = ""
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class ValidationError(Exception):
    pass


class User:
    
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, username: str, email: str, password: str, role: UserRole = UserRole.USER):
        self._id: Optional[str] = None
        self._username = self._validate_username(username)
        self._email = self._validate_email(email)
        self._password_hash = self._hash_password(password)
        self._role = role
        self._profile = UserProfile()
        self._created_at = datetime.utcnow()
        self._permissions = self._get_permissions()
    
    # Properties with clean access control
    @property
    def id(self) -> Optional[str]:
        return self._id
    
    @id.setter
    def id(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise ValidationError("Invalid user ID")
        self._id = value
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def role(self) -> UserRole:
        return self._role
    
    @property
    def profile(self) -> UserProfile:
        return self._profile
    
    @property
    def is_admin(self) -> bool:
        return self._role == UserRole.ADMIN
    
    # Core validation methods
    def _validate_username(self, username: str) -> str:
        if not username or len(username) < 3:
            raise ValidationError("Username must be at least 3 characters")
        return username.lower().strip()
    
    def _validate_email(self, email: str) -> str:
        email = email.strip().lower()
        if not self.EMAIL_REGEX.match(email):
            raise ValidationError("Invalid email format")
        return email
    
    def _hash_password(self, password: str) -> str:
        if len(password) < 6:
            raise ValidationError("Password too short")
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{hash_obj.hex()}"
    
    def _get_permissions(self) -> List[str]:
        permissions = {
            UserRole.ADMIN: ["admin.panel", "user.manage", "system.settings"],
            UserRole.USER: ["profile.update", "content.create"],
            UserRole.GUEST: ["content.read"]
        }
        return permissions.get(self._role, [])
    
    # Essential business methods
    def verify_password(self, password: str) -> bool:
        try:
            salt, stored_hash = self._password_hash.split(':')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == stored_hash
        except:
            return False
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        if not self.verify_password(old_password):
            raise ValidationError("Current password incorrect")
        self._password_hash = self._hash_password(new_password)
        return True
    
    def update_profile(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self._profile, key):
                setattr(self._profile, key, value)
    
    def has_permission(self, permission: str) -> bool:
        return permission in self._permissions
    
    def promote_to_admin(self, admin_user: 'User') -> bool:
        if not admin_user.is_admin:
            raise ValidationError("Only admins can promote users")
        self._role = UserRole.ADMIN
        self._permissions = self._get_permissions()
        return True
    
    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "username": self._username,
            "email": self._email,
            "role": self._role.value,
            "profile": {
                "first_name": self._profile.first_name,
                "last_name": self._profile.last_name,
                "bio": self._profile.bio
            },
            "created_at": self._created_at.isoformat(),
            "permissions": self._permissions
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        user = cls(
            username=data["username"],
            email=data["email"],
            password="dummy",
            role=UserRole(data["role"])
        )
        user._id = data.get("id")
        user._created_at = datetime.fromisoformat(data["created_at"])
        user._permissions = data.get("permissions", [])
        
        # Restore profile
        profile_data = data.get("profile", {})
        user._profile.first_name = profile_data.get("first_name", "")
        user._profile.last_name = profile_data.get("last_name", "")
        user._profile.bio = profile_data.get("bio", "")
        
        return user
    
    @classmethod
    def from_json(cls, json_str: str) -> 'User':
        return cls.from_dict(json.loads(json_str))
    
    # Magic methods for clean representation
    def __str__(self) -> str:
        return f"User({self._username}, {self._email})"
    
    def __repr__(self) -> str:
        return f"User(id='{self._id}', username='{self._username}', role='{self._role.value}')"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, User) and self._username == other._username


# Example usage
if __name__ == "__main__":
    # Create user
    user = User("john_doe", "john@example.com", "password123")
    user.id = "user_001"
    
    # Update profile
    user.update_profile(first_name="John", last_name="Doe", bio="Developer")
    
    # Test features
    print(f"User: {user}")
    print(f"Full name: {user.profile.full_name}")
    print(f"Is admin: {user.is_admin}")
    print(f"Can create content: {user.has_permission('content.create')}")
    print(f"Password valid: {user.verify_password('password123')}")
    
    # Serialization
    user_json = user.to_json()
    user_restored = User.from_json(user_json)
    print(f"Restored user: {user_restored}")
