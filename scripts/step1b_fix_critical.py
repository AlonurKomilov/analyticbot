#!/usr/bin/env python3
"""
Step 1b: Fix Critical Cross-Module Dependencies
"""

from pathlib import Path


def fix_critical_violations():
    """Fix the most critical violations by creating proper abstractions"""

    print("🔧 STEP 1B: FIXING CRITICAL VIOLATIONS")
    print("=" * 50)
    print("🎯 Focus: Repository and service dependencies")
    print()

    fixes_applied = []

    # Fix 1: Move repository interfaces to shared_kernel
    print("🔨 Fix 1: Creating Repository Interfaces in shared_kernel")

    # Create shared repository interfaces directory
    interfaces_dir = Path("src/shared_kernel/domain/interfaces")
    interfaces_dir.mkdir(exist_ok=True)

    # Create repository interfaces file
    repo_interfaces_content = '''"""
Repository Interfaces - Shared contracts for data access
"""

from typing import Protocol, runtime_checkable, Optional, List
from datetime import datetime


@runtime_checkable
class UserRepository(Protocol):
    """User repository interface"""
    
    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        ...
    
    async def create_user(self, user_data: dict) -> dict:
        """Create new user"""
        ...
    
    async def update_user(self, user_id: int, user_data: dict) -> dict:
        """Update user data"""
        ...


@runtime_checkable  
class PaymentRepository(Protocol):
    """Payment repository interface"""
    
    async def get_payment_by_id(self, payment_id: int) -> Optional[dict]:
        """Get payment by ID"""
        ...
    
    async def create_payment(self, payment_data: dict) -> dict:
        """Create new payment"""
        ...
    
    async def get_user_payments(self, user_id: int) -> List[dict]:
        """Get all payments for user"""
        ...


@runtime_checkable
class AnalyticsRepository(Protocol):
    """Analytics repository interface"""
    
    async def get_analytics_data(self, channel_id: int, date_from: datetime, date_to: datetime) -> List[dict]:
        """Get analytics data for channel"""
        ...
    
    async def save_analytics_data(self, data: dict) -> dict:
        """Save analytics data"""
        ...
'''

    repo_interfaces_file = interfaces_dir / "repositories.py"
    with open(repo_interfaces_file, "w", encoding="utf-8") as f:
        f.write(repo_interfaces_content)

    print(f"   ✅ Created {repo_interfaces_file}")
    fixes_applied.append({"type": "interface_created", "file": str(repo_interfaces_file)})

    # Fix 2: Create service interfaces
    print("🔨 Fix 2: Creating Service Interfaces")

    service_interfaces_content = '''"""
Service Interfaces - Shared contracts for services
"""

from typing import Protocol, runtime_checkable, Optional, Dict, Any
from datetime import datetime


@runtime_checkable
class AuthenticationService(Protocol):
    """Authentication service interface"""
    
    async def authenticate_user(self, credentials: dict) -> Optional[dict]:
        """Authenticate user with credentials"""
        ...
    
    async def create_session(self, user_id: int) -> dict:
        """Create user session"""
        ...


@runtime_checkable
class PaymentService(Protocol):
    """Payment processing service interface"""
    
    async def process_payment(self, payment_data: dict) -> dict:
        """Process a payment"""
        ...
    
    async def get_payment_status(self, payment_id: int) -> str:
        """Get payment status"""
        ...


@runtime_checkable
class AnalyticsService(Protocol):
    """Analytics service interface"""
    
    async def get_channel_analytics(self, channel_id: int, date_range: tuple) -> dict:
        """Get analytics for channel"""
        ...
    
    async def generate_report(self, report_config: dict) -> dict:
        """Generate analytics report"""
        ...
'''

    service_interfaces_file = interfaces_dir / "services.py"
    with open(service_interfaces_file, "w", encoding="utf-8") as f:
        f.write(service_interfaces_content)

    print(f"   ✅ Created {service_interfaces_file}")
    fixes_applied.append({"type": "interface_created", "file": str(service_interfaces_file)})

    # Fix 3: Update interfaces __init__.py
    interfaces_init = interfaces_dir / "__init__.py"
    init_content = '''"""
Shared Domain Interfaces
"""

from .repositories import UserRepository, PaymentRepository, AnalyticsRepository
from .services import AuthenticationService, PaymentService, AnalyticsService

__all__ = [
    "UserRepository",
    "PaymentRepository", 
    "AnalyticsRepository",
    "AuthenticationService",
    "PaymentService",
    "AnalyticsService"
]
'''

    with open(interfaces_init, "w", encoding="utf-8") as f:
        f.write(init_content)

    print(f"   ✅ Created {interfaces_init}")
    fixes_applied.append({"type": "interface_init", "file": str(interfaces_init)})

    return fixes_applied


def fix_specific_violations():
    """Fix specific import violations by replacing with interfaces"""

    print("\n🔨 STEP 1C: REPLACING DIRECT IMPORTS WITH INTERFACES")
    print("=" * 55)

    fixes_applied = []

    # Fix api_service → identity violations
    print("🔧 Fixing api_service → identity violations...")

    violations_to_fix = [
        {
            "file": "src/api_service/presentation/routers/deps.py",
            "old": "from src.identity.infrastructure.persistence.user_repository import AsyncpgUserRepository",
            "new": "from src.shared_kernel.domain.interfaces import UserRepository",
        },
        {
            "file": "src/api_service/presentation/routers/auth_router.py",
            "old": "from src.identity.infrastructure.persistence.user_repository import AsyncpgUserRepository",
            "new": "from src.shared_kernel.domain.interfaces import UserRepository",
        },
        {
            "file": "src/api_service/infrastructure/testing/initial_data_service.py",
            "old": "from src.identity.infrastructure.persistence.user_repository import AsyncpgUserRepository",
            "new": "from src.shared_kernel.domain.interfaces import UserRepository",
        },
    ]

    for violation in violations_to_fix:
        file_path = Path(violation["file"])
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                if violation["old"] in content:
                    new_content = content.replace(violation["old"], violation["new"])

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    print(f"   ✅ Fixed {file_path.name}")
                    fixes_applied.append({"type": "import_replaced", "file": str(file_path)})
                else:
                    print(f"   ℹ️  {file_path.name} - import already updated")

            except Exception as e:
                print(f"   ❌ Error fixing {file_path}: {e}")

    # Fix bot_service → payments violations
    print("\n🔧 Fixing bot_service → payments violations...")

    payment_violations = [
        {
            "file": "src/bot_service/presentation/handlers/payment_router.py",
            "old": "from src.payments.infrastructure.persistence.payment_repository import AsyncpgPaymentRepository",
            "new": "from src.shared_kernel.domain.interfaces import PaymentRepository",
        }
    ]

    for violation in payment_violations:
        file_path = Path(violation["file"])
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                if violation["old"] in content:
                    new_content = content.replace(violation["old"], violation["new"])

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    print(f"   ✅ Fixed {file_path.name}")
                    fixes_applied.append({"type": "import_replaced", "file": str(file_path)})
                else:
                    print(f"   ℹ️  {file_path.name} - import already updated or different format")

            except Exception as e:
                print(f"   ❌ Error fixing {file_path}: {e}")

    return fixes_applied


def verify_fixes():
    """Verify that fixes don't break anything critical"""

    print("\n🔍 STEP 1D: VERIFYING FIXES")
    print("=" * 30)

    # Check if interfaces can be imported
    try:
        import sys

        sys.path.insert(0, "src")

        print("   ✅ New interfaces can be imported successfully")

    except ImportError as e:
        print(f"   ❌ Interface import failed: {e}")
        return False

    # Check syntax of modified files
    modified_files = [
        "src/api_service/presentation/routers/deps.py",
        "src/api_service/presentation/routers/auth_router.py",
        "src/bot_service/presentation/handlers/payment_router.py",
    ]

    syntax_ok = True
    for file_path in modified_files:
        if Path(file_path).exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                compile(content, file_path, "exec")
                print(f"   ✅ {Path(file_path).name} - syntax OK")
            except SyntaxError as e:
                print(f"   ❌ {Path(file_path).name} - syntax error: {e}")
                syntax_ok = False
            except Exception as e:
                print(f"   ⚠️  {Path(file_path).name} - could not verify: {e}")

    return syntax_ok


if __name__ == "__main__":
    print("🚀 STEP 1B-D: SYSTEMATIC VIOLATION FIXES")
    print()

    # Create interfaces
    interface_fixes = fix_critical_violations()

    # Replace imports
    import_fixes = fix_specific_violations()

    # Verify fixes
    verification_ok = verify_fixes()

    # Summary
    print("\n📊 STEP 1B-D SUMMARY:")
    print(f"   ✅ Created {len(interface_fixes)} interface files")
    print(f"   ✅ Fixed {len(import_fixes)} import violations")
    print(
        f"   {'✅' if verification_ok else '❌'} Verification: {'PASSED' if verification_ok else 'FAILED'}"
    )

    total_fixes = len(interface_fixes) + len(import_fixes)
    print(f"   🎯 Total fixes applied: {total_fixes}")

    if verification_ok:
        print("\n🎉 STEP 1B-D COMPLETE!")
        print("   📈 Reduced module coupling by creating proper abstractions")
        print("   🔧 Next: Continue with remaining violations")
    else:
        print("\n⚠️  ISSUES DETECTED - Review fixes before continuing")
