#!/usr/bin/env python3
"""
Fix mock services imports after migration
"""

import re
import sys
from pathlib import Path

def fix_mock_imports():
    """Fix import statements in mock services"""
    
    # Find all mock service files
    mock_files = list(Path("src/api_service/infrastructure/testing").rglob("*.py"))
    
    # Import mapping corrections
    import_fixes = {
        'src.bot_service.models': 'src.bot_service.domain.models',
        'src.shared_kernel.infrastructure.persistence.admin_repository': 'src.shared_kernel.infrastructure.repositories.admin_repository',
        'src.api_service.application.services.analytics_service': 'src.shared_kernel.application.services.analytics_service',
    }
    
    files_fixed = []
    
    for mock_file in mock_files:
        if mock_file.is_file() and mock_file.suffix == '.py':
            try:
                content = mock_file.read_text()
                original_content = content
                
                # Apply import fixes
                for old_import, new_import in import_fixes.items():
                    if old_import in content:
                        content = content.replace(old_import, new_import)
                
                if content != original_content:
                    mock_file.write_text(content)
                    files_fixed.append(str(mock_file.relative_to(Path.cwd())))
            except Exception as e:
                print(f"⚠️  Error processing {mock_file}: {e}")
    
    return files_fixed

def main():
    print("🔧 Fixing mock service imports...")
    
    fixed_files = fix_mock_imports()
    
    if fixed_files:
        print(f"✅ Fixed imports in {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"   - {file}")
    else:
        print("ℹ️  No import fixes needed")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)