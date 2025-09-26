#!/usr/bin/env python3
"""
Complete Module Monolith Migration - Properly integrate remaining components
"""

import os
import shutil
from pathlib import Path

def complete_module_monolith_migration():
    """Complete migration respecting existing Module Monolith architecture"""
    
    print("🔧 COMPLETING MODULE MONOLITH MIGRATION")
    print("=" * 60)
    print("📋 Strategy: Integrate components into existing modular structure")
    print()
    
    # Phase 1: Move core infrastructure to shared_kernel (where it belongs)
    print("📦 Phase 1: Complete shared_kernel Infrastructure")
    
    shared_moves = [
        # DI Container should be in shared_kernel/infrastructure 
        ("core/di_container.py", "src/shared_kernel/infrastructure/di_container.py"),
        
        # Protocols should be in shared_kernel/domain
        ("core/protocols.py", "src/shared_kernel/domain/protocols.py"),
        
        # Common helpers to shared_kernel/infrastructure
        ("core/common_helpers/", "src/shared_kernel/infrastructure/common_helpers/"),
        ("core/common/", "src/shared_kernel/infrastructure/common/"),
    ]
    
    for src_path, dst_path in shared_moves:
        if os.path.exists(src_path):
            print(f"   📁 Moving {src_path} → {dst_path}")
            # Create destination directory
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            # Move the file/directory
            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                shutil.rmtree(src_path)
            else:
                shutil.move(src_path, dst_path)
            print(f"   ✅ Completed: {src_path} → {dst_path}")
    
    # Phase 2: Distribute database repositories to appropriate modules
    print(f"\n📦 Phase 2: Distribute Database Repositories to Modules")
    
    repo_distributions = [
        # Identity module repositories
        ("infra/db/repositories/user_repository.py", "src/identity/infrastructure/persistence/"),
        ("infra/db/repositories/admin_repository.py", "src/identity/infrastructure/persistence/"),
        
        # Analytics module repositories  
        ("infra/db/repositories/analytics_repository.py", "src/analytics/infrastructure/persistence/"),
        ("infra/db/repositories/reports_repository.py", "src/analytics/infrastructure/persistence/"),
        
        # Payments module repositories
        ("infra/db/repositories/payment_repository.py", "src/payments/infrastructure/persistence/"),
        ("infra/db/repositories/subscription_repository.py", "src/payments/infrastructure/persistence/"),
        
        # Scheduling module repositories
        ("infra/db/repositories/schedule_repository.py", "src/scheduling/infrastructure/persistence/"),
        ("infra/db/repositories/delivery_repository.py", "src/scheduling/infrastructure/persistence/"),
        
        # Channels module repositories
        ("infra/db/repositories/channel_repository.py", "src/channels/infrastructure/persistence/"),
        ("infra/db/repositories/telegram_repository.py", "src/channels/infrastructure/persistence/"),
        
        # Bot service repositories (if any specific ones exist)
        ("infra/db/repositories/bot_repository.py", "src/bot_service/infrastructure/persistence/"),
    ]
    
    for src_file, dst_dir in repo_distributions:
        if os.path.exists(src_file):
            print(f"   📁 Distributing {src_file} → {dst_dir}")
            os.makedirs(dst_dir, exist_ok=True)
            dst_file = os.path.join(dst_dir, os.path.basename(src_file))
            shutil.move(src_file, dst_file)
            print(f"   ✅ Completed: {src_file} → {dst_file}")
    
    # Phase 3: Move shared database infrastructure to shared_kernel
    print(f"\n📦 Phase 3: Move Shared Database Infrastructure")
    
    shared_db_moves = [
        # Database connection manager (shared across modules)
        ("infra/db/connection_manager.py", "src/shared_kernel/infrastructure/database/connection_manager.py"),
        
        # Database migrations (shared)
        ("infra/db/alembic/", "src/shared_kernel/infrastructure/database/alembic/"),
        
        # Base database classes (shared)
        ("infra/db/__init__.py", "src/shared_kernel/infrastructure/database/__init__.py"),
    ]
    
    for src_path, dst_path in shared_db_moves:
        if os.path.exists(src_path):
            print(f"   📁 Moving shared DB: {src_path} → {dst_path}")
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                shutil.rmtree(src_path)
            else:
                shutil.move(src_path, dst_path)
            print(f"   ✅ Completed: {src_path} → {dst_path}")
    
    # Phase 4: Handle cross-cutting concerns properly
    print(f"\n📦 Phase 4: Handle Cross-Cutting Concerns")
    
    cross_cutting_moves = [
        # Celery (background jobs) - could go to shared_kernel or specific modules
        ("infra/celery/", "src/shared_kernel/infrastructure/background_jobs/"),
        
        # Observability (monitoring) - shared concern
        ("infra/obs/", "src/shared_kernel/infrastructure/observability/"),
        
        # Email (if not already in shared_kernel)
        ("infra/email/", "src/shared_kernel/infrastructure/email/"),  # check if exists
        
        # Cache (if not already in shared_kernel) 
        ("infra/cache/", "src/shared_kernel/infrastructure/cache/"),  # check if exists
    ]
    
    for src_path, dst_path in cross_cutting_moves:
        if os.path.exists(src_path):
            # Check if already exists in shared_kernel
            existing_shared = Path(dst_path).name
            if os.path.exists(f"src/shared_kernel/infrastructure/{existing_shared}"):
                print(f"   ⚠️  {existing_shared} already exists in shared_kernel, skipping {src_path}")
                continue
                
            print(f"   📁 Moving cross-cutting: {src_path} → {dst_path}")
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                shutil.rmtree(src_path)
            else:
                shutil.move(src_path, dst_path)
            print(f"   ✅ Completed: {src_path} → {dst_path}")
    
    # Phase 5: Complete module structures for incomplete modules
    print(f"\n📦 Phase 5: Complete Module Structures")
    
    incomplete_modules = ["publishing", "security"]
    standard_layers = ["domain", "application", "infrastructure", "presentation"]
    
    for module in incomplete_modules:
        module_path = Path(f"src/{module}")
        if module_path.exists():
            print(f"   📂 Completing {module} module structure:")
            for layer in standard_layers:
                layer_path = module_path / layer
                if not layer_path.exists():
                    layer_path.mkdir(exist_ok=True)
                    (layer_path / "__init__.py").touch()
                    print(f"      ✅ Created {module}/{layer}/")
    
    print(f"\n🎉 MODULE MONOLITH MIGRATION COMPLETED!")
    print(f"📊 Next: Update imports and test integration")

def main():
    print("🚀 MODULE MONOLITH COMPLETION")
    print("⚠️  This will complete the migration by properly distributing components")
    print("⚠️  Existing src/ structure will be respected and enhanced")
    
    response = input("\nProceed with completing Module Monolith migration? (yes/no): ")
    
    if response.lower() == 'yes':
        complete_module_monolith_migration()
    else:
        print("❌ Migration cancelled")

if __name__ == "__main__":
    main()