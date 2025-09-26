#!/usr/bin/env python3
"""
Comprehensive fix for all broken imports in mock services
"""

import re
from pathlib import Path

def fix_all_mock_imports():
    """Fix all broken imports in mock services"""
    
    mock_files = [
        "src/api_service/infrastructure/testing/services/mock_payment_service.py",
        "src/api_service/infrastructure/testing/services/mock_demo_data_service.py", 
        "src/api_service/infrastructure/testing/services/mock_email_service.py",
        "src/api_service/infrastructure/testing/services/mock_admin_service.py",
        "src/api_service/infrastructure/testing/services/mock_ai_service.py",
        "src/api_service/infrastructure/testing/services/mock_auth_service.py",
        "src/api_service/infrastructure/testing/services/mock_telegram_service.py",
    ]
    
    # Common constants to add
    demo_constants = '''
# Demo constants (moved from old apps.api.__mocks__.constants)
DEMO_API_DELAY_MS = 100
DEMO_SUCCESS_RATE = 0.95
DEFAULT_DEMO_CHANNEL_ID = "demo_channel_123"
DEMO_POSTS_COUNT = 50
DEMO_METRICS_DAYS = 30
'''
    
    for file_path in mock_files:
        file_obj = Path(file_path)
        if not file_obj.exists():
            continue
            
        content = file_obj.read_text()
        original_content = content
        
        # Remove old apps imports and add constants directly
        if "from apps.api.__mocks__.constants import" in content:
            # Remove the import line
            lines = content.split('\n')
            new_lines = []
            in_import_block = False
            
            for line in lines:
                if "from apps.api.__mocks__.constants import" in line:
                    # Start of import block - add constants instead
                    new_lines.append(demo_constants.strip())
                    in_import_block = True
                elif in_import_block and (line.strip() == '' or line.startswith('    ') or line.startswith(')')):
                    # Skip continuation of import block
                    if ')' in line:
                        in_import_block = False
                    continue
                else:
                    in_import_block = False
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
        
        # Fix other broken imports
        replacements = {
            'from apps.bot.services.adapters.mock_payment_adapter import MockPaymentAdapter': 
                '# MockPaymentAdapter - using inline implementation',
            'from apps.bot.models.payment import BillingCycle': 
                'from src.payments.domain.value_objects import BillingCycle',
            'from apps.bot.models.twa import InitialDataResponse':
                'from src.bot_service.domain.models.twa import InitialDataResponse',
        }
        
        for old_import, new_import in replacements.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
        
        if content != original_content:
            file_obj.write_text(content)
            print(f"✅ Fixed imports in {file_path}")

def main():
    print("🔧 Fixing all mock service imports...")
    fix_all_mock_imports()
    print("✅ All mock service imports fixed!")

if __name__ == "__main__":
    main()