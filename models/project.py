from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

from .task import Task, TaskStatus


class ProjectStatus(Enum):
    """Project status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ProjectMilestone:
    """Project milestone data structure"""
    id: str
    title: str
    description: str
    due_date: datetime
    completed: bool = False
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat(),
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class Project:
    """
    Clean and elegant Project model with proper encapsulation
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        owner_id: Optional[str] = None
    ):
        self._id = str(uuid.uuid4())
        self._name = self._validate_name(name)
        self._description = description
        self._status = ProjectStatus.PLANNING
        self._owner_id = owner_id
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._tasks: List[Task] = []
        self._milestones: List[ProjectMilestone] = []
        self._team_members: List[str] = []
    
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
    def status(self) -> ProjectStatus:
        return self._status
    
    @property
    def owner_id(self) -> Optional[str]:
        return self._owner_id
    
    @owner_id.setter
    def owner_id(self, value: Optional[str]) -> None:
        self._owner_id = value
        self._updated_at = datetime.utcnow()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def tasks(self) -> List[Task]:
        return self._tasks.copy()
    
    @property
    def milestones(self) -> List[ProjectMilestone]:
        return self._milestones.copy()
    
    @property
    def team_members(self) -> List[str]:
        return self._team_members.copy()
    
    # Business logic methods
    def _validate_name(self, name: str) -> str:
        """Validate and clean project name"""
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")
        return name.strip()
    
    def update_status(self, new_status: ProjectStatus) -> None:
        """Update project status"""
        self._status = new_status
        self._updated_at = datetime.utcnow()
    
    def add_task(self, task: Task) -> None:
        """Add a task to the project"""
        if task not in self._tasks:
            self._tasks.append(task)
            self._updated_at = datetime.utcnow()
    
    def remove_task(self, task: Task) -> None:
        """Remove a task from the project"""
        if task in self._tasks:
            self._tasks.remove(task)
            self._updated_at = datetime.utcnow()
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with specific status"""
        return [task for task in self._tasks if task.status == status]
    
    def add_milestone(
        self,
        title: str,
        description: str,
        due_date: datetime
    ) -> ProjectMilestone:
        """Add a milestone to the project"""
        milestone = ProjectMilestone(
            id=str(uuid.uuid4()),
            title=title.strip(),
            description=description.strip(),
            due_date=due_date
        )
        self._milestones.append(milestone)
        self._updated_at = datetime.utcnow()
        return milestone
    
    def complete_milestone(self, milestone_id: str) -> bool:
        """Mark a milestone as completed"""
        for milestone in self._milestones:
            if milestone.id == milestone_id:
                milestone.completed = True
                milestone.completed_at = datetime.utcnow()
                self._updated_at = datetime.utcnow()
                return True
        return False
    
    def add_team_member(self, user_id: str) -> None:
        """Add a team member to the project"""
        if user_id not in self._team_members:
            self._team_members.append(user_id)
            self._updated_at = datetime.utcnow()
    
    def remove_team_member(self, user_id: str) -> None:
        """Remove a team member from the project"""
        if user_id in self._team_members:
            self._team_members.remove(user_id)
            self._updated_at = datetime.utcnow()
    
    def get_progress_percentage(self) -> int:
        """Calculate project progress based on completed tasks"""
        if not self._tasks:
            return 0
        
        completed_tasks = len(self.get_tasks_by_status(TaskStatus.DONE))
        return int((completed_tasks / len(self._tasks)) * 100)
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks in the project"""
        return [task for task in self._tasks if task.is_overdue()]
    
    def get_urgent_tasks(self) -> List[Task]:
        """Get all urgent tasks in the project"""
        return [task for task in self._tasks if task.is_urgent()]
    
    def get_task_statistics(self) -> Dict[str, int]:
        """Get task statistics for the project"""
        stats = {
            "total": len(self._tasks),
            "todo": len(self.get_tasks_by_status(TaskStatus.TODO)),
            "in_progress": len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS)),
            "review": len(self.get_tasks_by_status(TaskStatus.REVIEW)),
            "done": len(self.get_tasks_by_status(TaskStatus.DONE)),
            "cancelled": len(self.get_tasks_by_status(TaskStatus.CANCELLED)),
            "overdue": len(self.get_overdue_tasks()),
            "urgent": len(self.get_urgent_tasks())
        }
        return stats
    
    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary"""
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "status": self._status.value,
            "owner_id": self._owner_id,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "tasks": [task.to_dict() for task in self._tasks],
            "milestones": [milestone.to_dict() for milestone in self._milestones],
            "team_members": self._team_members
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create project from dictionary"""
        project = cls(
            name=data["name"],
            description=data.get("description", ""),
            owner_id=data.get("owner_id")
        )
        
        project._id = data["id"]
        project._status = ProjectStatus(data["status"])
        project._created_at = datetime.fromisoformat(data["created_at"])
        project._updated_at = datetime.fromisoformat(data["updated_at"])
        project._team_members = data.get("team_members", [])
        
        # Restore tasks
        for task_data in data.get("tasks", []):
            task = Task.from_dict(task_data)
            project._tasks.append(task)
        
        # Restore milestones
        for milestone_data in data.get("milestones", []):
            milestone = ProjectMilestone(
                id=milestone_data["id"],
                title=milestone_data["title"],
                description=milestone_data["description"],
                due_date=datetime.fromisoformat(milestone_data["due_date"]),
                completed=milestone_data.get("completed", False),
                completed_at=datetime.fromisoformat(milestone_data["completed_at"]) if milestone_data.get("completed_at") else None
            )
            project._milestones.append(milestone)
        
        return project
    
    # Magic methods
    def __str__(self) -> str:
        return f"Project({self._name}, {self._status.value})"
    
    def __repr__(self) -> str:
        return f"Project(id='{self._id}', name='{self._name}', status='{self._status.value}')"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Project) and self._id == other._id
