"""
Task Repository - Data access for Task entities
"""

from typing import List, Optional
from datetime import datetime
from .base_repository import BaseRepository
from models.task import Task, TaskStatus, TaskPriority


class TaskRepository(BaseRepository[Task]):
    """
    Repository for Task entities with in-memory storage
    Implements the repository pattern for clean data access
    """
    
    def save(self, task: Task) -> Task:
        """Save a task to the repository"""
        if not task.id:
            task.id = self._generate_id()
        
        self._data[task.id] = task
        return task
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self._data.get(task_id)
    
    def get_all(self) -> List[Task]:
        """Get all tasks"""
        return list(self._data.values())
    
    def delete(self, task_id: str) -> bool:
        """Delete a task by ID"""
        if task_id in self._data:
            del self._data[task_id]
            return True
        return False
    
    def get_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status"""
        return [task for task in self._data.values() if task.status == status]
    
    def get_by_priority(self, priority: TaskPriority) -> List[Task]:
        """Get all tasks with a specific priority"""
        return [task for task in self._data.values() if task.priority == priority]
    
    def get_by_assignee(self, assignee_id: str) -> List[Task]:
        """Get all tasks assigned to a specific user"""
        return [task for task in self._data.values() if task.assignee_id == assignee_id]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks"""
        return [task for task in self._data.values() if task.is_overdue()]
    
    def get_urgent_tasks(self) -> List[Task]:
        """Get all urgent tasks"""
        return [task for task in self._data.values() if task.is_urgent()]
    
    def get_tasks_due_before(self, due_date: datetime) -> List[Task]:
        """Get all tasks due before a specific date"""
        return [
            task for task in self._data.values()
            if task.due_date and task.due_date <= due_date
        ]
    
    def get_tasks_created_after(self, created_date: datetime) -> List[Task]:
        """Get all tasks created after a specific date"""
        return [
            task for task in self._data.values()
            if task.created_at >= created_date
        ]
    
    def search_by_title(self, title_query: str) -> List[Task]:
        """Search tasks by title"""
        query_lower = title_query.lower()
        return [
            task for task in self._data.values()
            if query_lower in task.title.lower()
        ]
    
    def search_by_description(self, description_query: str) -> List[Task]:
        """Search tasks by description"""
        query_lower = description_query.lower()
        return [
            task for task in self._data.values()
            if query_lower in task.description.lower()
        ]
    
    def get_tasks_with_tag(self, tag: str) -> List[Task]:
        """Get all tasks with a specific tag"""
        tag_lower = tag.lower()
        return [
            task for task in self._data.values()
            if tag_lower in [t.lower() for t in task.tags]
        ]
    
    def get_task_statistics(self) -> dict:
        """Get task statistics"""
        all_tasks = self.get_all()
        
        stats = {
            "total": len(all_tasks),
            "by_status": {},
            "by_priority": {},
            "overdue": len(self.get_overdue_tasks()),
            "urgent": len(self.get_urgent_tasks())
        }
        
        # Count by status
        for status in TaskStatus:
            stats["by_status"][status.value] = len(self.get_by_status(status))
        
        # Count by priority
        for priority in TaskPriority:
            stats["by_priority"][priority.name] = len(self.get_by_priority(priority))
        
        return stats
