"""
Team Repository - Data access for Team entities
"""

from typing import List, Optional
from datetime import datetime
from .base_repository import BaseRepository
from models.team import Team, TeamRole


class TeamRepository(BaseRepository[Team]):
    """
    Repository for Team entities with in-memory storage
    Implements the repository pattern for clean data access
    """
    
    def save(self, team: Team) -> Team:
        """Save a team to the repository"""
        if not team.id:
            team.id = self._generate_id()
        
        self._data[team.id] = team
        return team
    
    def get_by_id(self, team_id: str) -> Optional[Team]:
        """Get a team by ID"""
        return self._data.get(team_id)
    
    def get_all(self) -> List[Team]:
        """Get all teams"""
        return list(self._data.values())
    
    def delete(self, team_id: str) -> bool:
        """Delete a team by ID"""
        if team_id in self._data:
            del self._data[team_id]
            return True
        return False
    
    def get_by_leader(self, leader_id: str) -> List[Team]:
        """Get all teams led by a specific user"""
        return [team for team in self._data.values() if team.leader_id == leader_id]
    
    def get_by_member(self, user_id: str) -> List[Team]:
        """Get all teams where a user is a member"""
        return [
            team for team in self._data.values()
            if team.is_member(user_id)
        ]
    
    def get_user_teams(self, user_id: str) -> List[Team]:
        """Get all teams for a user (led or member)"""
        return [
            team for team in self._data.values()
            if team.leader_id == user_id or team.is_member(user_id)
        ]
    
    def get_teams_with_project(self, project_id: str) -> List[Team]:
        """Get all teams that have a specific project"""
        return [
            team for team in self._data.values()
            if project_id in team.projects
        ]
    
    def get_teams_created_after(self, created_date: datetime) -> List[Team]:
        """Get all teams created after a specific date"""
        return [
            team for team in self._data.values()
            if team.created_at >= created_date
        ]
    
    def search_by_name(self, name_query: str) -> List[Team]:
        """Search teams by name"""
        query_lower = name_query.lower()
        return [
            team for team in self._data.values()
            if query_lower in team.name.lower()
        ]
    
    def search_by_description(self, description_query: str) -> List[Team]:
        """Search teams by description"""
        query_lower = description_query.lower()
        return [
            team for team in self._data.values()
            if query_lower in team.description.lower()
        ]
    
    def get_teams_by_size(self, min_size: int = 0, max_size: int = None) -> List[Team]:
        """Get teams by member count"""
        teams = []
        for team in self._data.values():
            member_count = team.get_member_count()
            if member_count >= min_size:
                if max_size is None or member_count <= max_size:
                    teams.append(team)
        return teams
    
    def get_teams_with_role(self, role: TeamRole) -> List[Team]:
        """Get all teams that have members with a specific role"""
        return [
            team for team in self._data.values()
            if team.get_members_by_role(role)
        ]
    
    def get_team_statistics(self) -> dict:
        """Get team statistics"""
        all_teams = self.get_all()
        
        stats = {
            "total": len(all_teams),
            "total_members": 0,
            "total_projects": 0,
            "average_team_size": 0,
            "largest_team_size": 0,
            "smallest_team_size": float('inf') if all_teams else 0
        }
        
        if all_teams:
            team_sizes = []
            for team in all_teams:
                member_count = team.get_member_count()
                team_sizes.append(member_count)
                stats["total_members"] += member_count
                stats["total_projects"] += len(team.projects)
                stats["largest_team_size"] = max(stats["largest_team_size"], member_count)
                stats["smallest_team_size"] = min(stats["smallest_team_size"], member_count)
            
            stats["average_team_size"] = sum(team_sizes) / len(team_sizes)
        
        if stats["smallest_team_size"] == float('inf'):
            stats["smallest_team_size"] = 0
        
        return stats
