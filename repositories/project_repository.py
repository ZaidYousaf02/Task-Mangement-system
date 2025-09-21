"""
Project Repository - Data access for Project entities
"""

from typing import List, Optional
from datetime import datetime
from .base_repository import BaseRepository
from models.project import Project, ProjectStatus


class ProjectRepository(BaseRepository[Project]):
    """
    Repository for Project entities with in-memory storage
    Implements the repository pattern for clean data access
    """
    
    def save(self, project: Project) -> Project:
        """Save a project to the repository"""
        if not project.id:
            project.id = self._generate_id()
        
        self._data[project.id] = project
        return project
    
    def get_by_id(self, project_id: str) -> Optional[Project]:
        """Get a project by ID"""
        return self._data.get(project_id)
    
    def get_all(self) -> List[Project]:
        """Get all projects"""
        return list(self._data.values())
    
    def delete(self, project_id: str) -> bool:
        """Delete a project by ID"""
        if project_id in self._data:
            del self._data[project_id]
            return True
        return False
    
    def get_by_status(self, status: ProjectStatus) -> List[Project]:
        """Get all projects with a specific status"""
        return [project for project in self._data.values() if project.status == status]
    
    def get_by_owner(self, owner_id: str) -> List[Project]:
        """Get all projects owned by a specific user"""
        return [project for project in self._data.values() if project.owner_id == owner_id]
    
    def get_by_team_member(self, user_id: str) -> List[Project]:
        """Get all projects where a user is a team member"""
        return [
            project for project in self._data.values()
            if user_id in project.team_members
        ]
    
    def get_user_projects(self, user_id: str) -> List[Project]:
        """Get all projects for a user (owned or team member)"""
        return [
            project for project in self._data.values()
            if project.owner_id == user_id or user_id in project.team_members
        ]
    
    def get_projects_created_after(self, created_date: datetime) -> List[Project]:
        """Get all projects created after a specific date"""
        return [
            project for project in self._data.values()
            if project.created_at >= created_date
        ]
    
    def search_by_name(self, name_query: str) -> List[Project]:
        """Search projects by name"""
        query_lower = name_query.lower()
        return [
            project for project in self._data.values()
            if query_lower in project.name.lower()
        ]
    
    def search_by_description(self, description_query: str) -> List[Project]:
        """Search projects by description"""
        query_lower = description_query.lower()
        return [
            project for project in self._data.values()
            if query_lower in project.description.lower()
        ]
    
    def get_active_projects(self) -> List[Project]:
        """Get all active projects"""
        return self.get_by_status(ProjectStatus.ACTIVE)
    
    def get_completed_projects(self) -> List[Project]:
        """Get all completed projects"""
        return self.get_by_status(ProjectStatus.COMPLETED)
    
    def get_projects_with_overdue_tasks(self) -> List[Project]:
        """Get all projects that have overdue tasks"""
        return [
            project for project in self._data.values()
            if project.get_overdue_tasks()
        ]
    
    def get_projects_with_urgent_tasks(self) -> List[Project]:
        """Get all projects that have urgent tasks"""
        return [
            project for project in self._data.values()
            if project.get_urgent_tasks()
        ]
    
    def get_project_statistics(self) -> dict:
        """Get project statistics"""
        all_projects = self.get_all()
        
        stats = {
            "total": len(all_projects),
            "by_status": {},
            "total_tasks": 0,
            "total_milestones": 0,
            "projects_with_overdue_tasks": len(self.get_projects_with_overdue_tasks()),
            "projects_with_urgent_tasks": len(self.get_projects_with_urgent_tasks())
        }
        
        # Count by status
        for status in ProjectStatus:
            stats["by_status"][status.value] = len(self.get_by_status(status))
        
        # Calculate totals
        for project in all_projects:
            stats["total_tasks"] += len(project.tasks)
            stats["total_milestones"] += len(project.milestones)
        
        return stats
