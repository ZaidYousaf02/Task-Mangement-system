"""
User Service - Business logic for user management
"""

from typing import List, Optional, Dict, Any

from models.user import User, UserRole, ValidationError


class UserService:
    """
    Service class for user-related business logic
    Clean separation of concerns with proper validation
    """
    
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.USER
    ) -> User:
        """Create a new user with validation"""
        # Check if username already exists
        if self.user_repository.get_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        
        # Check if email already exists
        if self.user_repository.get_by_email(email):
            raise ValueError(f"Email '{email}' already exists")
        
        try:
            user = User(
                username=username,
                email=email,
                password=password,
                role=role
            )
            return self.user_repository.save(user)
        except ValidationError as e:
            raise ValueError(str(e))
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self.user_repository.get_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.user_repository.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        return self.user_repository.get_by_email(email)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        user = self.user_repository.get_by_username(username)
        if user and user.verify_password(password):
            return user
        return None
    
    def update_user_profile(
        self,
        user_id: str,
        **profile_data
    ) -> User:
        """Update user profile information"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Validate profile data
        valid_fields = ['first_name', 'last_name', 'bio']
        for key, value in profile_data.items():
            if key not in valid_fields:
                raise ValueError(f"Invalid profile field: {key}")
            if not isinstance(value, str):
                raise ValueError(f"Profile field {key} must be a string")
        
        user.update_profile(**profile_data)
        return self.user_repository.save(user)
    
    def change_user_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> User:
        """Change user password with validation"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        try:
            user.change_password(old_password, new_password)
            return self.user_repository.save(user)
        except ValidationError as e:
            raise ValueError(str(e))
    
    def promote_user(
        self,
        user_id: str,
        new_role: UserRole,
        promoter_id: str
    ) -> User:
        """Promote a user to a new role"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        promoter = self.get_user(promoter_id)
        if not promoter:
            raise ValueError(f"Promoter with ID {promoter_id} not found")
        
        # Only admins can promote users
        if not promoter.is_admin:
            raise PermissionError("Only admins can promote users")
        
        # Cannot demote the last admin
        if user.is_admin and new_role != UserRole.ADMIN:
            admin_count = len(self.get_users_by_role(UserRole.ADMIN))
            if admin_count <= 1:
                raise ValueError("Cannot demote the last admin user")
        
        user._role = new_role
        user._permissions = user._get_permissions()
        return self.user_repository.save(user)
    
    def deactivate_user(self, user_id: str, deactivator_id: str) -> User:
        """Deactivate a user account"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        deactivator = self.get_user(deactivator_id)
        if not deactivator:
            raise ValueError(f"Deactivator with ID {deactivator_id} not found")
        
        # Only admins can deactivate users
        if not deactivator.is_admin:
            raise PermissionError("Only admins can deactivate users")
        
        # Cannot deactivate the last admin
        if user.is_admin:
            admin_count = len(self.get_users_by_role(UserRole.ADMIN))
            if admin_count <= 1:
                raise ValueError("Cannot deactivate the last admin user")
        
        # For now, we'll just change the role to GUEST
        # In a real system, you might have an 'active' field
        user._role = UserRole.GUEST
        user._permissions = user._get_permissions()
        return self.user_repository.save(user)
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get all users with a specific role"""
        all_users = self.user_repository.get_all()
        return [user for user in all_users if user.role == role]
    
    def search_users(
        self,
        query: str,
        role: Optional[UserRole] = None
    ) -> List[User]:
        """Search users with filters"""
        all_users = self.user_repository.get_all()
        filtered_users = []
        
        query_lower = query.lower()
        
        for user in all_users:
            # Text search in username, email, and profile
            matches_text = (
                query_lower in user.username.lower() or
                query_lower in user.email.lower() or
                query_lower in user.profile.first_name.lower() or
                query_lower in user.profile.last_name.lower()
            )
            
            if not matches_text:
                continue
            
            # Role filter
            if role and user.role != role:
                continue
            
            filtered_users.append(user)
        
        return filtered_users
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        all_users = self.user_repository.get_all()
        
        stats = {
            "total": len(all_users),
            "by_role": {},
            "recent_registrations": 0
        }
        
        # Count by role
        for role in UserRole:
            count = len([user for user in all_users if user.role == role])
            stats["by_role"][role.value] = count
        
        # Count recent registrations (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        stats["recent_registrations"] = len([
            user for user in all_users 
            if user._created_at >= thirty_days_ago
        ])
        
        return stats
    
    def get_user_activity_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user activity summary"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        return {
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_admin": user.is_admin,
            "profile": {
                "first_name": user.profile.first_name,
                "last_name": user.profile.last_name,
                "full_name": user.profile.full_name,
                "bio": user.profile.bio
            },
            "permissions": user._permissions,
            "created_at": user._created_at.isoformat(),
            "last_updated": user._updated_at.isoformat() if hasattr(user, '_updated_at') else None
        }
    
    def validate_user_data(
        self,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Validate user data and return validation errors"""
        errors = {
            "username": [],
            "email": [],
            "password": []
        }
        
        if username is not None:
            if not username or len(username) < 3:
                errors["username"].append("Username must be at least 3 characters")
            elif self.user_repository.get_by_username(username):
                errors["username"].append("Username already exists")
        
        if email is not None:
            if not email or not User.EMAIL_REGEX.match(email):
                errors["email"].append("Invalid email format")
            elif self.user_repository.get_by_email(email):
                errors["email"].append("Email already exists")
        
        if password is not None:
            if not password or len(password) < 6:
                errors["password"].append("Password must be at least 6 characters")
        
        # Remove empty error lists
        return {k: v for k, v in errors.items() if v}
