#!/usr/bin/env python3
"""
Complete Migration Plan - Fix the incomplete migration properly
"""

import shutil
import os
from pathlib import Path

def complete_migration():
    """Complete the migration properly for Module Monolith architecture"""
    
    print("🔧 COMPLETING MODULE MONOLITH MIGRATION")
    print("=" * 60)
    
    # Phase 1: Move core infrastructure to shared_kernel
    print("\n📦 Phase 1: Move Core Infrastructure")
    
    moves_phase1 = [
        ("core/protocols.py", "src/shared_kernel/domain/protocols.py"),
        ("core/di_container.py", "src/shared_kernel/infrastructure/di_container.py"),
        ("core/common_helpers/", "src/shared_kernel/infrastructure/common_helpers/"),
        ("core/common/", "src/shared_kernel/infrastructure/common/"),
    ]
    
    for src_path, dst_path in moves_phase1:
        if os.path.exists(src_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.move(src_path, dst_path)
            else:
                shutil.move(src_path, dst_path)
            print(f"   ✅ Moved {src_path} → {dst_path}")
    
    # Phase 2: Distribute infra components to appropriate modules
    print("\n📦 Phase 2: Distribute Infrastructure Components")
    
    # Database repositories to appropriate modules
    db_migrations = [
        ("infra/db/repositories/user_repository.py", "src/identity/infrastructure/persistence/"),
        ("infra/db/repositories/admin_repository.py", "src/identity/infrastructure/persistence/"),
        ("infra/db/repositories/analytics_repository.py", "src/analytics/infrastructure/persistence/"),
        ("infra/db/repositories/payment_repository.py", "src/payments/infrastructure/persistence/"),
        ("infra/db/repositories/schedule_repository.py", "src/scheduling/infrastructure/persistence/"),
        ("infra/db/repositories/delivery_repository.py", "src/scheduling/infrastructure/persistence/"),
        ("infra/db/repositories/channel_repository.py", "src/channels/infrastructure/persistence/"),
    ]
    
    for src_file, dst_dir in db_migrations:
        if os.path.exists(src_file):
            os.makedirs(dst_dir, exist_ok=True)
            dst_file = os.path.join(dst_dir, os.path.basename(src_file))
            shutil.move(src_file, dst_file)
            print(f"   ✅ Moved {src_file} → {dst_file}")
    
    # Phase 3: Create legacy folder for deprecated components
    print("\n📦 Phase 3: Create Legacy Components Folder")
    
    legacy_dir = "src/legacy"
    os.makedirs(legacy_dir, exist_ok=True)
    
    legacy_items = [
        "infra/celery/",
        "infra/common/",
        "infra/obs/",
        "infra/email/",
        "infra/cache/", 
    ]
    
    for item in legacy_items:
        if os.path.exists(item):
            dst_path = os.path.join(legacy_dir, os.path.basename(item))
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.move(item, dst_path)
            print(f"   ✅ Moved {item} → {dst_path}")
    
    # Phase 4: Create shared infrastructure
    print("\n📦 Phase 4: Create Shared Infrastructure")
    
    shared_infra_moves = [
        ("infra/db/connection_manager.py", "src/shared_kernel/infrastructure/database/connection_manager.py"),
        ("infra/db/alembic/", "src/shared_kernel/infrastructure/database/alembic/"),
    ]
    
    for src_path, dst_path in shared_infra_moves:
        if os.path.exists(src_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.move(src_path, dst_path)
            else:
                shutil.move(src_path, dst_path)
            print(f"   ✅ Moved {src_path} → {dst_path}")

def main():
    print("⚠️  CRITICAL: This will complete the incomplete migration")
    print("⚠️  Make sure to backup your work before proceeding")
    response = input("\nProceed with complete migration? (yes/no): ")
    
    if response.lower() == 'yes':
        complete_migration()
        print("\n🎉 Complete migration finished!")
        print("📝 Next: Update imports and test thoroughly")
    else:
        print("❌ Migration cancelled")

if __name__ == "__main__":
    main()