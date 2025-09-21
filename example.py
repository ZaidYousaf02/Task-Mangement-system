from datetime import datetime, timedelta
import json

# Import all our clean, well-structured modules
from models import User, UserRole, Task, TaskStatus, TaskPriority, Project, ProjectStatus, Team, TeamRole
from repositories import UserRepository, TaskRepository, ProjectRepository, TeamRepository
from services import UserService, TaskService, ProjectService, TeamService


def main():
    """
    Comprehensive example demonstrating the task management system

    """
    print("🚀 Task Management System ")
    print("=" * 60)
    
    # Initialize repositories (data layer)
    user_repo = UserRepository()
    task_repo = TaskRepository()
    project_repo = ProjectRepository()
    team_repo = TeamRepository()
    
    # Initialize services (business logic layer)
    user_service = UserService(user_repo)
    task_service = TaskService(task_repo, user_repo)
    project_service = ProjectService(project_repo, task_repo, user_repo)
    team_service = TeamService(team_repo, user_repo)
    
    print("\n📝 Creating Users...")
    print("-" * 30)
    
    # Create users with proper validation
    try:
        admin = user_service.create_user(
            username="admin",
            email="admin@company.com",
            password="admin123",
            role=UserRole.ADMIN
        )
        admin.id = "user_001"
        print(f"✅ Created admin: {admin}")
        
        john = user_service.create_user(
            username="john_doe",
            email="john@company.com",
            password="password123"
        )
        john.id = "user_002"
        print(f"✅ Created user: {john}")
        
        jane = user_service.create_user(
            username="jane_smith",
            email="jane@company.com",
            password="password123"
        )
        jane.id = "user_003"
        print(f"✅ Created user: {jane}")
        
        # Update user profiles
        user_service.update_user_profile(
            john.id,
            first_name="John",
            last_name="Doe",
            bio="Senior Developer"
        )
        
        user_service.update_user_profile(
            jane.id,
            first_name="Jane",
            last_name="Smith",
            bio="Project Manager"
        )
        
        print(f"📋 John's full name: {john.profile.full_name}")
        print(f"📋 Jane's full name: {jane.profile.full_name}")
        
    except ValueError as e:
        print(f"❌ Error creating users: {e}")
        return
    
    print("\n👥 Creating Team...")
    print("-" * 30)
    
    # Create a development team
    dev_team = team_service.create_team(
        name="Development Team",
        description="Core development team for web applications",
        leader_id=jane.id
    )
    dev_team.id = "team_001"
    print(f"✅ Created team: {dev_team}")
    
    # Add team members
    team_service.add_team_member(dev_team.id, john.id, TeamRole.MEMBER, jane.id)
    team_service.add_team_member(dev_team.id, admin.id, TeamRole.LEADER, jane.id)
    print(f"👥 Team members: {dev_team.get_member_count()}")
    
    print("\n📁 Creating Project...")
    print("-" * 30)
    
    # Create a project
    web_app_project = project_service.create_project(
        name="E-commerce Web App",
        description="Modern e-commerce platform with React frontend and Python backend",
        owner_id=jane.id
    )
    web_app_project.id = "project_001"
    print(f"✅ Created project: {web_app_project}")
    
    # Add project to team
    team_service.add_project_to_team(dev_team.id, web_app_project.id, jane.id)
    
    # Add team members to project
    project_service.add_team_member(web_app_project.id, john.id, jane.id)
    project_service.add_team_member(web_app_project.id, admin.id, jane.id)
    
    print("\n📋 Creating Tasks...")
    print("-" * 30)
    
    # Create tasks with different priorities and due dates
    tasks = []
    
    # High priority task due soon
    urgent_task = task_service.create_task(
        title="Setup development environment",
        description="Configure Docker, database, and CI/CD pipeline",
        assignee_id=john.id,
        priority=TaskPriority.HIGH,
        due_date=datetime.utcnow() + timedelta(days=2),
        creator_id=jane.id
    )
    urgent_task.id = "task_001"
    tasks.append(urgent_task)
    print(f"✅ Created urgent task: {urgent_task}")
    
    # Medium priority task
    api_task = task_service.create_task(
        title="Design REST API",
        description="Create API endpoints for user management and product catalog",
        assignee_id=john.id,
        priority=TaskPriority.MEDIUM,
        due_date=datetime.utcnow() + timedelta(days=7),
        creator_id=jane.id
    )
    api_task.id = "task_002"
    tasks.append(api_task)
    print(f"✅ Created API task: {api_task}")
    
    # Low priority task
    docs_task = task_service.create_task(
        title="Write documentation",
        description="Create user guide and API documentation",
        assignee_id=jane.id,
        priority=TaskPriority.LOW,
        due_date=datetime.utcnow() + timedelta(days=14),
        creator_id=admin.id
    )
    docs_task.id = "task_003"
    tasks.append(docs_task)
    print(f"✅ Created documentation task: {docs_task}")
    
    # Add tasks to project
    for task in tasks:
        project_service.add_task_to_project(web_app_project.id, task, jane.id)
    
    print("\n🔄 Task Management Workflow...")
    print("-" * 30)
    
    # Simulate task workflow
    print(f"📊 Initial task status: {urgent_task.status.value}")
    
    # Start working on urgent task
    task_service.update_task_status(urgent_task.id, TaskStatus.IN_PROGRESS, john.id)
    print(f"🔄 Task status updated: {urgent_task.status.value}")
    
    # Add comments to task
    task_service.add_task_comment(
        urgent_task.id,
        john.id,
        "Started setting up Docker containers. Database connection established."
    )
    
    task_service.add_task_comment(
        urgent_task.id,
        jane.id,
        "Great progress! Make sure to document the setup process."
    )
    
    print(f"💬 Comments added: {len(urgent_task.comments)}")
    
    # Complete the task
    task_service.update_task_status(urgent_task.id, TaskStatus.DONE, john.id)
    print(f"✅ Task completed: {urgent_task.status.value}")
    
    print("\n📊 Project Milestones...")
    print("-" * 30)
    
    # Add project milestones
    milestone1 = project_service.add_milestone(
        web_app_project.id,
        "Development Environment Setup",
        "Complete development environment configuration",
        datetime.utcnow() + timedelta(days=3),
        jane.id
    )
    print(f"🎯 Created milestone: {milestone1.title}")
    
    milestone2 = project_service.add_milestone(
        web_app_project.id,
        "API Development",
        "Complete REST API implementation",
        datetime.utcnow() + timedelta(days=10),
        jane.id
    )
    print(f"🎯 Created milestone: {milestone2.title}")
    
    # Complete first milestone
    project_service.complete_milestone(web_app_project.id, milestone1.id, jane.id)
    print(f"✅ Milestone completed: {milestone1.title}")
    
    print("\n📈 System Statistics...")
    print("-" * 30)
    
    # Display comprehensive statistics
    user_stats = user_service.get_user_statistics()
    task_stats = task_service.get_task_statistics()
    project_stats = project_service.get_project_statistics()
    team_stats = team_service.get_team_statistics(dev_team.id)
    
    print(f"👥 Users: {user_stats['total']} total")
    print(f"📋 Tasks: {task_stats['total']} total, {task_stats['done']} completed")
    print(f"📁 Projects: {project_stats['total']} total")
    print(f"👥 Team: {team_stats['total_members']} members, {team_stats['total_projects']} projects")
    
    print("\n🔍 Advanced Queries...")
    print("-" * 30)
    
    # Demonstrate advanced querying capabilities
    john_tasks = task_service.get_user_tasks(john.id)
    print(f"📋 John's tasks: {len(john_tasks)}")
    
    overdue_tasks = task_service.get_overdue_tasks()
    print(f"⏰ Overdue tasks: {len(overdue_tasks)}")
    
    urgent_tasks = task_service.get_urgent_tasks()
    print(f"🚨 Urgent tasks: {len(urgent_tasks)}")
    
    # Search functionality
    search_results = task_service.search_tasks("API")
    print(f"🔍 Tasks matching 'API': {len(search_results)}")
    
    print("\n💾 Data Serialization...")
    print("-" * 30)
    
    # Demonstrate serialization capabilities
    project_data = web_app_project.to_dict()
    print(f"📄 Project serialized: {len(json.dumps(project_data))} characters")
    
    # Show task progress
    for task in tasks:
        progress = task.get_progress_percentage()
        print(f"📊 {task.title}: {progress}% complete")
    
    print("\n🎉 Example completed successfully!")
    print("=" * 60)
    print("✨ This demonstrates:")
    print("   • Clean object-oriented design")
    print("   • Proper separation of concerns")
    print("   • Repository pattern for data access")
    print("   • Service layer for business logic")
    print("   • Comprehensive validation and error handling")
    print("   • Rich domain models with business methods")
    print("   • Flexible querying and search capabilities")
    print("   • Data serialization and persistence")


if __name__ == "__main__":
    main()
