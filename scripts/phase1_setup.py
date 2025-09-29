#!/usr/bin/env python3
"""
Phase 1: Architecture Migration Foundation Setup
Creates new directory structure and validates current state
"""

import os
import shutil
from pathlib import Path
import subprocess

def create_new_structure():
    """Create the new architecture directory structure"""
    print("🏗️ Creating new architecture structure...")
    
    directories = [
        # Domain layer
        "domain/entities",
        "domain/value_objects", 
        "domain/services",
        "domain/events",
        
        # Application layer
        "application/use_cases",
        "application/services", 
        "application/commands",
        "application/queries",
        "application/event_bus",
        
        # Infrastructure layer
        "infrastructure/adapters",
        "infrastructure/repositories",
        "infrastructure/messaging", 
        "infrastructure/telegram",
        "infrastructure/database",
        "infrastructure/cache",
        "infrastructure/notifications",
        
        # Presentation layer
        "presentation/api",
        "presentation/bot",
        "presentation/frontend", 
        "presentation/jobs",
        "presentation/mtproto",
        "presentation/shared",
        
        # Test structure
        "tests/unit/domain",
        "tests/unit/application", 
        "tests/unit/infrastructure",
        "tests/unit/presentation",
        "tests/integration",
        "tests/e2e",
        
        # Config structure
        "config/environments"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
        print(f"✅ Created {directory}/")

def analyze_current_structure():
    """Analyze current code structure and create migration map"""
    print("\n🔍 Analyzing current structure...")
    
    analysis = {
        "apps_files": [],
        "core_files": [],
        "infra_files": [],
        "src_files": [],
        "cross_dependencies": []
    }
    
    # Scan apps directory
    if os.path.exists("apps"):
        for root, dirs, files in os.walk("apps"):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    analysis["apps_files"].append(full_path)
    
    # Scan core directory  
    if os.path.exists("core"):
        for root, dirs, files in os.walk("core"):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    analysis["core_files"].append(full_path)
    
    # Scan infra directory
    if os.path.exists("infra"):
        for root, dirs, files in os.walk("infra"):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    analysis["infra_files"].append(full_path)
    
    # Scan src directory
    if os.path.exists("src"):
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    analysis["src_files"].append(full_path)
    
    print(f"📊 Found {len(analysis['apps_files'])} apps files")
    print(f"📊 Found {len(analysis['core_files'])} core files") 
    print(f"📊 Found {len(analysis['infra_files'])} infra files")
    print(f"📊 Found {len(analysis['src_files'])} src files")
    
    return analysis

def create_event_bus():
    """Create the event bus foundation"""
    print("\n🚌 Creating event bus foundation...")
    
    event_bus_code = '''"""
Event Bus Implementation for Clean Architecture
Enables loose coupling between application layers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Type, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class DomainEvent:
    """Base domain event class"""
    event_id: str
    timestamp: datetime
    event_type: str
    data: Dict[str, Any]
    correlation_id: Optional[str] = None
    
    @classmethod
    def create(cls, event_type: str, data: Dict[str, Any], 
               correlation_id: Optional[str] = None) -> 'DomainEvent':
        return cls(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=event_type,
            data=data,
            correlation_id=correlation_id
        )

class EventHandler(ABC):
    """Abstract base class for event handlers"""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle a domain event"""
        pass
    
    @property
    @abstractmethod
    def handled_event_types(self) -> List[str]:
        """List of event types this handler can process"""
        pass

class EventBus:
    """In-memory event bus for application coordination"""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._middleware: List[callable] = []
    
    def subscribe(self, handler: EventHandler) -> None:
        """Subscribe a handler to its supported event types"""
        for event_type in handler.handled_event_types:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            logger.info(f"Subscribed {handler.__class__.__name__} to {event_type}")
    
    def add_middleware(self, middleware: callable) -> None:
        """Add middleware for event processing"""
        self._middleware.append(middleware)
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered handlers"""
        logger.info(f"Publishing event {event.event_type} with ID {event.event_id}")
        
        # Apply middleware
        for middleware in self._middleware:
            event = await middleware(event)
        
        # Get handlers for this event type
        handlers = self._handlers.get(event.event_type, [])
        
        if not handlers:
            logger.warning(f"No handlers found for event type {event.event_type}")
            return
        
        # Execute handlers concurrently
        tasks = [handler.handle(event) for handler in handlers]
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error publishing event {event.event_id}: {e}")
            raise

# Global event bus instance
event_bus = EventBus()

# Common event types
class EventTypes:
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated" 
    ANALYTICS_REQUESTED = "analytics.requested"
    PAYMENT_PROCESSED = "payment.processed"
    CHANNEL_JOINED = "channel.joined"
    MESSAGE_SENT = "message.sent"
'''
    
    with open("application/event_bus/event_bus.py", "w") as f:
        f.write(event_bus_code)
    
    print("✅ Created application/event_bus/event_bus.py")

def create_migration_mapping():
    """Create detailed migration mapping file"""
    print("\n📋 Creating migration mapping...")
    
    mapping_content = '''# DETAILED MIGRATION MAPPING
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
    r'from core\.models\.(\w+)': r'from domain.entities.\1',
    r'from core\.domain\.(\w+)': r'from domain.entities.\1',
    r'from core\.services\.(\w+)': r'from domain.services.\1', 
    r'from core\.common\.(\w+)': r'from application.services.\1',
    r'from apps\.(\w+)\.': r'from presentation.\1.',
    r'from infra\.': r'from infrastructure.',
    r'from src\.api_service': r'from application.services',
    r'from src\.shared_kernel': r'from application.services',
}

# Files requiring manual review
MANUAL_REVIEW_FILES = [
    "apps/bot/container.py",  # DI container needs careful migration
    "core/protocols.py",      # Interface definitions
    "apps/api/deps.py",       # Dependency injection
]

# Cross-cutting concerns that need special handling
CROSS_CUTTING_CONCERNS = [
    "logging",
    "error_handling", 
    "authentication",
    "authorization",
    "validation",
    "caching"
]
'''
    
    with open("scripts/migration_mapping.py", "w") as f:
        f.write(mapping_content)
    
    print("✅ Created scripts/migration_mapping.py")

def create_validation_script():
    """Create architecture validation script"""
    print("\n✅ Creating validation script...")
    
    validator_code = '''#!/usr/bin/env python3
"""
Architecture Compliance Validator
Checks that the new architecture follows Clean Architecture principles
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Tuple

class ArchitectureViolation:
    def __init__(self, file_path: str, line: int, message: str):
        self.file_path = file_path
        self.line = line
        self.message = message
    
    def __str__(self):
        return f"{self.file_path}:{self.line} - {self.message}"

class ArchitectureValidator:
    def __init__(self):
        self.violations: List[ArchitectureViolation] = []
    
    def validate_imports(self, file_path: str) -> List[ArchitectureViolation]:
        """Validate that imports follow Clean Architecture rules"""
        violations = []
        
        # Define forbidden import patterns
        rules = [
            # Domain layer rules
            (r'^domain/', [r'from (infrastructure|presentation)\.', 
                          r'from application\.(?!event_bus)']),
            
            # Application layer rules  
            (r'^application/', [r'from presentation\.']),
            
            # Presentation layer rules
            (r'^presentation/(?!shared)', [r'from presentation\.(?!shared)']),
            
            # Infrastructure rules (can import anything except presentation)
            (r'^infrastructure/', [r'from presentation\.']),
        ]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        import_statement = f"from {node.module}"
                        
                        for pattern, forbidden_imports in rules:
                            if re.match(pattern, file_path):
                                for forbidden in forbidden_imports:
                                    if re.search(forbidden, import_statement):
                                        violations.append(
                                            ArchitectureViolation(
                                                file_path, 
                                                node.lineno,
                                                f"Forbidden import: {import_statement}"
                                            )
                                        )
        except (SyntaxError, UnicodeDecodeError):
            # Skip files that can't be parsed
            pass
        
        return violations
    
    def validate_file_location(self, file_path: str) -> List[ArchitectureViolation]:
        """Validate that files are in the correct layer"""
        violations = []
        
        # Define file location rules
        if file_path.startswith('domain/'):
            # Domain files should not import external libraries (except standard lib)
            pass
        elif file_path.startswith('application/'):
            # Application files should contain use cases and services
            pass
        elif file_path.startswith('infrastructure/'):
            # Infrastructure files should contain adapters and repositories
            pass
        elif file_path.startswith('presentation/'):
            # Presentation files should be thin controllers
            pass
        
        return violations
    
    def validate_project(self, project_path: str = '.') -> List[ArchitectureViolation]:
        """Validate entire project architecture"""
        all_violations = []
        
        # Find all Python files
        for py_file in Path(project_path).rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            file_violations = []
            file_violations.extend(self.validate_imports(str(py_file)))
            file_violations.extend(self.validate_file_location(str(py_file)))
            
            all_violations.extend(file_violations)
        
        return all_violations

def main():
    validator = ArchitectureValidator()
    violations = validator.validate_project()
    
    if violations:
        print(f"❌ Found {len(violations)} architecture violations:")
        for violation in violations:
            print(f"  {violation}")
        return 1
    else:
        print("✅ Architecture validation passed!")
        return 0

if __name__ == '__main__':
    exit(main())
'''
    
    with open("scripts/validate_architecture.py", "w") as f:
        f.write(validator_code)
    
    os.chmod("scripts/validate_architecture.py", 0o755)
    print("✅ Created scripts/validate_architecture.py")

def main():
    """Execute Phase 1 setup"""
    print("🚀 Starting Architecture Migration - Phase 1")
    print("=" * 50)
    
    # Create scripts directory if it doesn't exist
    Path("scripts").mkdir(exist_ok=True)
    
    # Execute setup steps
    create_new_structure()
    analysis = analyze_current_structure() 
    create_event_bus()
    create_migration_mapping()
    create_validation_script()
    
    print("\n🎉 Phase 1 Complete!")
    print("=" * 50)
    print("✅ New directory structure created")
    print("✅ Event bus foundation implemented") 
    print("✅ Migration mapping defined")
    print("✅ Validation scripts ready")
    
    print("\n📋 Next Steps:")
    print("1. Review the migration mapping in scripts/migration_mapping.py")
    print("2. Run baseline validation: python scripts/validate_architecture.py")
    print("3. Begin Phase 2: Domain layer migration")
    
    return analysis

if __name__ == '__main__':
    main()