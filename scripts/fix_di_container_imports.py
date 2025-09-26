#!/usr/bin/env python3
"""
Fix remaining broken imports in core/di_container.py after migration
"""

import re
import sys
from pathlib import Path

def main():
    di_file = Path("core/di_container.py")
    if not di_file.exists():
        print(f"❌ {di_file} not found")
        return False
        
    content = di_file.read_text()
    original_content = content
    
    # Import mapping for mock services (now in src/)
    mock_imports = {
        'tests.mocks.services.mock_analytics_service': 'src.api_service.infrastructure.testing.services.mock_analytics_service',
        'tests.mocks.services.mock_payment_service': 'src.api_service.infrastructure.testing.services.mock_payment_service', 
        'tests.mocks.database.mock_database': 'src.api_service.infrastructure.testing.database.mock_database',
        'tests.mocks.services.mock_ai_service': 'src.api_service.infrastructure.testing.services.mock_ai_service',
        'tests.mocks.services.mock_telegram_service': 'src.api_service.infrastructure.testing.services.mock_telegram_service',
        'tests.mocks.services.mock_email_service': 'src.api_service.infrastructure.testing.services.mock_email_service',
        'tests.mocks.services.mock_auth_service': 'src.api_service.infrastructure.testing.services.mock_auth_service',
        'tests.mocks.services.mock_admin_service': 'src.api_service.infrastructure.testing.services.mock_admin_service',
        'tests.mocks.services.mock_demo_data_service': 'src.api_service.infrastructure.testing.services.mock_demo_data_service',
    }
    
    # Service imports (corrected paths)
    service_imports = {
        'src.services.payment_service': 'src.bot_service.application.services.payment_service',
        'src.shared_kernel.application.services.ml.ai_insights': 'src.bot_service.application.services.ml.ai_insights',
        'src.shared_kernel.application.services.superadmin_service': 'src.identity.application.services.superadmin_service',
        'src.services.adapters.telegram_analytics_adapter': 'src.bot_service.application.services.adapters.telegram_analytics_adapter',
    }
    
    # Infrastructure imports that need fixing
    infra_imports = {
        'infra.email.smtp_email_service': 'src.notification.infrastructure.email.smtp_email_service',
        'core.security_engine.auth': 'src.identity.infrastructure.security_engine.auth',
    }
    
    # Apply all import fixes
    all_imports = {**mock_imports, **service_imports, **infra_imports}
    
    changes_made = []
    
    for old_import, new_import in all_imports.items():
        old_pattern = f"from {old_import} import"
        new_pattern = f"from {new_import} import"
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            changes_made.append(f"✅ {old_import} → {new_import}")
    
    # Add missing import for asynccontextmanager
    if '@asynccontextmanager' in content and 'from contextlib import asynccontextmanager' not in content:
        # Find import section and add the missing import
        import_section = content.find('from typing import')
        if import_section != -1:
            line_end = content.find('\n', import_section)
            content = content[:line_end + 1] + 'from contextlib import asynccontextmanager\n' + content[line_end + 1:]
            changes_made.append("✅ Added missing asynccontextmanager import")
    
    if content != original_content:
        di_file.write_text(content)
        print(f"🎯 Fixed {len(changes_made)} import issues in DI container:")
        for change in changes_made:
            print(f"   {change}")
        return True
    else:
        print("✅ No changes needed in DI container")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)