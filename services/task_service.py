"""
Task Service - Business logic for task management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from models.task import Task, TaskStatus, TaskPriority
from models.user import User


class TaskService:
    """
    Service class for task-related business logic
    Clean separation of concerns with proper error handling
    """
    
    def __init__(self, task_repository, user_repository):
        self.task_repository = task_repository
        self.user_repository = user_repository
    
    def create_task(
        self,
        title: str,
        description: str = "",
        assignee_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        creator_id: Optional[str] = None
    ) -> Task:
        """Create a new task with validation"""
        # Validate assignee exists if provided
        if assignee_id and not self.user_repository.get_by_id(assignee_id):
            raise ValueError(f"Assignee with ID {assignee_id} not found")
        
        # Validate creator exists if provided
        if creator_id and not self.user_repository.get_by_id(creator_id):
            raise ValueError(f"Creator with ID {creator_id} not found")
        
        task = Task(
            title=title,
            description=description,
            assignee_id=assignee_id,
            priority=priority,
            due_date=due_date
        )
        
        return self.task_repository.save(task)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.task_repository.get_by_id(task_id)
    
    def update_task_status(
        self,
        task_id: str,
        new_status: TaskStatus,
        user_id: Optional[str] = None
    ) -> Task:
        """Update task status with permission checking"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Check permissions if user_id provided
        if user_id:
            if not self._can_modify_task(user_id, task):
                raise PermissionError("User does not have permission to modify this task")
        
        task.update_status(new_status)
        return self.task_repository.save(task)
    
    def assign_task(self, task_id: str, assignee_id: str, assigner_id: str) -> Task:
        """Assign a task to a user"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        assignee = self.user_repository.get_by_id(assignee_id)
        if not assignee:
            raise ValueError(f"Assignee with ID {assignee_id} not found")
        
        # Check if assigner has permission
        if not self._can_assign_task(assigner_id, task):
            raise PermissionError("User does not have permission to assign this task")
        
        task.assignee_id = assignee_id
        return self.task_repository.save(task)
    
    def add_task_comment(
        self,
        task_id: str,
        author_id: str,
        content: str
    ) -> Task:
        """Add a comment to a task"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        author = self.user_repository.get_by_id(author_id)
        if not author:
            raise ValueError(f"Author with ID {author_id} not found")
        
        # Check if user can comment on this task
        if not self._can_comment_on_task(author_id, task):
            raise PermissionError("User does not have permission to comment on this task")
        
        task.add_comment(author_id, content)
        return self.task_repository.save(task)
    
    def get_user_tasks(
        self,
        user_id: str,
        status: Optional[TaskStatus] = None,
        include_assigned: bool = True
    ) -> List[Task]:
        """Get tasks for a specific user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        all_tasks = self.task_repository.get_all()
        user_tasks = []
        
        for task in all_tasks:
            # Check if task is assigned to user
            if include_assigned and task.assignee_id == user_id:
                if status is None or task.status == status:
                    user_tasks.append(task)
        
        return user_tasks
    
    def get_overdue_tasks(self, user_id: Optional[str] = None) -> List[Task]:
        """Get overdue tasks, optionally filtered by user"""
        all_tasks = self.task_repository.get_all()
        overdue_tasks = [task for task in all_tasks if task.is_overdue()]
        
        if user_id:
            overdue_tasks = [task for task in overdue_tasks if task.assignee_id == user_id]
        
        return overdue_tasks
    
    def get_urgent_tasks(self, user_id: Optional[str] = None) -> List[Task]:
        """Get urgent tasks, optionally filtered by user"""
        all_tasks = self.task_repository.get_all()
        urgent_tasks = [task for task in all_tasks if task.is_urgent()]
        
        if user_id:
            urgent_tasks = [task for task in urgent_tasks if task.assignee_id == user_id]
        
        return urgent_tasks
    
    def search_tasks(
        self,
        query: str,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assignee_id: Optional[str] = None
    ) -> List[Task]:
        """Search tasks with filters"""
        all_tasks = self.task_repository.get_all()
        filtered_tasks = []
        
        query_lower = query.lower()
        
        for task in all_tasks:
            # Text search
            if query_lower not in task.title.lower() and query_lower not in task.description.lower():
                continue
            
            # Status filter
            if status and task.status != status:
                continue
            
            # Priority filter
            if priority and task.priority != priority:
                continue
            
            # Assignee filter
            if assignee_id and task.assignee_id != assignee_id:
                continue
            
            filtered_tasks.append(task)
        
        return filtered_tasks
    
    def get_task_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get task statistics"""
        all_tasks = self.task_repository.get_all()
        
        if user_id:
            all_tasks = [task for task in all_tasks if task.assignee_id == user_id]
        
        stats = {
            "total": len(all_tasks),
            "by_status": {},
            "by_priority": {},
            "overdue": len([task for task in all_tasks if task.is_overdue()]),
            "urgent": len([task for task in all_tasks if task.is_urgent()])
        }
        
        # Count by status
        for status in TaskStatus:
            stats["by_status"][status.value] = len([
                task for task in all_tasks if task.status == status
            ])
        
        # Count by priority
        for priority in TaskPriority:
            stats["by_priority"][priority.name] = len([
                task for task in all_tasks if task.priority == priority
            ])
        
        return stats
    
    def _can_modify_task(self, user_id: str, task: Task) -> bool:
        """Check if user can modify a task"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        # Admin can modify any task
        if user.is_admin:
            return True
        
        # Task assignee can modify their own tasks
        if task.assignee_id == user_id:
            return True
        
        return False
    
    def _can_assign_task(self, user_id: str, task: Task) -> bool:
        """Check if user can assign a task"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        # Admin can assign any task
        if user.is_admin:
            return True
        
        # For now, only admins can assign tasks
        # This could be extended based on project/team permissions
        return False
    
    def _can_comment_on_task(self, user_id: str, task: Task) -> bool:
        """Check if user can comment on a task"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        # Admin can comment on any task
        if user.is_admin:
            return True
        
        # Task assignee can comment on their tasks
        if task.assignee_id == user_id:
            return True
        
        # This could be extended based on project/team membership
        return False
