"""
Test suite for domain models

"""

import unittest
from datetime import datetime, timedelta

from models.user import User, UserRole, UserProfile, ValidationError
from models.task import Task, TaskStatus, TaskPriority, TaskComment
from models.project import Project, ProjectStatus, ProjectMilestone
from models.team import Team, TeamRole, TeamMember


class TestUserModel(unittest.TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "test@example.com", "password123")
        self.user.id = "user_001"
    
    def test_user_creation(self):
        """Test user creation with valid data"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.role, UserRole.USER)
        self.assertIsNotNone(self.user.id)
    
    def test_user_validation(self):
        """Test user validation rules"""
        # Test invalid username
        with self.assertRaises(ValidationError):
            User("ab", "test@example.com", "password123")
        
        # Test invalid email
        with self.assertRaises(ValidationError):
            User("testuser", "invalid-email", "password123")
        
        # Test short password
        with self.assertRaises(ValidationError):
            User("testuser", "test@example.com", "123")
    
    def test_password_verification(self):
        """Test password verification"""
        self.assertTrue(self.user.verify_password("password123"))
        self.assertFalse(self.user.verify_password("wrongpassword"))
    
    def test_profile_management(self):
        """Test user profile management"""
        self.user.update_profile(
            first_name="John",
            last_name="Doe",
            bio="Test user"
        )
        
        self.assertEqual(self.user.profile.first_name, "John")
        self.assertEqual(self.user.profile.last_name, "Doe")
        self.assertEqual(self.user.profile.full_name, "John Doe")
        self.assertEqual(self.user.profile.bio, "Test user")
    
    def test_user_serialization(self):
        """Test user serialization to/from dict"""
        self.user.update_profile(first_name="John", last_name="Doe")
        
        user_dict = self.user.to_dict()
        self.assertIn("username", user_dict)
        self.assertIn("email", user_dict)
        self.assertIn("profile", user_dict)
        
        restored_user = User.from_dict(user_dict)
        self.assertEqual(restored_user.username, self.user.username)
        self.assertEqual(restored_user.email, self.user.email)


class TestTaskModel(unittest.TestCase):
    """Test cases for Task model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.task = Task(
            title="Test Task",
            description="A test task",
            assignee_id="user_001",
            priority=TaskPriority.HIGH
        )
        self.task.id = "task_001"
    
    def test_task_creation(self):
        """Test task creation with valid data"""
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.description, "A test task")
        self.assertEqual(self.task.assignee_id, "user_001")
        self.assertEqual(self.task.priority, TaskPriority.HIGH)
        self.assertEqual(self.task.status, TaskStatus.TODO)
    
    def test_task_status_updates(self):
        """Test task status updates"""
        self.task.update_status(TaskStatus.IN_PROGRESS)
        self.assertEqual(self.task.status, TaskStatus.IN_PROGRESS)
        
        self.task.update_status(TaskStatus.DONE)
        self.assertEqual(self.task.status, TaskStatus.DONE)
        
        # Cannot change status of completed task
        with self.assertRaises(ValueError):
            self.task.update_status(TaskStatus.TODO)
    
    def test_task_comments(self):
        """Test task comment functionality"""
        comment = self.task.add_comment("user_001", "This is a test comment")
        
        self.assertEqual(len(self.task.comments), 1)
        self.assertEqual(comment.content, "This is a test comment")
        self.assertEqual(comment.author_id, "user_001")
    
    def test_task_tags(self):
        """Test task tagging functionality"""
        self.task.add_tag("frontend")
        self.task.add_tag("urgent")
        
        self.assertIn("frontend", self.task.tags)
        self.assertIn("urgent", self.task.tags)
        
        self.task.remove_tag("frontend")
        self.assertNotIn("frontend", self.task.tags)
        self.assertIn("urgent", self.task.tags)
    
    def test_task_overdue_detection(self):
        """Test overdue task detection"""
        # Task with past due date
        overdue_task = Task(
            title="Overdue Task",
            due_date=datetime.utcnow() - timedelta(days=1)
        )
        self.assertTrue(overdue_task.is_overdue())
        
        # Task with future due date
        future_task = Task(
            title="Future Task",
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        self.assertFalse(future_task.is_overdue())
    
    def test_task_urgency_detection(self):
        """Test urgent task detection"""
        # Urgent priority task
        urgent_task = Task(
            title="Urgent Task",
            priority=TaskPriority.URGENT
        )
        self.assertTrue(urgent_task.is_urgent())
        
        # High priority task due soon
        soon_due_task = Task(
            title="Soon Due Task",
            priority=TaskPriority.HIGH,
            due_date=datetime.utcnow() + timedelta(hours=12)
        )
        self.assertTrue(soon_due_task.is_urgent())
    
    def test_task_progress(self):
        """Test task progress calculation"""
        self.assertEqual(self.task.get_progress_percentage(), 0)  # TODO
        
        self.task.update_status(TaskStatus.IN_PROGRESS)
        self.assertEqual(self.task.get_progress_percentage(), 50)
        
        self.task.update_status(TaskStatus.DONE)
        self.assertEqual(self.task.get_progress_percentage(), 100)


class TestProjectModel(unittest.TestCase):
    """Test cases for Project model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.project = Project(
            name="Test Project",
            description="A test project",
            owner_id="user_001"
        )
        self.project.id = "project_001"
    
    def test_project_creation(self):
        """Test project creation with valid data"""
        self.assertEqual(self.project.name, "Test Project")
        self.assertEqual(self.project.description, "A test project")
        self.assertEqual(self.project.owner_id, "user_001")
        self.assertEqual(self.project.status, ProjectStatus.PLANNING)
    
    def test_project_tasks(self):
        """Test project task management"""
        task1 = Task("Task 1", "First task")
        task2 = Task("Task 2", "Second task")
        
        self.project.add_task(task1)
        self.project.add_task(task2)
        
        self.assertEqual(len(self.project.tasks), 2)
        
        self.project.remove_task(task1)
        self.assertEqual(len(self.project.tasks), 1)
    
    def test_project_milestones(self):
        """Test project milestone management"""
        milestone = self.project.add_milestone(
            "Milestone 1",
            "First milestone",
            datetime.utcnow() + timedelta(days=7)
        )
        
        self.assertEqual(len(self.project.milestones), 1)
        self.assertFalse(milestone.completed)
        
        self.project.complete_milestone(milestone.id)
        self.assertTrue(milestone.completed)
        self.assertIsNotNone(milestone.completed_at)
    
    def test_project_team_members(self):
        """Test project team member management"""
        self.project.add_team_member("user_002")
        self.project.add_team_member("user_003")
        
        self.assertEqual(len(self.project.team_members), 2)
        self.assertIn("user_002", self.project.team_members)
        
        self.project.remove_team_member("user_002")
        self.assertEqual(len(self.project.team_members), 1)
        self.assertNotIn("user_002", self.project.team_members)
    
    def test_project_progress(self):
        """Test project progress calculation"""
        # Add tasks with different statuses
        task1 = Task("Task 1")
        task2 = Task("Task 2")
        task3 = Task("Task 3")
        
        task1.update_status(TaskStatus.DONE)
        task2.update_status(TaskStatus.IN_PROGRESS)
        
        self.project.add_task(task1)
        self.project.add_task(task2)
        self.project.add_task(task3)
        
        # 1 out of 3 tasks completed = 33%
        self.assertEqual(self.project.get_progress_percentage(), 33)


class TestTeamModel(unittest.TestCase):
    """Test cases for Team model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.team = Team(
            name="Test Team",
            description="A test team",
            leader_id="user_001"
        )
        self.team.id = "team_001"
    
    def test_team_creation(self):
        """Test team creation with valid data"""
        self.assertEqual(self.team.name, "Test Team")
        self.assertEqual(self.team.description, "A test team")
        self.assertEqual(self.team.leader_id, "user_001")
    
    def test_team_members(self):
        """Test team member management"""
        member1 = self.team.add_member("user_002", TeamRole.MEMBER)
        member2 = self.team.add_member("user_003", TeamRole.CONTRIBUTOR)
        
        self.assertEqual(len(self.team.members), 2)
        self.assertTrue(self.team.is_member("user_002"))
        self.assertEqual(self.team.get_member_role("user_002"), TeamRole.MEMBER)
        
        self.team.remove_member("user_002")
        self.assertEqual(len(self.team.members), 1)
        self.assertFalse(self.team.is_member("user_002"))
    
    def test_team_permissions(self):
        """Test team permission system"""
        member = self.team.add_member("user_002", TeamRole.MEMBER)
        
        self.assertTrue(self.team.has_permission("user_002", "project.view"))
        self.assertFalse(self.team.has_permission("user_002", "team.manage"))
        
        # Promote to leader
        self.team.promote_member("user_002", TeamRole.LEADER)
        self.assertTrue(self.team.has_permission("user_002", "team.manage"))
    
    def test_team_projects(self):
        """Test team project management"""
        self.team.add_project("project_001")
        self.team.add_project("project_002")
        
        self.assertEqual(len(self.team.projects), 2)
        self.assertIn("project_001", self.team.projects)
        
        self.team.remove_project("project_001")
        self.assertEqual(len(self.team.projects), 1)
        self.assertNotIn("project_001", self.team.projects)


if __name__ == "__main__":
    unittest.main()
