"""
Project Service - Business logic for project management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from models.project import Project, ProjectStatus, ProjectMilestone
from models.task import Task, TaskStatus
from models.user import User


class ProjectService:
    """
    Service class for project-related business logic
    Clean separation of concerns with proper validation
    """
    
    def __init__(self, project_repository, task_repository, user_repository):
        self.project_repository = project_repository
        self.task_repository = task_repository
        self.user_repository = user_repository
    
    def create_project(
        self,
        name: str,
        description: str = "",
        owner_id: Optional[str] = None
    ) -> Project:
        """Create a new project with validation"""
        # Validate owner exists if provided
        if owner_id and not self.user_repository.get_by_id(owner_id):
            raise ValueError(f"Owner with ID {owner_id} not found")
        
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id
        )
        
        return self.project_repository.save(project)
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID"""
        return self.project_repository.get_by_id(project_id)
    
    def update_project_status(
        self,
        project_id: str,
        new_status: ProjectStatus,
        user_id: str
    ) -> Project:
        """Update project status with permission checking"""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        if not self._can_modify_project(user_id, project):
            raise PermissionError("User does not have permission to modify this project")
        
        project.update_status(new_status)
        return self.project_repository.save(project)
    
    def add_task_to_project(
        self,
        project_id: str,
        task: Task,
        user_id: str
    ) -> Project:
        """Add a task to a project"""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        if not self._can_modify_project(user_id, project):
            raise PermissionError("User does not have permission to modify this project")
        
        project.add_task(task)
        return self.project_repository.save(project)
    
    def remove_task_from_project(
        self,
        project_id: str,
        task: Task,
        user_id: str
    ) -> Project:
        """Remove a task from a project"""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        if not self._can_modify_project(user_id, project):
            raise PermissionError("User does not have permission to modify this project")
        
        project.remove_task(task)
        return self.project_repository.save(project)
    
    def add_milestone(
        self,
        project_id: str,
        title: str,
        description: str,
        due_date: datetime,
        user_id: str
    ) -> ProjectMilestone:
        """Add a milestone to a project"""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        if not self._can_modify_project(user_id, project):
            raise PermissionError("User does not have permission to modify this project")
        
        milestone = project.add_milestone(title, description, due_date)
        self.project_repository.save(project)
        return milestone
    
    def complete_milestone(
        self,
        project_id: str,
        milestone_id: str,
        user_id: str
    ) -> bool:
        """Complete a project milestone"""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        if not self._can_modify_project(user_id, project):
            raise PermissionError("User does not have permission to modify this project")
        
        success = project.complete_milestone(milestone_id)
        if success:
            self.project_repository.save(project)
        return success
    
    def add_team_member(
        self,
        project_id: str,
        user_id: str,
        adder_id: str
    ) -> Project:
        """Add a team member to a project"""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        if not self._can_modify_project(adder_id, project):
            raise PermissionError("User does not have permission to modify this project")
        
        project.add_team_member(user_id)
        return self.project_repository.save(project)
    
    def remove_team_member(
        self,
        project_id: str,
        user_id: str,
        remover_id: str
    ) -> Project:
        """Remove a team member from a project"""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        if not self._can_modify_project(remover_id, project):
            raise PermissionError("User does not have permission to modify this project")
        
        project.remove_team_member(user_id)
        return self.project_repository.save(project)
    
    def get_user_projects(
        self,
        user_id: str,
        status: Optional[ProjectStatus] = None
    ) -> List[Project]:
        """Get projects for a specific user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        all_projects = self.project_repository.get_all()
        user_projects = []
        
        for project in all_projects:
            # Check if user is owner or team member
            if (project.owner_id == user_id or 
                user_id in project.team_members):
                if status is None or project.status == status:
                    user_projects.append(project)
        
        return user_projects
    
    def get_project_tasks(
        self,
        project_id: str,
        status: Optional[TaskStatus] = None
    ) -> List[Task]:
        """Get all tasks in a project"""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        if status:
            return project.get_tasks_by_status(status)
        return project.tasks
    
    def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """Get detailed project progress information"""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        return {
            "project_id": project_id,
            "name": project.name,
            "status": project.status.value,
            "progress_percentage": project.get_progress_percentage(),
            "task_statistics": project.get_task_statistics(),
            "overdue_tasks": len(project.get_overdue_tasks()),
            "urgent_tasks": len(project.get_urgent_tasks()),
            "milestones": {
                "total": len(project.milestones),
                "completed": len([m for m in project.milestones if m.completed]),
                "pending": len([m for m in project.milestones if not m.completed])
            },
            "team_size": len(project.team_members)
        }
    
    def search_projects(
        self,
        query: str,
        status: Optional[ProjectStatus] = None,
        owner_id: Optional[str] = None
    ) -> List[Project]:
        """Search projects with filters"""
        all_projects = self.project_repository.get_all()
        filtered_projects = []
        
        query_lower = query.lower()
        
        for project in all_projects:
            # Text search
            if query_lower not in project.name.lower() and query_lower not in project.description.lower():
                continue
            
            # Status filter
            if status and project.status != status:
                continue
            
            # Owner filter
            if owner_id and project.owner_id != owner_id:
                continue
            
            filtered_projects.append(project)
        
        return filtered_projects
    
    def get_project_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get project statistics"""
        all_projects = self.project_repository.get_all()
        
        if user_id:
            all_projects = self.get_user_projects(user_id)
        
        stats = {
            "total": len(all_projects),
            "by_status": {},
            "total_tasks": 0,
            "total_milestones": 0,
            "overdue_projects": 0
        }
        
        # Count by status
        for status in ProjectStatus:
            count = len([p for p in all_projects if p.status == status])
            stats["by_status"][status.value] = count
        
        # Calculate totals
        for project in all_projects:
            stats["total_tasks"] += len(project.tasks)
            stats["total_milestones"] += len(project.milestones)
            if project.get_overdue_tasks():
                stats["overdue_projects"] += 1
        
        return stats
    
    def _can_modify_project(self, user_id: str, project: Project) -> bool:
        """Check if user can modify a project"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        # Admin can modify any project
        if user.is_admin:
            return True
        
        # Project owner can modify their projects
        if project.owner_id == user_id:
            return True
        
        # Team members can modify projects (could be restricted further)
        if user_id in project.team_members:
            return True
        
        return False
