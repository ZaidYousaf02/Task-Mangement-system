"""
Test suite for service layer

"""

import unittest
from datetime import datetime, timedelta

from models.user import User, UserRole
from models.task import Task, TaskStatus, TaskPriority
from models.project import Project, ProjectStatus
from models.team import Team, TeamRole

from repositories import UserRepository, TaskRepository, ProjectRepository, TeamRepository
from services import UserService, TaskService, ProjectService, TeamService


class TestUserService(unittest.TestCase):
    """Test cases for UserService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user_repo = UserRepository()
        self.user_service = UserService(self.user_repo)
    
    def test_create_user(self):
        """Test user creation through service"""
        user = self.user_service.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, UserRole.USER)
    
    def test_duplicate_username(self):
        """Test duplicate username handling"""
        self.user_service.create_user("testuser", "test1@example.com", "password123")
        
        with self.assertRaises(ValueError):
            self.user_service.create_user("testuser", "test2@example.com", "password123")
    
    def test_duplicate_email(self):
        """Test duplicate email handling"""
        self.user_service.create_user("user1", "test@example.com", "password123")
        
        with self.assertRaises(ValueError):
            self.user_service.create_user("user2", "test@example.com", "password123")
    
    def test_authenticate_user(self):
        """Test user authentication"""
        user = self.user_service.create_user("testuser", "test@example.com", "password123")
        
        # Valid credentials
        authenticated = self.user_service.authenticate_user("testuser", "password123")
        self.assertEqual(authenticated.id, user.id)
        
        # Invalid credentials
        authenticated = self.user_service.authenticate_user("testuser", "wrongpassword")
        self.assertIsNone(authenticated)
    
    def test_update_profile(self):
        """Test profile update through service"""
        user = self.user_service.create_user("testuser", "test@example.com", "password123")
        
        self.user_service.update_user_profile(
            user.id,
            first_name="John",
            last_name="Doe",
            bio="Test user"
        )
        
        self.assertEqual(user.profile.first_name, "John")
        self.assertEqual(user.profile.last_name, "Doe")
        self.assertEqual(user.profile.bio, "Test user")


class TestTaskService(unittest.TestCase):
    """Test cases for TaskService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user_repo = UserRepository()
        self.task_repo = TaskRepository()
        self.task_service = TaskService(self.task_repo, self.user_repo)
        
        # Create test users
        self.user1 = self.user_service.create_user("user1", "user1@example.com", "password123")
        self.user2 = self.user_service.create_user("user2", "user2@example.com", "password123")
    
    def test_create_task(self):
        """Test task creation through service"""
        task = self.task_service.create_task(
            title="Test Task",
            description="A test task",
            assignee_id=self.user1.id,
            priority=TaskPriority.HIGH,
            creator_id=self.user2.id
        )
        
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.assignee_id, self.user1.id)
        self.assertEqual(task.priority, TaskPriority.HIGH)
    
    def test_update_task_status(self):
        """Test task status update through service"""
        task = self.task_service.create_task(
            title="Test Task",
            assignee_id=self.user1.id,
            creator_id=self.user2.id
        )
        
        # Assignee can update their own task
        updated_task = self.task_service.update_task_status(
            task.id,
            TaskStatus.IN_PROGRESS,
            self.user1.id
        )
        
        self.assertEqual(updated_task.status, TaskStatus.IN_PROGRESS)
    
    def test_assign_task(self):
        """Test task assignment through service"""
        task = self.task_service.create_task(
            title="Test Task",
            creator_id=self.user1.id
        )
        
        # Admin can assign tasks
        admin = self.user_service.create_user("admin", "admin@example.com", "password123", UserRole.ADMIN)
        
        assigned_task = self.task_service.assign_task(task.id, self.user2.id, admin.id)
        self.assertEqual(assigned_task.assignee_id, self.user2.id)
    
    def test_add_task_comment(self):
        """Test adding comments through service"""
        task = self.task_service.create_task(
            title="Test Task",
            assignee_id=self.user1.id,
            creator_id=self.user2.id
        )
        
        # Assignee can comment on their task
        commented_task = self.task_service.add_task_comment(
            task.id,
            self.user1.id,
            "This is a test comment"
        )
        
        self.assertEqual(len(commented_task.comments), 1)
        self.assertEqual(commented_task.comments[0].content, "This is a test comment")
    
    def test_get_user_tasks(self):
        """Test getting user tasks through service"""
        task1 = self.task_service.create_task("Task 1", assignee_id=self.user1.id, creator_id=self.user2.id)
        task2 = self.task_service.create_task("Task 2", assignee_id=self.user1.id, creator_id=self.user2.id)
        task3 = self.task_service.create_task("Task 3", assignee_id=self.user2.id, creator_id=self.user1.id)
        
        user1_tasks = self.task_service.get_user_tasks(self.user1.id)
        self.assertEqual(len(user1_tasks), 2)
        
        user2_tasks = self.task_service.get_user_tasks(self.user2.id)
        self.assertEqual(len(user2_tasks), 1)


class TestProjectService(unittest.TestCase):
    """Test cases for ProjectService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user_repo = UserRepository()
        self.task_repo = TaskRepository()
        self.project_repo = ProjectRepository()
        self.project_service = ProjectService(self.project_repo, self.task_repo, self.user_repo)
        
        # Create test users
        self.owner = self.user_service.create_user("owner", "owner@example.com", "password123")
        self.member = self.user_service.create_user("member", "member@example.com", "password123")
    
    def test_create_project(self):
        """Test project creation through service"""
        project = self.project_service.create_project(
            name="Test Project",
            description="A test project",
            owner_id=self.owner.id
        )
        
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.owner_id, self.owner.id)
        self.assertEqual(project.status, ProjectStatus.PLANNING)
    
    def test_add_task_to_project(self):
        """Test adding task to project through service"""
        project = self.project_service.create_project("Test Project", owner_id=self.owner.id)
        task = Task("Test Task")
        
        updated_project = self.project_service.add_task_to_project(project.id, task, self.owner.id)
        self.assertEqual(len(updated_project.tasks), 1)
    
    def test_add_milestone(self):
        """Test adding milestone through service"""
        project = self.project_service.create_project("Test Project", owner_id=self.owner.id)
        
        milestone = self.project_service.add_milestone(
            project.id,
            "Milestone 1",
            "First milestone",
            datetime.utcnow() + timedelta(days=7),
            self.owner.id
        )
        
        self.assertEqual(milestone.title, "Milestone 1")
        self.assertFalse(milestone.completed)
    
    def test_add_team_member(self):
        """Test adding team member through service"""
        project = self.project_service.create_project("Test Project", owner_id=self.owner.id)
        
        updated_project = self.project_service.add_team_member(project.id, self.member.id, self.owner.id)
        self.assertIn(self.member.id, updated_project.team_members)


class TestTeamService(unittest.TestCase):
    """Test cases for TeamService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user_repo = UserRepository()
        self.team_repo = TeamRepository()
        self.team_service = TeamService(self.team_repo, self.user_repo)
        
        # Create test users
        self.leader = self.user_service.create_user("leader", "leader@example.com", "password123")
        self.member = self.user_service.create_user("member", "member@example.com", "password123")
    
    def test_create_team(self):
        """Test team creation through service"""
        team = self.team_service.create_team(
            name="Test Team",
            description="A test team",
            leader_id=self.leader.id
        )
        
        self.assertEqual(team.name, "Test Team")
        self.assertEqual(team.leader_id, self.leader.id)
        self.assertTrue(team.is_member(self.leader.id))
        self.assertEqual(team.get_member_role(self.leader.id), TeamRole.LEADER)
    
    def test_add_team_member(self):
        """Test adding team member through service"""
        team = self.team_service.create_team("Test Team", leader_id=self.leader.id)
        
        member = self.team_service.add_team_member(team.id, self.member.id, TeamRole.MEMBER, self.leader.id)
        self.assertEqual(member.user_id, self.member.id)
        self.assertEqual(member.role, TeamRole.MEMBER)
        self.assertTrue(team.is_member(self.member.id))
    
    def test_promote_team_member(self):
        """Test promoting team member through service"""
        team = self.team_service.create_team("Test Team", leader_id=self.leader.id)
        self.team_service.add_team_member(team.id, self.member.id, TeamRole.MEMBER, self.leader.id)
        
        success = self.team_service.promote_team_member(team.id, self.member.id, TeamRole.LEADER, self.leader.id)
        self.assertTrue(success)
        self.assertEqual(team.get_member_role(self.member.id), TeamRole.LEADER)
    
    def test_remove_team_member(self):
        """Test removing team member through service"""
        team = self.team_service.create_team("Test Team", leader_id=self.leader.id)
        self.team_service.add_team_member(team.id, self.member.id, TeamRole.MEMBER, self.leader.id)
        
        success = self.team_service.remove_team_member(team.id, self.member.id, self.leader.id)
        self.assertTrue(success)
        self.assertFalse(team.is_member(self.member.id))


if __name__ == "__main__":
    unittest.main()
