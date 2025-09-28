#!/usr/bin/env python3
"""
Fix All Imports - Correct imports for Module Monolith architecture
"""

import os
from pathlib import Path


def fix_module_monolith_imports():
    """Fix all imports to work with Module Monolith architecture"""

    print("🔧 FIXING IMPORTS FOR MODULE MONOLITH ARCHITECTURE")
    print("=" * 60)

    # Import mapping for Module Monolith
    import_mappings = {
        # Core infrastructure moved to shared kernel
        "from core.protocols import": "from src.shared_kernel.domain.protocols import",
        "from core.di_container import": "from src.shared_kernel.infrastructure.di_container import",
        "from core.common_helpers": "from src.shared_kernel.infrastructure.common_helpers",
        "from core.common": "from src.shared_kernel.infrastructure.common",
        # Database repositories to modules
        "from infra.db.repositories.user_repository": "from src.identity.infrastructure.persistence.user_repository",
        "from infra.db.repositories.admin_repository": "from src.identity.infrastructure.persistence.admin_repository",
        "from infra.db.repositories.analytics_repository": "from src.analytics.infrastructure.persistence.analytics_repository",
        "from infra.db.repositories.payment_repository": "from src.payments.infrastructure.persistence.payment_repository",
        "from infra.db.repositories.schedule_repository": "from src.scheduling.infrastructure.persistence.schedule_repository",
        "from infra.db.repositories.channel_repository": "from src.channels.infrastructure.persistence.channel_repository",
        # Database connection to shared kernel
        "from infra.db.connection_manager": "from src.shared_kernel.infrastructure.database.connection_manager",
        # Legacy components
        "from infra.celery": "from src.legacy.celery",
        "from infra.cache": "from src.legacy.cache",
        "from infra.email": "from src.legacy.email",
        "from infra.obs": "from src.legacy.obs",
    }

    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip .git, __pycache__, .venv directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__" and d != "venv"]
        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)

    files_updated = 0
    total_replacements = 0

    for file_path in python_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            file_replacements = 0

            # Apply import mappings
            for old_import, new_import in import_mappings.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    file_replacements += content.count(new_import) - original_content.count(
                        new_import
                    )

            # Write back if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                files_updated += 1
                total_replacements += file_replacements
                print(f"   ✅ Updated {file_path} ({file_replacements} imports)")

        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")

    print("\n📊 IMPORT FIX SUMMARY:")
    print(f"   • Files updated: {files_updated}")
    print(f"   • Total import replacements: {total_replacements}")


if __name__ == "__main__":
    fix_module_monolith_imports()
