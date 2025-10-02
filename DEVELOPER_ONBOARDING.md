# 👨‍💻 AnalyticBot Developer Onboarding Guide

**Welcome to the AnalyticBot development team!** This guide will help you set up your development environment and get productive quickly.

---

## 📖 **Table of Contents**

1. [Quick Start (5 minutes)](#-quick-start-5-minutes)
2. [Prerequisites](#-prerequisites)
3. [Environment Setup](#-environment-setup)
4. [Development Workflow](#-development-workflow)
5. [Architecture Understanding](#-architecture-understanding)
6. [Common Tasks](#-common-tasks)
7. [Testing Guidelines](#-testing-guidelines)
8. [Code Contribution](#-code-contribution)
9. [Troubleshooting](#-troubleshooting)
10. [Resources & Support](#-resources--support)

---

## ⚡ **Quick Start (5 minutes)**

Get AnalyticBot running locally in 5 minutes:

```bash
# 1. Clone repository
git clone https://github.com/AlonurKomilov/analyticbot.git
cd analyticbot

# 2. Set up environment
make dev-install    # Install dependencies
make dev-start      # Start development servers

# 3. Verify setup
curl http://localhost:11300/health/  # API health check
```

**That's it!** Your development environment is running:
- 🌐 **API Server**: http://localhost:11300
- 🤖 **Bot**: Running in background
- 📊 **Database**: PostgreSQL on port 11432
- ⚡ **Redis**: Cache on port 11379

---

## 📋 **Prerequisites**

### **Required Software**

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Python** | 3.11+ | Core language | `brew install python` (macOS) |
| **Git** | 2.30+ | Version control | `git --version` |
| **PostgreSQL** | 14+ | Database | `brew install postgresql` |
| **Redis** | 6+ | Caching | `brew install redis` |
| **Make** | Any | Build automation | Usually pre-installed |

### **Optional (Recommended)**

| Tool | Purpose | Installation |
|------|---------|--------------|
| **Docker** | Containerization | [Docker Desktop](https://docker.com) |
| **Node.js** | Frontend development | `brew install node` |
| **VS Code** | IDE | [Download](https://code.visualstudio.com) |
| **Postman** | API testing | [Download](https://postman.com) |

### **System Requirements**

- **OS**: macOS, Linux, Windows (WSL)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB free space
- **Network**: Internet access for dependencies

---

## ⚙️ **Environment Setup**

### **Step 1: Clone and Enter Repository**

```bash
# Clone the repository
git clone https://github.com/AlonurKomilov/analyticbot.git
cd analyticbot

# Check project structure
ls -la
```

### **Step 2: Environment Configuration**

The project uses a **Two-File Environment System**:

```bash
# Environment files are auto-created from templates
ls -la .env.*

# Files created:
# .env.development      - Development configuration
# .env.production       - Production configuration
```

#### **Configure Development Environment**

```bash
# Edit development configuration
nano .env.development

# Key settings to update:
# - BOT_TOKEN=your_telegram_bot_token
# - DATABASE_URL=postgresql://user:pass@localhost:11432/analyticbot_dev
# - REDIS_URL=redis://localhost:11379
```

### **Step 3: Install Dependencies**

```bash
# Install Python dependencies
make dev-install

# This runs:
# - Creates virtual environment (.venv/)
# - Installs requirements.txt
# - Sets up pre-commit hooks
```

### **Step 4: Database Setup**

```bash
# Start PostgreSQL and Redis
brew services start postgresql
brew services start redis

# Create development database
createdb analyticbot_dev

# Run database migrations
make migrate

# Optional: Load sample data
python data/init_sqlite_db.py
```

### **Step 5: Start Development Environment**

```bash
# Start all development services
make dev-start

# This starts:
# ✅ API server (FastAPI) on port 11300
# ✅ Telegram bot (Aiogram) in background
# ✅ Celery workers for background tasks
# ✅ Redis and PostgreSQL services
```

### **Step 6: Verify Setup**

```bash
# Test API endpoint
curl http://localhost:11300/health/

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-02T10:30:00Z",
  "version": "2.0.0"
}

# Check development status
make dev-status
```

---

## 🔄 **Development Workflow**

### **Daily Development Commands**

```bash
# Start development
make dev-start          # Start all services
make dev-logs           # View logs
make dev-status         # Check service status

# Development tasks
make dev-test           # Run tests
make lint               # Code linting
make typecheck          # Type checking

# Stop development
make dev-stop           # Stop all services
```

### **File Organization**

```
analyticbot/
├── 📁 apps/                    # Application layer
│   ├── api/                    # FastAPI REST API
│   ├── bot/                    # Telegram bot
│   ├── frontend/               # React web app
│   └── jobs/                   # Background tasks
├── 📁 core/                    # Business logic layer
│   ├── domain/                 # Domain models
│   ├── services/               # Business services
│   ├── ports/                  # Interfaces
│   └── models/                 # Data models
├── 📁 infra/                   # Infrastructure layer
│   ├── db/                     # Database layer
│   ├── factories/              # Repository factories
│   └── cache/                  # Caching layer
├── 📁 tests/                   # Test suites
├── 📁 docs/                    # Documentation
└── 📁 config/                  # Configuration files
```

### **Port Allocation**

| Service | Development | Production | Purpose |
|---------|-------------|------------|---------|
| **API Server** | 11300 | 10300 | FastAPI REST API |
| **Frontend** | 11400 | 10400 | React web application |
| **Database** | 11432 | 5432 | PostgreSQL |
| **Redis** | 11379 | 6379 | Cache and sessions |
| **Celery Flower** | 11555 | 5555 | Task monitoring |

---

## 🏗️ **Architecture Understanding**

### **Clean Architecture Overview**

AnalyticBot follows **Clean Architecture** principles:

```
┌─────────────────────────────────────────┐
│           🎮 Applications               │
│  (FastAPI, Telegram Bot, Web App)      │
├─────────────────────────────────────────┤
│         🏗️ Infrastructure              │
│  (Database, Cache, External APIs)      │
├─────────────────────────────────────────┤
│             💎 Core                     │
│    (Business Logic, Domain Rules)      │
└─────────────────────────────────────────┘
```

### **Key Design Patterns**

#### **1. Repository Factory Pattern**
```python
# Abstract interface
from core.ports.repository_factory import RepositoryFactoryProtocol

# Concrete implementation
from infra.factories.repository_factory import AsyncpgRepositoryFactory

# Usage in apps
factory = AsyncpgRepositoryFactory()
analytics_repo = factory.create_analytics_repository()
```

#### **2. Dependency Injection**
```python
# Service definition
from core.services.analytics_service import AnalyticsService

# Dependency injection
service = AnalyticsService(repository=analytics_repo)
```

#### **3. Service Layer Pattern**
```python
# Business logic in core services
class AnalyticsService:
    async def calculate_engagement_score(self, channel_id: int) -> float:
        # Pure business logic
        pass
```

### **Layer Rules (CRITICAL)**

```python
# ✅ ALLOWED: Apps can import from Core and Infra
from core.services.analytics_service import AnalyticsService
from infra.factories.repository_factory import AsyncpgRepositoryFactory

# ✅ ALLOWED: Infra can import from Core
from core.ports.analytics_repository import AnalyticsRepositoryProtocol

# ❌ FORBIDDEN: Core cannot import from Apps or Infra
from apps.api.routers import some_router  # NEVER DO THIS!
from infra.db.repositories import repo    # NEVER DO THIS!
```

---

## 📝 **Common Tasks**

### **Creating a New API Endpoint**

```python
# 1. Create router file: apps/api/routers/my_router.py
from fastapi import APIRouter, Depends
from core.services.my_service import MyService

router = APIRouter(prefix="/my-endpoint", tags=["my-feature"])

@router.get("/data/{item_id}")
async def get_data(
    item_id: int,
    service: MyService = Depends()
) -> MyResponse:
    return await service.get_data(item_id)

# 2. Add to main.py
from apps.api.routers.my_router import router as my_router
app.include_router(my_router)
```

### **Creating a Business Service**

```python
# 1. Create interface: core/ports/my_service_protocol.py
from typing import Protocol

class MyServiceProtocol(Protocol):
    async def process_data(self, data: str) -> str: ...

# 2. Create service: core/services/my_service.py
from core.ports.my_repository import MyRepositoryProtocol

class MyService:
    def __init__(self, repository: MyRepositoryProtocol):
        self._repository = repository
    
    async def process_data(self, data: str) -> str:
        # Business logic here
        return processed_data
```

### **Adding Database Operations**

```python
# 1. Create repository interface: core/ports/my_repository.py
from typing import Protocol
from core.models.my_model import MyModel

class MyRepositoryProtocol(Protocol):
    async def get_by_id(self, id: int) -> MyModel | None: ...
    async def create(self, data: MyModel) -> MyModel: ...

# 2. Create implementation: infra/db/repositories/my_repository.py
class AsyncpgMyRepository(MyRepositoryProtocol):
    async def get_by_id(self, id: int) -> MyModel | None:
        # Database implementation
        pass
```

### **Running Background Tasks**

```python
# 1. Create task: apps/jobs/tasks/my_task.py
from apps.jobs.celery_app import celery_app

@celery_app.task
def process_analytics(channel_id: int):
    # Background processing
    pass

# 2. Schedule task
from apps.jobs.tasks.my_task import process_analytics
process_analytics.delay(channel_id=123)
```

---

## 🧪 **Testing Guidelines**

### **Test Structure**

```
tests/
├── unit/                   # Unit tests (core business logic)
├── integration/           # Integration tests (database, APIs)
├── e2e/                   # End-to-end tests
└── fixtures/              # Test data and utilities
```

### **Running Tests**

```bash
# Run all tests
make dev-test

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests

# Run with coverage
pytest --cov=core --cov=apps --cov=infra
```

### **Writing Tests**

#### **Unit Test Example**
```python
# tests/unit/core/services/test_analytics_service.py
import pytest
from unittest.mock import Mock
from core.services.analytics_service import AnalyticsService

@pytest.mark.asyncio
async def test_calculate_engagement_score():
    # Given
    mock_repo = Mock()
    mock_repo.get_metrics.return_value = {"views": 1000, "likes": 50}
    service = AnalyticsService(repository=mock_repo)
    
    # When
    score = await service.calculate_engagement_score(channel_id=123)
    
    # Then
    assert score > 0
    assert score <= 1.0
    mock_repo.get_metrics.assert_called_once_with(123)
```

#### **Integration Test Example**
```python
# tests/integration/test_analytics_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_analytics_endpoint(test_client: AsyncClient):
    # When
    response = await test_client.get("/analytics/123")
    
    # Then
    assert response.status_code == 200
    data = response.json()
    assert "engagement_score" in data
```

---

## 🔀 **Code Contribution**

### **Git Workflow**

```bash
# 1. Create feature branch
git checkout -b feature/analytics-enhancement

# 2. Make changes and commit
git add .
git commit -m "feat: add engagement trend analysis"

# 3. Push and create PR
git push origin feature/analytics-enhancement
# Create Pull Request on GitHub
```

### **Commit Message Format**

```
<type>(<scope>): <description>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```bash
feat(analytics): add real-time engagement tracking
fix(api): resolve authentication token validation
docs(readme): update installation instructions
test(analytics): add unit tests for engagement service
```

### **Code Review Checklist**

- ✅ **Architecture compliance**: Follows clean architecture rules
- ✅ **Tests included**: Unit and integration tests
- ✅ **Documentation**: API endpoints documented
- ✅ **Type hints**: All functions have type annotations
- ✅ **Error handling**: Proper exception handling
- ✅ **Performance**: Efficient database queries

### **Pre-commit Hooks**

```bash
# Automatically runs on commit:
# - Code formatting (black)
# - Import sorting (isort)
# - Linting (flake8)
# - Type checking (mypy)

# Run manually:
pre-commit run --all-files
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Environment Issues**

**Problem**: `ModuleNotFoundError`
```bash
# Solution: Activate virtual environment
source .venv/bin/activate
# or
make dev-install
```

**Problem**: Database connection errors
```bash
# Solution: Check PostgreSQL service
brew services list | grep postgresql
brew services start postgresql

# Create database if missing
createdb analyticbot_dev
```

**Problem**: Port already in use
```bash
# Solution: Stop conflicting services
lsof -ti:11300 | xargs kill -9  # Kill process on port 11300
make dev-stop                   # Stop all dev services
```

#### **Development Issues**

**Problem**: Import errors between layers
```python
# ❌ Wrong: Core importing from Apps
from apps.api.dependencies import get_service

# ✅ Correct: Use dependency injection
def my_service(repo: MyRepositoryProtocol = Depends()):
    return MyService(repo)
```

**Problem**: Database migrations failing
```bash
# Solution: Reset migrations
make migrate-reset
make migrate
```

### **Performance Issues**

**Problem**: Slow API responses
```python
# Check database queries
# Add indexes for frequently queried fields
# Use async/await properly
# Implement caching for expensive operations
```

**Problem**: High memory usage
```bash
# Monitor processes
make dev-status
htop

# Check for memory leaks in background tasks
```

### **Getting Help**

1. **Check logs**: `make dev-logs`
2. **Review documentation**: `docs/` folder
3. **Search issues**: GitHub issues
4. **Ask team**: Slack channel
5. **Create issue**: Detailed bug report

---

## 📚 **Resources & Support**

### **Documentation**

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[ARCHITECTURE.md](../ARCHITECTURE.md)** | System architecture | Understanding design |
| **[API_DOCUMENTATION.md](../API_DOCUMENTATION.md)** | API reference | Building integrations |
| **[TESTING.md](./docs/TESTING.md)** | Testing guidelines | Writing tests |
| **[DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md)** | Deployment procedures | Production deployment |

### **Interactive Resources**

- **API Documentation**: http://localhost:11300/docs (Swagger)
- **API Alternative**: http://localhost:11300/redoc (ReDoc)  
- **Postman Collection**: `docs/postman/` folder
- **Database Admin**: Connect to `postgresql://localhost:11432/analyticbot_dev`

### **External Resources**

| Resource | Purpose | Link |
|----------|---------|------|
| **FastAPI Docs** | API framework | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) |
| **Aiogram Docs** | Telegram bot framework | [aiogram.dev](https://aiogram.dev) |
| **Clean Architecture** | Architecture principles | [Clean Architecture Blog](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) |
| **Python Type Hints** | Type annotations | [Python Typing](https://docs.python.org/3/library/typing.html) |

### **Development Tools**

#### **VS Code Extensions** (Recommended)
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.mypy-type-checker",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-json"
  ]
}
```

#### **IDE Configuration**
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true
}
```

### **Support Channels**

- **GitHub Issues**: Bug reports and feature requests
- **Team Slack**: `#analyticbot-dev` channel
- **Code Review**: Pull request discussions
- **Architecture Questions**: `#architecture` channel
- **Documentation**: `#docs` channel

---

## 🎯 **Success Checklist**

After completing this guide, you should be able to:

### **Environment Setup** ✅
- [ ] Clone repository and install dependencies
- [ ] Start development environment with `make dev-start`
- [ ] Access API at http://localhost:11300
- [ ] Run tests with `make dev-test`
- [ ] View logs with `make dev-logs`

### **Development Skills** ✅
- [ ] Understand clean architecture layers
- [ ] Create new API endpoints
- [ ] Write business services in core layer
- [ ] Implement repository patterns
- [ ] Write unit and integration tests

### **Code Quality** ✅
- [ ] Follow commit message conventions
- [ ] Use pre-commit hooks
- [ ] Write type hints for all functions
- [ ] Handle errors appropriately
- [ ] Follow layer dependency rules

### **Collaboration** ✅
- [ ] Create feature branches
- [ ] Submit pull requests
- [ ] Respond to code review feedback
- [ ] Update documentation when needed
- [ ] Communicate effectively with team

---

## 🎉 **Welcome to the Team!**

You're now ready to contribute to AnalyticBot! Here are your first steps:

1. **Complete the setup checklist** above
2. **Pick a "good first issue"** from GitHub
3. **Join the team Slack** channels
4. **Introduce yourself** to the team
5. **Start coding!** 🚀

### **Quick Commands Reference**

```bash
# Daily workflow
make dev-start     # Start development
make dev-test      # Run tests
make dev-logs      # View logs
make dev-stop      # Stop development

# Code quality
make lint          # Lint code
make typecheck     # Type checking
pre-commit run     # Run all checks

# Database
make migrate       # Run migrations
make migrate-reset # Reset database
```

**Happy coding!** If you have any questions, don't hesitate to ask the team. We're here to help! 💪

---

**Guide Version**: 1.0  
**Last Updated**: October 2, 2025  
**Maintained by**: Development Team  
**Questions?** Create an issue or ask in #analyticbot-dev