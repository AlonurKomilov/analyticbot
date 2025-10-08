# DETAILED MIGRATION MAPPING
# This file maps current files to their new locations

MIGRATION_MAP = {
    # Domain Layer Migrations
    "core/domain/": "domain/entities/",
    "core/models/": "domain/entities/",
    "core/services/business_logic.py": "domain/services/",
    # Application Layer Migrations
    "src/api_service/": "application/services/",
    "src/shared_kernel/": "application/services/",
    "core/common/": "application/services/",
    # Infrastructure Migrations
    "infra/": "infrastructure/",
    "core/adapters/": "infrastructure/adapters/",
    "core/repositories/": "infrastructure/repositories/",
    # Presentation Migrations
    "apps/api/": "presentation/api/",
    "apps/bot/": "presentation/bot/",
    "apps/frontend/": "presentation/frontend/",
    "apps/jobs/": "presentation/jobs/",
    "apps/mtproto/": "presentation/mtproto/",
    "apps/shared/": "presentation/shared/",
}

# Import replacement patterns
IMPORT_REPLACEMENTS = {
    r"from core\.models\.(\w+)": r"from domain.entities.",
    r"from core\.domain\.(\w+)": r"from domain.entities.",
    r"from core\.services\.(\w+)": r"from domain.services.",
    r"from core\.common\.(\w+)": r"from application.services.",
    r"from apps\.(\w+)\.": r"from presentation..",
    r"from infra\.": r"from infrastructure.",
    r"from src\.api_service": r"from application.services",
    r"from src\.shared_kernel": r"from application.services",
}

# Files requiring manual review
MANUAL_REVIEW_FILES = [
    "apps/bot/container.py",  # DI container needs careful migration
    "core/protocols.py",  # Interface definitions
    "apps/api/deps.py",  # Dependency injection
]

# Cross-cutting concerns that need special handling
CROSS_CUTTING_CONCERNS = [
    "logging",
    "error_handling",
    "authentication",
    "authorization",
    "validation",
    "caching",
]
