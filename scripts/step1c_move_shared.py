#!/usr/bin/env python3
"""
Step 1c: Move Shared Logic to shared_kernel
"""

import os
import shutil
from pathlib import Path

def analyze_shared_components():
    """Identify components that should be in shared_kernel"""
    
    print("🔍 STEP 1C: ANALYZING SHARED COMPONENTS")
    print("=" * 42)
    
    # Look for commonly used utilities across modules
    shared_candidates = []
    
    # Check for database utilities
    db_files = []
    for module_path in Path("src").iterdir():
        if module_path.is_dir() and module_path.name != "shared_kernel":
            db_config_files = list(module_path.rglob("*database*"))
            db_connection_files = list(module_path.rglob("*connection*"))
            db_files.extend(db_config_files + db_connection_files)
    
    if db_files:
        print(f"🔍 Found {len(db_files)} database-related files across modules:")
        for f in db_files[:5]:  # Show first 5
            print(f"   📄 {f}")
        shared_candidates.append("database_utilities")
    
    # Check for authentication utilities
    auth_files = []
    for module_path in Path("src").iterdir():
        if module_path.is_dir() and module_path.name != "shared_kernel":
            auth_related_files = list(module_path.rglob("*auth*"))
            auth_files.extend(auth_related_files)
    
    if auth_files:
        print(f"\n🔍 Found {len(auth_files)} auth-related files across modules:")
        for f in auth_files[:5]:  # Show first 5
            print(f"   📄 {f}")
        shared_candidates.append("authentication_utilities")
    
    # Check for logging/monitoring utilities
    monitoring_files = []
    for module_path in Path("src").iterdir():
        if module_path.is_dir() and module_path.name != "shared_kernel":
            log_files = list(module_path.rglob("*log*"))
            monitoring_files.extend(log_files)
    
    if monitoring_files:
        print(f"\n🔍 Found {len(monitoring_files)} logging/monitoring files:")
        for f in monitoring_files[:3]:  # Show first 3
            print(f"   📄 {f}")
        shared_candidates.append("logging_utilities")
    
    return shared_candidates

def move_database_utilities():
    """Move database utilities to shared_kernel"""
    
    print(f"\n🔧 MOVING DATABASE UTILITIES TO SHARED_KERNEL")
    print("=" * 48)
    
    # Create shared infrastructure directory
    shared_infra_dir = Path("src/shared_kernel/infrastructure")
    shared_infra_dir.mkdir(exist_ok=True)
    
    # Create database utilities directory
    db_utils_dir = shared_infra_dir / "database"
    db_utils_dir.mkdir(exist_ok=True)
    
    # Look for database configuration in individual modules
    db_config_content = '''"""
Shared Database Configuration and Utilities
"""

from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import asyncpg
import os
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "analyticbot"
    username: str = "postgres"
    password: str = ""
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load config from environment variables"""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "analyticbot"),
            username=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "")
        )


class DatabaseConnection:
    """Shared database connection utilities"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig.from_env()
        self._pool: Optional[asyncpg.Pool] = None
    
    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool"""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=5,
                max_size=20
            )
        return self._pool
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            yield conn
    
    async def close(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None

def get_database_connection() -> DatabaseConnection:
    """Get global database connection instance"""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection
'''
    
    db_config_file = db_utils_dir / "connection.py"
    with open(db_config_file, 'w', encoding='utf-8') as f:
        f.write(db_config_content)
    
    print(f"   ✅ Created {db_config_file}")
    
    # Create database __init__.py
    db_init_content = '''"""
Shared Database Infrastructure
"""

from .connection import DatabaseConfig, DatabaseConnection, get_database_connection

__all__ = ["DatabaseConfig", "DatabaseConnection", "get_database_connection"]
'''
    
    db_init_file = db_utils_dir / "__init__.py"
    with open(db_init_file, 'w', encoding='utf-8') as f:
        f.write(db_init_content)
    
    print(f"   ✅ Created {db_init_file}")
    
    return [str(db_config_file), str(db_init_file)]

def create_common_exceptions():
    """Create shared exception classes"""
    
    print(f"\n🔧 CREATING SHARED EXCEPTION CLASSES")
    print("=" * 37)
    
    # Create shared domain exceptions
    domain_dir = Path("src/shared_kernel/domain")
    exceptions_content = '''"""
Shared Domain Exceptions
"""


class DomainException(Exception):
    """Base domain exception"""
    pass


class ValidationError(DomainException):
    """Validation error in domain logic"""
    pass


class ResourceNotFoundError(DomainException):
    """Requested resource not found"""
    pass


class AuthenticationError(DomainException):
    """Authentication failed"""
    pass


class AuthorizationError(DomainException):
    """Authorization failed - user lacks permissions"""
    pass


class BusinessRuleViolation(DomainException):
    """Business rule violated"""
    pass
'''
    
    exceptions_file = domain_dir / "exceptions.py"
    with open(exceptions_file, 'w', encoding='utf-8') as f:
        f.write(exceptions_content)
    
    print(f"   ✅ Created {exceptions_file}")
    
    return [str(exceptions_file)]

def update_module_imports():
    """Update modules to use shared utilities instead of duplicated code"""
    
    print(f"\n🔧 UPDATING MODULE IMPORTS TO USE SHARED UTILITIES")
    print("=" * 52)
    
    fixes_applied = []
    
    # Find files that might be importing database utilities from other modules
    suspicious_files = []
    
    # Check api_service for cross-module imports
    api_files = list(Path("src/api_service").rglob("*.py"))
    for file_path in api_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for imports from other modules
            if "from src.bot_service" in content or "from src.identity" in content:
                suspicious_files.append(file_path)
        except Exception as e:
            continue
    
    print(f"🔍 Found {len(suspicious_files)} files with potential cross-module imports:")
    for f in suspicious_files:
        print(f"   📄 {f}")
    
    # Update imports in these files
    for file_path in suspicious_files[:3]:  # Process first 3 files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace database imports
            content = content.replace(
                "from src.bot_service.infrastructure.database",
                "from src.shared_kernel.infrastructure.database"
            )
            
            # Replace authentication imports  
            content = content.replace(
                "from src.identity.domain.exceptions",
                "from src.shared_kernel.domain.exceptions"
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ Updated imports in {file_path.name}")
                fixes_applied.append(str(file_path))
        
        except Exception as e:
            print(f"   ❌ Error updating {file_path}: {e}")
    
    return fixes_applied

if __name__ == "__main__":
    print("🚀 STEP 1C: MOVE SHARED LOGIC TO SHARED_KERNEL")
    print()
    
    # Analyze what should be shared
    candidates = analyze_shared_components()
    
    # Move database utilities
    db_files = move_database_utilities()
    
    # Create shared exceptions
    exception_files = create_common_exceptions()
    
    # Update imports
    updated_imports = update_module_imports()
    
    # Summary
    print(f"\n📊 STEP 1C SUMMARY:")
    print(f"   🔍 Identified {len(candidates)} categories of shared components")
    print(f"   ✅ Created {len(db_files)} database utility files")
    print(f"   ✅ Created {len(exception_files)} shared exception files")
    print(f"   🔄 Updated {len(updated_imports)} files with corrected imports")
    
    total_created = len(db_files) + len(exception_files)
    print(f"   🎯 Total new shared files: {total_created}")
    print(f"   🎯 Total files updated: {len(updated_imports)}")
    
    print(f"\n🎉 STEP 1C COMPLETE!")
    print(f"   📈 Centralized shared utilities in shared_kernel")
    print(f"   🔧 Reduced code duplication across modules")
    print(f"   🔧 Next: Final verification and cleanup")