"""
Team Service - Business logic for team management
"""

from typing import List, Optional, Dict, Any

from models.team import Team, TeamRole, TeamMember
from models.user import User


class TeamService:
    """
    Service class for team-related business logic
    Clean separation of concerns with proper validation
    """
    
    def __init__(self, team_repository, user_repository):
        self.team_repository = team_repository
        self.user_repository = user_repository
    
    def create_team(
        self,
        name: str,
        description: str = "",
        leader_id: Optional[str] = None
    ) -> Team:
        """Create a new team with validation"""
        # Validate leader exists if provided
        if leader_id and not self.user_repository.get_by_id(leader_id):
            raise ValueError(f"Leader with ID {leader_id} not found")
        
        team = Team(
            name=name,
            description=description,
            leader_id=leader_id
        )
        
        # Add leader as team member if provided
        if leader_id:
            team.add_member(leader_id, TeamRole.LEADER)
        
        return self.team_repository.save(team)
    
    def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID"""
        return self.team_repository.get_by_id(team_id)
    
    def add_team_member(
        self,
        team_id: str,
        user_id: str,
        role: TeamRole = TeamRole.MEMBER,
        adder_id: str
    ) -> TeamMember:
        """Add a member to a team"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        if not self._can_manage_team(adder_id, team):
            raise PermissionError("User does not have permission to manage this team")
        
        member = team.add_member(user_id, role)
        self.team_repository.save(team)
        return member
    
    def remove_team_member(
        self,
        team_id: str,
        user_id: str,
        remover_id: str
    ) -> bool:
        """Remove a member from a team"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        if not self._can_manage_team(remover_id, team):
            raise PermissionError("User does not have permission to manage this team")
        
        success = team.remove_member(user_id)
        if success:
            self.team_repository.save(team)
        return success
    
    def promote_team_member(
        self,
        team_id: str,
        user_id: str,
        new_role: TeamRole,
        promoter_id: str
    ) -> bool:
        """Promote a team member to a new role"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        if not self._can_manage_team(promoter_id, team):
            raise PermissionError("User does not have permission to manage this team")
        
        success = team.promote_member(user_id, new_role)
        if success:
            self.team_repository.save(team)
        return success
    
    def change_team_leader(
        self,
        team_id: str,
        new_leader_id: str,
        changer_id: str
    ) -> Team:
        """Change the team leader"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        new_leader = self.user_repository.get_by_id(new_leader_id)
        if not new_leader:
            raise ValueError(f"New leader with ID {new_leader_id} not found")
        
        if not self._can_manage_team(changer_id, team):
            raise PermissionError("User does not have permission to manage this team")
        
        # Ensure new leader is a team member
        if not team.is_member(new_leader_id):
            team.add_member(new_leader_id, TeamRole.LEADER)
        else:
            team.promote_member(new_leader_id, TeamRole.LEADER)
        
        team.leader_id = new_leader_id
        return self.team_repository.save(team)
    
    def add_project_to_team(
        self,
        team_id: str,
        project_id: str,
        adder_id: str
    ) -> Team:
        """Add a project to a team"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        if not self._can_manage_team(adder_id, team):
            raise PermissionError("User does not have permission to manage this team")
        
        team.add_project(project_id)
        return self.team_repository.save(team)
    
    def remove_project_from_team(
        self,
        team_id: str,
        project_id: str,
        remover_id: str
    ) -> Team:
        """Remove a project from a team"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        if not self._can_manage_team(remover_id, team):
            raise PermissionError("User does not have permission to manage this team")
        
        team.remove_project(project_id)
        return self.team_repository.save(team)
    
    def get_user_teams(self, user_id: str) -> List[Team]:
        """Get all teams a user belongs to"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        all_teams = self.team_repository.get_all()
        user_teams = []
        
        for team in all_teams:
            if team.is_member(user_id):
                user_teams.append(team)
        
        return user_teams
    
    def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        return team.members
    
    def get_team_member_role(self, team_id: str, user_id: str) -> Optional[TeamRole]:
        """Get the role of a user in a team"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        return team.get_member_role(user_id)
    
    def check_team_permission(
        self,
        team_id: str,
        user_id: str,
        permission: str
    ) -> bool:
        """Check if user has specific permission in team"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        return team.has_permission(user_id, permission)
    
    def get_team_statistics(self, team_id: str) -> Dict[str, Any]:
        """Get detailed team statistics"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        return team.get_team_statistics()
    
    def search_teams(
        self,
        query: str,
        leader_id: Optional[str] = None
    ) -> List[Team]:
        """Search teams with filters"""
        all_teams = self.team_repository.get_all()
        filtered_teams = []
        
        query_lower = query.lower()
        
        for team in all_teams:
            # Text search
            if query_lower not in team.name.lower() and query_lower not in team.description.lower():
                continue
            
            # Leader filter
            if leader_id and team.leader_id != leader_id:
                continue
            
            filtered_teams.append(team)
        
        return filtered_teams
    
    def get_team_performance_metrics(self, team_id: str) -> Dict[str, Any]:
        """Get team performance metrics"""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        # This would typically integrate with project and task services
        # For now, return basic team metrics
        return {
            "team_id": team_id,
            "name": team.name,
            "member_count": team.get_member_count(),
            "project_count": len(team.projects),
            "role_distribution": {
                role.value: len(team.get_members_by_role(role))
                for role in TeamRole
            },
            "created_at": team.created_at.isoformat(),
            "last_updated": team.updated_at.isoformat()
        }
    
    def _can_manage_team(self, user_id: str, team: Team) -> bool:
        """Check if user can manage a team"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        # Admin can manage any team
        if user.is_admin:
            return True
        
        # Team leader can manage their team
        if team.leader_id == user_id:
            return True
        
        # Check if user is a team leader
        user_role = team.get_member_role(user_id)
        if user_role == TeamRole.LEADER:
            return True
        
        return False
