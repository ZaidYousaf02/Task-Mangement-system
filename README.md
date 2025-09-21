# Task Management System


## 🚀 Features

- **Domain Models**: Rich domain objects with business logic
- **Service Layer**: Business logic encapsulation
- **Repository Pattern**: Clean data access abstraction
- **Comprehensive Validation**: Input validation and error handling
- **Type Safety**: Full type hints throughout the codebase
- **Serialization**: JSON serialization/deserialization support
- **Testing**: Comprehensive test suite with unit tests

## 📁 Project Structure

```
task-management-system/
├── models/                 # Domain models
│   ├── __init__.py
│   ├── user.py            # User model with authentication
│   ├── task.py            # Task model with status tracking
│   ├── project.py         # Project model with milestones
│   └── team.py            # Team model with roles
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── user_service.py    # User management service
│   ├── task_service.py    # Task management service
│   ├── project_service.py # Project management service
│   └── team_service.py    # Team management service
├── repositories/          # Data access layer
│   ├── __init__.py
│   ├── base_repository.py # Abstract base repository
│   ├── user_repository.py # User data access
│   ├── task_repository.py # Task data access
│   ├── project_repository.py # Project data access
│   └── team_repository.py # Team data access
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_models.py     # Model tests
│   └── test_services.py   # Service tests
├── example.py             # Comprehensive usage example
├── requirements.txt       # Project dependencies
└── README.md             # This file
```

## 🏗️ Architecture

### Domain Models
- **User**: User management with authentication, profiles, and roles
- **Task**: Task management with status tracking, priorities, and comments
- **Project**: Project management with milestones and team collaboration
- **Team**: Team management with roles and permissions

### Service Layer
- **UserService**: User creation, authentication, and profile management
- **TaskService**: Task lifecycle management and assignment
- **ProjectService**: Project management and milestone tracking
- **TeamService**: Team management and member administration

### Repository Pattern
- **BaseRepository**: Abstract base class with common operations
- **Concrete Repositories**: In-memory implementations for each entity
- **Clean Interface**: Consistent data access patterns

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd task-management-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Example

```bash
python example.py
```

This will demonstrate:
- User creation and authentication
- Team and project setup
- Task management workflow
- Advanced querying and statistics
- Data serialization

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=models --cov=services --cov=repositories

# Run specific test file
python -m pytest tests/test_models.py
```

## 💡 Usage Examples

### Creating Users

```python
from models import User, UserRole
from services import UserService
from repositories import UserRepository

# Initialize services
user_repo = UserRepository()
user_service = UserService(user_repo)

# Create a user
user = user_service.create_user(
    username="john_doe",
    email="john@example.com",
    password="secure_password",
    role=UserRole.USER
)

# Update profile
user_service.update_user_profile(
    user.id,
    first_name="John",
    last_name="Doe",
    bio="Software Developer"
)
```

### Managing Tasks

```python
from models import Task, TaskStatus, TaskPriority
from services import TaskService
from repositories import TaskRepository, UserRepository

# Initialize services
user_repo = UserRepository()
task_repo = TaskRepository()
task_service = TaskService(task_repo, user_repo)

# Create a task
task = task_service.create_task(
    title="Implement user authentication",
    description="Add login and registration functionality",
    assignee_id="user_001",
    priority=TaskPriority.HIGH,
    due_date=datetime.utcnow() + timedelta(days=7)
)

# Update task status
task_service.update_task_status(task.id, TaskStatus.IN_PROGRESS, "user_001")

# Add comments
task_service.add_task_comment(task.id, "user_001", "Started working on the API endpoints")
```

### Project Management

```python
from models import Project, ProjectStatus
from services import ProjectService
from repositories import ProjectRepository, TaskRepository, UserRepository

# Initialize services
user_repo = UserRepository()
task_repo = TaskRepository()
project_repo = ProjectRepository()
project_service = ProjectService(project_repo, task_repo, user_repo)

# Create a project
project = project_service.create_project(
    name="E-commerce Platform",
    description="Modern e-commerce solution",
    owner_id="user_001"
)

# Add milestones
milestone = project_service.add_milestone(
    project.id,
    "MVP Release",
    "Minimum viable product with core features",
    datetime.utcnow() + timedelta(days=30),
    "user_001"
)
```

## 🧪 Testing

The project includes comprehensive tests covering:

- **Model Tests**: Domain object behavior and validation
- **Service Tests**: Business logic and workflow testing
- **Integration Tests**: End-to-end functionality verification

Run tests with:
```bash
python -m pytest tests/ -v
```

## 🎯 Design Principles

### Clean Code
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Dependency Inversion**: Depend on abstractions, not concretions

### Object-Oriented Design
- **Encapsulation**: Data and behavior are properly encapsulated
- **Inheritance**: Proper use of inheritance and composition
- **Polymorphism**: Interface-based programming

### SOLID Principles
- **S**ingle Responsibility Principle
- **O**pen/Closed Principle
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

## 🔧 Extensibility

The system is designed for easy extension:

1. **New Models**: Add new domain models following existing patterns
2. **New Services**: Implement business logic in service layer
3. **New Repositories**: Add data access for new entities
4. **Database Integration**: Replace in-memory repositories with database implementations
5. **API Layer**: Add REST API endpoints using the service layer

## 📊 Key Features Demonstrated

- ✅ **Clean Architecture** with proper layer separation
- ✅ **Rich Domain Models** with business logic
- ✅ **Service Layer** for business operations
- ✅ **Repository Pattern** for data access
- ✅ **Comprehensive Validation** and error handling
- ✅ **Type Safety** with full type hints
- ✅ **Serialization** support for persistence
- ✅ **Extensive Testing** with unit and integration tests
- ✅ **Documentation** with clear examples
- ✅ **SOLID Principles** throughout the codebase

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing patterns
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Built with ❤️ using clean, elegant object-oriented Python**
