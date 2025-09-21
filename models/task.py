from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import uuid


class TaskStatus(Enum):
    """Task status enumeration"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority enumeration"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskComment:
    """Task comment data structure"""
    id: str
    author_id: str
    content: str
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "author_id": self.author_id,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }


class Task:
    """
    Clean and elegant Task model with proper encapsulation
    """
    
    def __init__(
        self,
        title: str,
        description: str = "",
        assignee_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None
    ):
        self._id = str(uuid.uuid4())
        self._title = self._validate_title(title)
        self._description = description
        self._status = TaskStatus.TODO
        self._priority = priority
        self._assignee_id = assignee_id
        self._due_date = due_date
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._comments: List[TaskComment] = []
        self._tags: List[str] = []
    
    # Properties with validation
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        self._title = self._validate_title(value)
        self._updated_at = datetime.utcnow()
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        self._description = value
        self._updated_at = datetime.utcnow()
    
    @property
    def status(self) -> TaskStatus:
        return self._status
    
    @property
    def priority(self) -> TaskPriority:
        return self._priority
    
    @priority.setter
    def priority(self, value: TaskPriority) -> None:
        self._priority = value
        self._updated_at = datetime.utcnow()
    
    @property
    def assignee_id(self) -> Optional[str]:
        return self._assignee_id
    
    @assignee_id.setter
    def assignee_id(self, value: Optional[str]) -> None:
        self._assignee_id = value
        self._updated_at = datetime.utcnow()
    
    @property
    def due_date(self) -> Optional[datetime]:
        return self._due_date
    
    @due_date.setter
    def due_date(self, value: Optional[datetime]) -> None:
        self._due_date = value
        self._updated_at = datetime.utcnow()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def comments(self) -> List[TaskComment]:
        return self._comments.copy()
    
    @property
    def tags(self) -> List[str]:
        return self._tags.copy()
    
    # Business logic methods
    def _validate_title(self, title: str) -> str:
        """Validate and clean task title"""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        return title.strip()
    
    def update_status(self, new_status: TaskStatus) -> None:
        """Update task status with validation"""
        if self._status == TaskStatus.DONE and new_status != TaskStatus.DONE:
            raise ValueError("Cannot change status of completed task")
        
        self._status = new_status
        self._updated_at = datetime.utcnow()
    
    def add_comment(self, author_id: str, content: str) -> TaskComment:
        """Add a comment to the task"""
        if not content.strip():
            raise ValueError("Comment content cannot be empty")
        
        comment = TaskComment(
            id=str(uuid.uuid4()),
            author_id=author_id,
            content=content.strip(),
            created_at=datetime.utcnow()
        )
        self._comments.append(comment)
        self._updated_at = datetime.utcnow()
        return comment
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the task"""
        tag = tag.strip().lower()
        if tag and tag not in self._tags:
            self._tags.append(tag)
            self._updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the task"""
        tag = tag.strip().lower()
        if tag in self._tags:
            self._tags.remove(tag)
            self._updated_at = datetime.utcnow()
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self._due_date or self._status == TaskStatus.DONE:
            return False
        return datetime.utcnow() > self._due_date
    
    def is_urgent(self) -> bool:
        """Check if task is urgent based on priority and due date"""
        if self._priority == TaskPriority.URGENT:
            return True
        
        if self._due_date:
            days_until_due = (self._due_date - datetime.utcnow()).days
            return days_until_due <= 1 and self._priority in [TaskPriority.HIGH, TaskPriority.URGENT]
        
        return False
    
    def get_progress_percentage(self) -> int:
        """Get task progress as percentage"""
        status_progress = {
            TaskStatus.TODO: 0,
            TaskStatus.IN_PROGRESS: 50,
            TaskStatus.REVIEW: 75,
            TaskStatus.DONE: 100,
            TaskStatus.CANCELLED: 0
        }
        return status_progress.get(self._status, 0)
    
    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "status": self._status.value,
            "priority": self._priority.value,
            "assignee_id": self._assignee_id,
            "due_date": self._due_date.isoformat() if self._due_date else None,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "comments": [comment.to_dict() for comment in self._comments],
            "tags": self._tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            assignee_id=data.get("assignee_id"),
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None
        )
        
        task._id = data["id"]
        task._status = TaskStatus(data["status"])
        task._created_at = datetime.fromisoformat(data["created_at"])
        task._updated_at = datetime.fromisoformat(data["updated_at"])
        task._tags = data.get("tags", [])
        
        # Restore comments
        for comment_data in data.get("comments", []):
            comment = TaskComment(
                id=comment_data["id"],
                author_id=comment_data["author_id"],
                content=comment_data["content"],
                created_at=datetime.fromisoformat(comment_data["created_at"])
            )
            task._comments.append(comment)
        
        return task
    
    # Magic methods
    def __str__(self) -> str:
        return f"Task({self._title}, {self._status.value})"
    
    def __repr__(self) -> str:
        return f"Task(id='{self._id}', title='{self._title}', status='{self._status.value}')"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Task) and self._id == other._id
