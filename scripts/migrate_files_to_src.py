#!/usr/bin/env python3
"""
Automated File Migration Script
Moves files from core/apps/infra to src/ architecture
"""

import os
import shutil
from pathlib import Path

class FileMigrator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.migration_map = self._get_migration_mapping()
        
    def _get_migration_mapping(self):
        """Define how files should be migrated"""
        return {
            # Core models to domain entities (actual files that exist)
            "core/models/base.py": "src/shared_kernel/domain/entities/base.py",
            "core/models/admin.py": "src/identity/domain/entities/admin.py",
            "core/models/common.py": "src/shared_kernel/domain/entities/common.py",
            "core/models/__init__.py": "src/shared_kernel/domain/entities/__init__.py",
            
            # Core repositories to domain interfaces
            "core/repositories/interfaces.py": "src/shared_kernel/domain/repositories/interfaces.py",
            "core/repositories/shared_reports_repository.py": "src/shared_kernel/domain/repositories/shared_reports_repository.py",
            "core/repositories/alert_repository.py": "src/shared_kernel/domain/repositories/alert_repository.py",
            
            # Core services to application layer (actual files that exist)
            "core/services/analytics_fusion_service.py": "src/analytics/application/services/analytics_fusion_service.py",
            "core/services/enhanced_delivery_service.py": "src/shared_kernel/application/services/enhanced_delivery_service.py",
            "core/services/superadmin_service.py": "src/identity/application/services/superadmin_service.py",
            "core/services/__init__.py": "src/shared_kernel/application/services/__init__.py",
            
            # Core ports to domain ports (directory)
            "core/ports/": "src/shared_kernel/domain/ports/",
            
            # Security engine to security domain (directory)
            "core/security_engine/": "src/security/",
            
            # Infrastructure repositories (actual files that exist)
            "infra/db/repositories/user_repository.py": "src/identity/infrastructure/persistence/user_repository.py",
            "infra/db/repositories/admin_repository.py": "src/identity/infrastructure/persistence/admin_repository.py",
            "infra/db/repositories/payment_repository.py": "src/payments/infrastructure/persistence/payment_repository.py",
            "infra/db/repositories/channel_repository.py": "src/analytics/infrastructure/persistence/channel_repository.py",
            "infra/db/repositories/channel_daily_repository.py": "src/analytics/infrastructure/persistence/channel_daily_repository.py",
            "infra/db/repositories/post_repository.py": "src/analytics/infrastructure/persistence/post_repository.py",
            "infra/db/repositories/post_metrics_repository.py": "src/analytics/infrastructure/persistence/post_metrics_repository.py",
            "infra/db/repositories/stats_raw_repository.py": "src/analytics/infrastructure/persistence/stats_raw_repository.py",
            "infra/db/repositories/shared_reports_repository.py": "src/shared_kernel/infrastructure/persistence/shared_reports_repository.py",
            "infra/db/repositories/alert_repository.py": "src/shared_kernel/infrastructure/persistence/alert_repository.py",
            "infra/db/repositories/__init__.py": "src/shared_kernel/infrastructure/persistence/__init__.py",
            
            # Shared infrastructure (directories)
            "infra/cache/": "src/shared_kernel/infrastructure/cache/",
            "infra/email/": "src/shared_kernel/infrastructure/email/",
            "infra/monitoring/": "src/shared_kernel/infrastructure/monitoring/",
        }
    
    def create_target_structure(self):
        """Create the target src/ directory structure"""
        directories = [
            # Shared kernel
            "src/shared_kernel/domain/entities",
            "src/shared_kernel/domain/repositories", 
            "src/shared_kernel/domain/ports",
            "src/shared_kernel/application/services",
            "src/shared_kernel/application/use_cases",
            "src/shared_kernel/infrastructure/cache",
            "src/shared_kernel/infrastructure/email",
            "src/shared_kernel/infrastructure/monitoring",
            "src/shared_kernel/infrastructure/persistence",
            "src/shared_kernel/infrastructure/di",
            
            # Analytics domain
            "src/analytics/domain/entities",
            "src/analytics/domain/repositories",
            "src/analytics/domain/value_objects",
            "src/analytics/application/services",
            "src/analytics/application/use_cases",
            "src/analytics/infrastructure/persistence",
            "src/analytics/infrastructure/external",
            
            # Identity domain
            "src/identity/domain/entities", 
            "src/identity/domain/repositories",
            "src/identity/domain/value_objects",
            "src/identity/application/services",
            "src/identity/application/use_cases",
            "src/identity/infrastructure/persistence",
            "src/identity/infrastructure/external",
            
            # Payments domain
            "src/payments/domain/entities",
            "src/payments/domain/repositories", 
            "src/payments/domain/value_objects",
            "src/payments/application/services",
            "src/payments/application/use_cases",
            "src/payments/infrastructure/persistence",
            "src/payments/infrastructure/external",
            
            # Security domain
            "src/security/domain",
            "src/security/application",
            "src/security/infrastructure",
            
            # Service layers
            "src/api_service/presentation/routers",
            "src/api_service/presentation/middleware", 
            "src/api_service/application/services",
            "src/bot_service/presentation/handlers",
            "src/bot_service/application/services",
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py files
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Domain module"""')
                
        print(f"✅ Created {len(directories)} directories")
    
    def migrate_files(self, dry_run=True):
        """Migrate files to new structure (MOVE, not copy)"""
        migrated = 0
        
        for source_pattern, target_path in self.migration_map.items():
            source_path = self.project_root / source_pattern
            target_full_path = self.project_root / target_path
            
            if source_path.is_file():
                if dry_run:
                    print(f"📁 Would MOVE: {source_pattern} → {target_path}")
                else:
                    # Ensure target directory exists
                    target_full_path.parent.mkdir(parents=True, exist_ok=True)
                    # MOVE file, don't copy
                    shutil.move(str(source_path), str(target_full_path))
                    print(f"✅ MOVED: {source_pattern} → {target_path}")
                migrated += 1
                
            elif source_path.is_dir():
                if dry_run:
                    print(f"📁 Would MOVE directory: {source_pattern} → {target_path}")
                else:
                    target_full_path.parent.mkdir(parents=True, exist_ok=True)
                    if target_full_path.exists():
                        shutil.rmtree(target_full_path)
                    # MOVE directory, don't copy
                    shutil.move(str(source_path), str(target_full_path))
                    print(f"✅ MOVED directory: {source_pattern} → {target_path}")
                migrated += 1
            else:
                print(f"⚠️ Source not found: {source_pattern}")
        
        return migrated
    
    def check_remaining_files(self):
        """Check what files remain in core/apps/infra after migration"""
        remaining_files = {
            "core": [],
            "apps": [], 
            "infra": []
        }
        
        for directory in ["core", "apps", "infra"]:
            dir_path = self.project_root / directory
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    if "__pycache__" not in str(py_file):
                        remaining_files[directory].append(str(py_file.relative_to(self.project_root)))
        
        return remaining_files
    
    def create_compatibility_layers(self):
        """Create compatibility imports for gradual transition"""
        compatibility_mappings = [
            ("core/__init__.py", [
                "# Compatibility layer - deprecated, use src/ imports",
                "import warnings",
                "warnings.warn('core/ imports are deprecated, use src/ instead', DeprecationWarning)",
                "",
                "# Re-export from new locations",
                "from src.shared_kernel.domain.entities.base import *",
                "from src.shared_kernel.application.services import *",
            ]),
            ("apps/__init__.py", [
                "# Compatibility layer - deprecated", 
                "import warnings",
                "warnings.warn('apps/ imports are deprecated, use src/ instead', DeprecationWarning)",
            ]),
            ("infra/__init__.py", [
                "# Compatibility layer - deprecated",
                "import warnings", 
                "warnings.warn('infra/ imports are deprecated, use src/ instead', DeprecationWarning)",
                "",
                "# Re-export from new locations",
                "from src.shared_kernel.infrastructure import *",
            ])
        ]
        
        for file_path, content_lines in compatibility_mappings:
            full_path = self.project_root / file_path
            full_path.parent.mkdir(exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write('\n'.join(content_lines))
            
            print(f"✅ Created compatibility layer: {file_path}")

def main():
    """Main migration function"""
    import argparse
    parser = argparse.ArgumentParser(description="Migrate files to src/ architecture")
    parser.add_argument("--execute", action="store_true", help="Actually perform migration (default is dry-run)")
    args = parser.parse_args()
    
    migrator = FileMigrator(".")
    
    print("🚀 Starting file migration to src/ architecture")
    print("=" * 50)
    
    # Step 1: Create directory structure
    migrator.create_target_structure()
    
    # Step 2: Migrate files
    if args.execute:
        print("\n📦 Executing file migration...")
        migrated = migrator.migrate_files(dry_run=False)
        
        # Step 3: Create compatibility layers
        print("\n🔗 Creating compatibility layers...")
        migrator.create_compatibility_layers()
        
        print(f"\n✅ Migration complete! Moved {migrated} items")
        
        # Check for remaining files that weren't migrated
        print("\n🔍 Checking for remaining files...")
        remaining = migrator.check_remaining_files()
        
        total_remaining = sum(len(files) for files in remaining.values())
        if total_remaining > 0:
            print(f"⚠️ Found {total_remaining} files not migrated:")
            for directory, files in remaining.items():
                if files:
                    print(f"\n📂 {directory}/ ({len(files)} files):")
                    for file in files[:5]:  # Show first 5
                        print(f"   • {file}")
                    if len(files) > 5:
                        print(f"   ... and {len(files) - 5} more")
            
            print("\n💡 These files may need manual migration or removal.")
        else:
            print("✅ All files successfully migrated!")
    else:
        print("\n📋 DRY RUN - showing what would be migrated:")
        migrated = migrator.migrate_files(dry_run=True)
        print(f"\nWould migrate {migrated} items. Run with --execute to perform migration.")

if __name__ == "__main__":
    main()