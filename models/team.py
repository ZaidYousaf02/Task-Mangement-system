from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

from .user import User, UserRole


class TeamRole(Enum):
    """Team role enumeration"""
    LEADER = "leader"
    MEMBER = "member"
    CONTRIBUTOR = "contributor"


@dataclass
class TeamMember:
    """Team member data structure"""
    user_id: str
    role: TeamRole
    joined_at: datetime
    permissions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat(),
            "permissions": self.permissions
        }


class Team:
    """
    Clean and elegant Team model with proper encapsulation
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        leader_id: Optional[str] = None
    ):
        self._id = str(uuid.uuid4())
        self._name = self._validate_name(name)
        self._description = description
        self._leader_id = leader_id
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._members: List[TeamMember] = []
        self._projects: List[str] = []  # Project IDs
    
    # Properties with validation
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = self._validate_name(value)
        self._updated_at = datetime.utcnow()
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        self._description = value
        self._updated_at = datetime.utcnow()
    
    @property
    def leader_id(self) -> Optional[str]:
        return self._leader_id
    
    @leader_id.setter
    def leader_id(self, value: Optional[str]) -> None:
        self._leader_id = value
        self._updated_at = datetime.utcnow()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def members(self) -> List[TeamMember]:
        return self._members.copy()
    
    @property
    def projects(self) -> List[str]:
        return self._projects.copy()
    
    # Business logic methods
    def _validate_name(self, name: str) -> str:
        """Validate and clean team name"""
        if not name or not name.strip():
            raise ValueError("Team name cannot be empty")
        return name.strip()
    
    def _get_default_permissions(self, role: TeamRole) -> List[str]:
        """Get default permissions for team role"""
        permissions = {
            TeamRole.LEADER: [
                "team.manage", "project.create", "project.assign",
                "member.add", "member.remove", "member.promote"
            ],
            TeamRole.MEMBER: [
                "project.view", "task.create", "task.assign",
                "comment.add", "milestone.view"
            ],
            TeamRole.CONTRIBUTOR: [
                "project.view", "task.view", "comment.add"
            ]
        }
        return permissions.get(role, [])
    
    def add_member(
        self,
        user_id: str,
        role: TeamRole = TeamRole.MEMBER
    ) -> TeamMember:
        """Add a member to the team"""
        # Check if user is already a member
        if self.is_member(user_id):
            raise ValueError("User is already a member of this team")
        
        member = TeamMember(
            user_id=user_id,
            role=role,
            joined_at=datetime.utcnow(),
            permissions=self._get_default_permissions(role)
        )
        self._members.append(member)
        self._updated_at = datetime.utcnow()
        return member
    
    def remove_member(self, user_id: str) -> bool:
        """Remove a member from the team"""
        for i, member in enumerate(self._members):
            if member.user_id == user_id:
                # Cannot remove the team leader
                if user_id == self._leader_id:
                    raise ValueError("Cannot remove team leader")
                self._members.pop(i)
                self._updated_at = datetime.utcnow()
                return True
        return False
    
    def promote_member(self, user_id: str, new_role: TeamRole) -> bool:
        """Promote a member to a new role"""
        for member in self._members:
            if member.user_id == user_id:
                member.role = new_role
                member.permissions = self._get_default_permissions(new_role)
                self._updated_at = datetime.utcnow()
                return True
        return False
    
    def is_member(self, user_id: str) -> bool:
        """Check if user is a member of the team"""
        return any(member.user_id == user_id for member in self._members)
    
    def get_member_role(self, user_id: str) -> Optional[TeamRole]:
        """Get the role of a team member"""
        for member in self._members:
            if member.user_id == user_id:
                return member.role
        return None
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission in the team"""
        for member in self._members:
            if member.user_id == user_id:
                return permission in member.permissions
        return False
    
    def add_project(self, project_id: str) -> None:
        """Add a project to the team"""
        if project_id not in self._projects:
            self._projects.append(project_id)
            self._updated_at = datetime.utcnow()
    
    def remove_project(self, project_id: str) -> None:
        """Remove a project from the team"""
        if project_id in self._projects:
            self._projects.remove(project_id)
            self._updated_at = datetime.utcnow()
    
    def get_member_count(self) -> int:
        """Get total number of team members"""
        return len(self._members)
    
    def get_leaders(self) -> List[TeamMember]:
        """Get all team leaders"""
        return [member for member in self._members if member.role == TeamRole.LEADER]
    
    def get_members_by_role(self, role: TeamRole) -> List[TeamMember]:
        """Get all members with specific role"""
        return [member for member in self._members if member.role == role]
    
    def get_team_statistics(self) -> Dict[str, Any]:
        """Get team statistics"""
        role_counts = {}
        for role in TeamRole:
            role_counts[role.value] = len(self.get_members_by_role(role))
        
        return {
            "total_members": self.get_member_count(),
            "total_projects": len(self._projects),
            "role_distribution": role_counts,
            "created_at": self._created_at.isoformat(),
            "last_updated": self._updated_at.isoformat()
        }
    
    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        """Convert team to dictionary"""
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "leader_id": self._leader_id,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "members": [member.to_dict() for member in self._members],
            "projects": self._projects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Team':
        """Create team from dictionary"""
        team = cls(
            name=data["name"],
            description=data.get("description", ""),
            leader_id=data.get("leader_id")
        )
        
        team._id = data["id"]
        team._created_at = datetime.fromisoformat(data["created_at"])
        team._updated_at = datetime.fromisoformat(data["updated_at"])
        team._projects = data.get("projects", [])
        
        # Restore members
        for member_data in data.get("members", []):
            member = TeamMember(
                user_id=member_data["user_id"],
                role=TeamRole(member_data["role"]),
                joined_at=datetime.fromisoformat(member_data["joined_at"]),
                permissions=member_data.get("permissions", [])
            )
            team._members.append(member)
        
        return team
    
    # Magic methods
    def __str__(self) -> str:
        return f"Team({self._name}, {self.get_member_count()} members)"
    
    def __repr__(self) -> str:
        return f"Team(id='{self._id}', name='{self._name}', members={self.get_member_count()})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Team) and self._id == other._id
