# 📚 AnalyticBot Documentation

**Welcome to the AnalyticBot documentation!** This guide provides comprehensive information for developers, users, and administrators.

## 🎯 **Quick Start**

| Document | Purpose | Audience |
|----------|---------|----------|
| [🏗️ **ARCHITECTURE.md**](../ARCHITECTURE.md) | System architecture and design patterns | Developers |
| [🚀 **Getting Started**](#-getting-started) | Setup and installation guide | All users |
| [📊 **System Requirements**](./SYSTEM_REQUIREMENTS.md) | Hardware and software requirements | DevOps |
| [🧪 **Testing Guide**](./TESTING.md) | Testing framework and guidelines | Developers |

## 📖 **Core Documentation**

### **🏗️ Architecture & Design**
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Clean architecture implementation and design patterns
- **[architecture.md](./architecture.md)** - Legacy architecture documentation
- **[CLEAN_ARCHITECTURE.md](./CLEAN_ARCHITECTURE.md)** - Clean architecture principles

### **🔧 Development Guides**
- **[DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md)** - Development process and workflows
- **[FRONTEND_DEVELOPMENT_GUIDE.md](./FRONTEND_DEVELOPMENT_GUIDE.md)** - Frontend development guidelines
- **[TESTING.md](./TESTING.md)** - Testing framework and best practices
- **[TEST_IMPROVEMENT_PLAN.md](./TEST_IMPROVEMENT_PLAN.md)** - Testing enhancement roadmap

### **🚀 Deployment & Operations**
- **[DOCKER_DEPLOYMENT_GUIDE.md](./DOCKER_DEPLOYMENT_GUIDE.md)** - Container deployment guide
- **[INFRASTRUCTURE_DEPLOYMENT_GUIDE.md](./INFRASTRUCTURE_DEPLOYMENT_GUIDE.md)** - Infrastructure setup
- **[PRODUCTION_DEPLOYMENT_GUIDE.md](./PRODUCTION_DEPLOYMENT_GUIDE.md)** - Production deployment procedures
- **[IMMEDIATE_DEPLOYMENT_PLAN.md](./IMMEDIATE_DEPLOYMENT_PLAN.md)** - Quick deployment checklist

### **⚙️ Configuration & Setup**
- **[SYSTEM_REQUIREMENTS.md](./SYSTEM_REQUIREMENTS.md)** - System and environment requirements
- **[ENVIRONMENT_ARCHITECTURE.md](./ENVIRONMENT_ARCHITECTURE.md)** - Environment configuration
- **[TWO_FILE_ENVIRONMENT_SYSTEM.md](./TWO_FILE_ENVIRONMENT_SYSTEM.md)** - Environment variable system
- **[DATABASE_MIGRATION_QUICK_REFERENCE.md](./DATABASE_MIGRATION_QUICK_REFERENCE.md)** - Database setup

### **📡 API & Integration**
- **[API_DOCUMENTATION_UPDATED.md](./API_DOCUMENTATION_UPDATED.md)** - API endpoints and usage
- **[analytics_v2.md](./analytics_v2.md)** - Analytics API v2 documentation
- **[share_links_v2.md](./share_links_v2.md)** - Share links system v2

### **🏭 System Features**
- **[MOCK_REAL_SYSTEM_DOCUMENTATION.md](./MOCK_REAL_SYSTEM_DOCUMENTATION.md)** - Mock vs real system architecture
- **[observability.md](./observability.md)** - Monitoring and observability
- **[TESTING_QUALITY_ASSURANCE_FRAMEWORK.md](./TESTING_QUALITY_ASSURANCE_FRAMEWORK.md)** - QA framework

## 📂 **Directory Structure**

```
docs/
├── 📖 Core Documentation (Active)
│   ├── ARCHITECTURE.md              # Main architecture guide
│   ├── SYSTEM_REQUIREMENTS.md       # System requirements
│   ├── TESTING.md                   # Testing framework
│   └── README.md                    # This documentation index
│
├── 📂 Specialized Directories
│   ├── deployment/                  # Deployment configurations
│   ├── guides/                      # User and admin guides
│   ├── postman/                     # API testing collections
│   └── implementation/              # Implementation-specific docs
│
└── 📦 archive/ (Historical Documentation)
    ├── audit_reports/               # Historical audit reports (130+ files)
    ├── implementation_reports/      # Completion reports (40+ files)
    ├── phase_documentation/         # Phase development docs (35+ files)
    └── legacy_guides/               # Outdated guides (15+ files)
```

## 🚀 **Getting Started**

### **For Developers**
1. **Architecture**: Start with [ARCHITECTURE.md](../ARCHITECTURE.md) to understand the system design
2. **Setup**: Follow [SYSTEM_REQUIREMENTS.md](./SYSTEM_REQUIREMENTS.md) for environment setup
3. **Development**: Use [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md) for development process
4. **Testing**: Implement tests using [TESTING.md](./TESTING.md) guidelines

### **For DevOps/Deployment**
1. **Requirements**: Check [SYSTEM_REQUIREMENTS.md](./SYSTEM_REQUIREMENTS.md)
2. **Docker**: Use [DOCKER_DEPLOYMENT_GUIDE.md](./DOCKER_DEPLOYMENT_GUIDE.md) for containerization
3. **Infrastructure**: Follow [INFRASTRUCTURE_DEPLOYMENT_GUIDE.md](./INFRASTRUCTURE_DEPLOYMENT_GUIDE.md)
4. **Production**: Deploy using [PRODUCTION_DEPLOYMENT_GUIDE.md](./PRODUCTION_DEPLOYMENT_GUIDE.md)

### **For API Integration**
1. **API Reference**: Check [API_DOCUMENTATION_UPDATED.md](./API_DOCUMENTATION_UPDATED.md)
2. **Analytics**: Use [analytics_v2.md](./analytics_v2.md) for analytics integration
3. **Testing**: Try endpoints with [postman/](./postman/) collections

## 📦 **Archived Documentation**

Historical documentation (220+ files) has been organized in `archive/` directory:

- **`archive/audit_reports/`** - System audits and analysis reports
- **`archive/implementation_reports/`** - Phase completion and implementation reports  
- **`archive/phase_documentation/`** - Development phase documentation
- **`archive/legacy_guides/`** - Outdated guides and documentation

This archive preserves development history while keeping current documentation clean and accessible.

## 🔗 **External Resources**

- **[GitHub Repository](https://github.com/AlonurKomilov/analyticbot)** - Source code and issues
- **[Clean Architecture Guide](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)** - Architecture principles
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - API framework
- **[Aiogram Documentation](https://aiogram.dev/)** - Telegram bot framework

## 📝 **Contributing**

To contribute to documentation:

1. **Current Documentation**: Update files in main `docs/` directory
2. **New Features**: Add documentation alongside code changes
3. **Historical**: Don't modify archived documentation
4. **Format**: Use Markdown with consistent formatting

---

**Last Updated**: October 2, 2025  
**Documentation Version**: 2.0  
**Files Archived**: 220+ historical documents  
**Current Active Files**: ~40 core documents  
**Maintained by**: Development Team