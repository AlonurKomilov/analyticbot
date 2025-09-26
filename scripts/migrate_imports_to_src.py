#!/usr/bin/env python3
"""
Import Statement Migration Script  
Updates all import statements from core/apps/infra to src/ architecture
"""

import ast
import re
from pathlib import Path

class ImportMigrator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.import_mappings = self._get_import_mappings()
        self.updated_files = 0
        
    def _get_import_mappings(self):
        """Define import statement mappings"""
        return {
            # Core imports → src/shared_kernel or specific domains
            r'from core\.models import (.+)': r'from src.shared_kernel.domain.entities import \1',
            r'from core\.models\.(.+) import': r'from src.shared_kernel.domain.entities.\1 import',
            r'from core\.services import (.+)': r'from src.shared_kernel.application.services import \1',
            r'from core\.services\.(.+) import': r'from src.shared_kernel.application.services.\1 import',
            r'from core\.repositories import (.+)': r'from src.shared_kernel.domain.repositories import \1',
            r'from core\.security_engine import (.+)': r'from src.security import \1',
            r'from core\.ports import (.+)': r'from src.shared_kernel.domain.ports import \1',
            
            # Infra imports → infrastructure layer
            r'from infra\.db\.repositories import (.+)': r'from src.shared_kernel.infrastructure.persistence import \1',
            r'from infra\.cache import (.+)': r'from src.shared_kernel.infrastructure.cache import \1',
            r'from infra\.email import (.+)': r'from src.shared_kernel.infrastructure.email import \1',
            r'from infra\.monitoring import (.+)': r'from src.shared_kernel.infrastructure.monitoring import \1',
            
            # Apps imports → presentation layer
            r'from apps\.api\.routers import (.+)': r'from src.api_service.presentation.routers import \1',
            r'from apps\.bot import (.+)': r'from src.bot_service.presentation import \1',
            
            # Specific domain mappings
            r'from core\.models\.user import (.+)': r'from src.identity.domain.entities.user import \1',
            r'from core\.models\.payment import (.+)': r'from src.payments.domain.entities.payment import \1',
            r'from core\.services\.analytics_(.+) import': r'from src.analytics.application.services.analytics_\1 import',
            r'from infra\.db\.repositories\.user_repository import (.+)': r'from src.identity.infrastructure.persistence.user_repository import \1',
            r'from infra\.db\.repositories\.payment_repository import (.+)': r'from src.payments.infrastructure.persistence.payment_repository import \1',
        }
    
    def migrate_file_imports(self, file_path, dry_run=True):
        """Migrate imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            updated = False
            
            # Apply import mappings using regex
            for old_pattern, new_pattern in self.import_mappings.items():
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content)
                    updated = True
            
            # Special handling for src.* imports that are currently broken
            broken_src_imports = [
                (r'from src\.shared_kernel\.di import', 'from src.shared_kernel.infrastructure.di import'),
                (r'from src\.di_analytics import', 'from src.analytics.infrastructure.di import'), 
                (r'from src\.__mocks__\.(.+) import', r'from tests.mocks.\1 import'),
                (r'from src\.services\.ml\.(.+) import', r'from src.shared_kernel.application.services.ml.\1 import'),
            ]
            
            for old_pattern, new_pattern in broken_src_imports:
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content)
                    updated = True
            
            if updated:
                if dry_run:
                    print(f"📝 Would update imports in: {file_path}")
                    return True
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Updated imports in: {file_path}")
                    return True
                    
        except Exception as e:
            print(f"⚠️ Could not process {file_path}: {e}")
            
        return False
    
    def migrate_all_imports(self, dry_run=True):
        """Migrate imports in all Python files"""
        # Files to process
        patterns = [
            "src/**/*.py",
            "core/**/*.py", 
            "apps/**/*.py",
            "infra/**/*.py",
            "tests/**/*.py",
            "scripts/**/*.py",
            "*.py"  # Root level files
        ]
        
        files_updated = 0
        for pattern in patterns:
            for py_file in self.project_root.glob(pattern):
                if "__pycache__" in str(py_file) or ".git" in str(py_file):
                    continue
                    
                if self.migrate_file_imports(py_file, dry_run):
                    files_updated += 1
        
        return files_updated

def main():
    """Main import migration function"""
    import argparse
    parser = argparse.ArgumentParser(description="Migrate import statements to src/ architecture")
    parser.add_argument("--execute", action="store_true", help="Actually update files (default is dry-run)")
    parser.add_argument("--file", help="Update specific file only")
    args = parser.parse_args()
    
    migrator = ImportMigrator(".")
    
    print("🔄 Starting import statement migration")
    print("=" * 50)
    
    if args.file:
        # Update specific file
        file_path = Path(args.file)
        if file_path.exists():
            success = migrator.migrate_file_imports(file_path, dry_run=not args.execute)
            if success and args.execute:
                print(f"✅ Updated {args.file}")
            elif success:
                print(f"📝 Would update {args.file}")
        else:
            print(f"❌ File not found: {args.file}")
    else:
        # Update all files
        if args.execute:
            print("🚀 Executing import migration...")
            updated = migrator.migrate_all_imports(dry_run=False)
            print(f"✅ Updated imports in {updated} files")
        else:
            print("📋 DRY RUN - showing files that would be updated:")
            updated = migrator.migrate_all_imports(dry_run=True)
            print(f"Would update imports in {updated} files. Run with --execute to perform updates.")

if __name__ == "__main__":
    main()