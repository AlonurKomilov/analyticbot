#!/usr/bin/env python3
"""
Legacy ML Services Migration Script
==================================

Professional migration script to safely transition from legacy ML services
to the new core-based architecture.

Migration Steps:
1. Backup legacy services
2. Update import references
3. Test new adapters
4. Archive legacy code
5. Verify system functionality

Safety Features:
- Rollback capability
- Comprehensive testing
- Backup preservation
- Gradual migration
"""

import asyncio
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MLServicesMigrator:
    """Professional ML services migration manager"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = (
            self.project_root
            / "archive"
            / f"legacy_ml_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.legacy_ml_dir = self.project_root / "apps" / "bot" / "services" / "ml"

        # Migration tracking
        self.migration_log = []
        self.rollback_actions = []

    def log_action(self, action: str, details: str = ""):
        """Log migration action"""
        entry = {"timestamp": datetime.now().isoformat(), "action": action, "details": details}
        self.migration_log.append(entry)
        logger.info(f"📝 {action}: {details}")

    def add_rollback_action(self, action: callable, description: str):
        """Add rollback action"""
        self.rollback_actions.append({"action": action, "description": description})

    async def phase_1_backup_legacy_services(self) -> bool:
        """Phase 1: Create comprehensive backup of legacy services"""
        try:
            self.log_action("PHASE_1_START", "Backing up legacy ML services")

            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            self.log_action("BACKUP_DIR_CREATED", str(self.backup_dir))

            # Backup ML services directory
            if self.legacy_ml_dir.exists():
                backup_ml_dir = self.backup_dir / "ml_services"
                shutil.copytree(self.legacy_ml_dir, backup_ml_dir)
                self.log_action("ML_SERVICES_BACKED_UP", f"Copied to {backup_ml_dir}")

                # List backed up files
                backed_up_files = list(backup_ml_dir.rglob("*.py"))
                self.log_action(
                    "BACKUP_FILES_COUNT", f"{len(backed_up_files)} Python files backed up"
                )

                for file in backed_up_files:
                    lines = len(file.read_text().splitlines())
                    self.log_action("BACKUP_FILE", f"{file.name} ({lines} lines)")

            # Backup related files that import ML services
            import_references = self._find_ml_import_references()
            if import_references:
                refs_backup_dir = self.backup_dir / "import_references"
                refs_backup_dir.mkdir(exist_ok=True)

                for file_path in import_references:
                    rel_path = file_path.relative_to(self.project_root)
                    backup_file = refs_backup_dir / f"{rel_path.as_posix().replace('/', '_')}"
                    shutil.copy2(file_path, backup_file)
                    self.log_action("REFERENCE_BACKED_UP", str(rel_path))

            self.log_action("PHASE_1_COMPLETE", "All legacy services backed up successfully")
            return True

        except Exception as e:
            self.log_action("PHASE_1_ERROR", f"Backup failed: {str(e)}")
            return False

    def _find_ml_import_references(self) -> list[Path]:
        """Find all files that import legacy ML services"""
        references = []
        search_patterns = ["from apps.bot.services.ml", "import apps.bot.services.ml"]

        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text()
                if any(pattern in content for pattern in search_patterns):
                    references.append(py_file)
            except Exception:
                pass

        return references

    async def phase_2_test_new_adapters(self) -> bool:
        """Phase 2: Test new ML adapter services"""
        try:
            self.log_action("PHASE_2_START", "Testing new ML adapter services")

            # Test ML coordinator import
            sys.path.insert(0, str(self.project_root))

            try:
                from apps.bot.services.ml_coordinator import (
                    create_ml_coordinator,
                )

                self.log_action("ADAPTER_IMPORT_SUCCESS", "ML Coordinator imported successfully")
            except Exception as e:
                self.log_action("ADAPTER_IMPORT_ERROR", f"ML Coordinator import failed: {e}")
                return False

            try:
                from apps.bot.services.bot_ml_facade import create_bot_ml_facade

                self.log_action("FACADE_IMPORT_SUCCESS", "Bot ML Facade imported successfully")
            except Exception as e:
                self.log_action("FACADE_IMPORT_ERROR", f"Bot ML Facade import failed: {e}")
                return False

            # Test core services availability
            core_services = [
                ("ai_insights_fusion", "core.services.ai_insights_fusion"),
                ("predictive_intelligence", "core.services.predictive_intelligence"),
                ("optimization_fusion", "core.services.optimization_fusion"),
                ("deep_learning_engagement", "core.services.deep_learning.engagement"),
                ("deep_learning_content", "core.services.deep_learning.content"),
            ]

            for service_name, module_path in core_services:
                try:
                    __import__(module_path)
                    self.log_action("CORE_SERVICE_OK", f"{service_name} available")
                except Exception as e:
                    self.log_action("CORE_SERVICE_ERROR", f"{service_name} failed: {e}")
                    return False

            # Test adapter instantiation
            try:
                coordinator = create_ml_coordinator()
                self.log_action("COORDINATOR_CREATED", "ML Coordinator instantiated successfully")

                facade = create_bot_ml_facade()
                self.log_action("FACADE_CREATED", "Bot ML Facade instantiated successfully")

                # Test health check
                health = await coordinator.health_check()
                self.log_action("HEALTH_CHECK", f"Status: {health.get('status', 'unknown')}")

            except Exception as e:
                self.log_action("ADAPTER_TEST_ERROR", f"Adapter testing failed: {e}")
                return False

            self.log_action("PHASE_2_COMPLETE", "New adapters tested successfully")
            return True

        except Exception as e:
            self.log_action("PHASE_2_ERROR", f"Adapter testing failed: {str(e)}")
            return False

    async def phase_3_update_import_references(self) -> bool:
        """Phase 3: Update import references to use new adapters"""
        try:
            self.log_action("PHASE_3_START", "Updating import references")

            import_references = self._find_ml_import_references()

            for file_path in import_references:
                # Backup original before modification
                backup_file = self.backup_dir / "import_references" / f"{file_path.name}.original"
                shutil.copy2(file_path, backup_file)
                self.add_rollback_action(
                    lambda: shutil.copy2(backup_file, file_path), f"Restore {file_path}"
                )

                # Update imports
                updated = self._update_file_imports(file_path)
                if updated:
                    self.log_action(
                        "IMPORTS_UPDATED", str(file_path.relative_to(self.project_root))
                    )
                else:
                    self.log_action(
                        "IMPORTS_UNCHANGED", str(file_path.relative_to(self.project_root))
                    )

            self.log_action("PHASE_3_COMPLETE", f"Updated {len(import_references)} files")
            return True

        except Exception as e:
            self.log_action("PHASE_3_ERROR", f"Import update failed: {str(e)}")
            return False

    def _update_file_imports(self, file_path: Path) -> bool:
        """Update ML imports in a single file"""
        try:
            content = file_path.read_text()
            original_content = content

            # Define import replacements
            replacements = {
                # Legacy → New adapter
                "from apps.bot.services.bot_ml_facade import create_bot_ml_facade": "from apps.bot.services.bot_ml_facade import create_bot_ml_facade",
                "from apps.bot.services.ml_coordinator import create_ml_coordinator": "from apps.bot.services.ml_coordinator import create_ml_coordinator",
                "from apps.bot.services.bot_ml_facade import create_bot_ml_facade": "from apps.bot.services.bot_ml_facade import create_bot_ml_facade",
                "from apps.bot.services.bot_ml_facade import create_bot_ml_facade": "from apps.bot.services.bot_ml_facade import create_bot_ml_facade",
                "# TODO: Implement churn prediction in core services": "# TODO: Implement churn prediction in core services",
                # Class usage replacements
                "# Use create_ml_coordinator() instead": "# Use create_ml_coordinator() instead",
                "# Use create_bot_ml_facade() instead": "# Use create_bot_ml_facade() instead",
                "# Use create_bot_ml_facade() instead": "# Use create_bot_ml_facade() instead",
                "# Use create_bot_ml_facade() instead": "# Use create_bot_ml_facade() instead",
            }

            for old_import, new_import in replacements.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)

            # Write updated content
            if content != original_content:
                file_path.write_text(content)
                return True

            return False

        except Exception as e:
            self.log_action("IMPORT_UPDATE_ERROR", f"Failed to update {file_path}: {e}")
            return False

    async def phase_4_archive_legacy_services(self) -> bool:
        """Phase 4: Archive legacy ML services"""
        try:
            self.log_action("PHASE_4_START", "Archiving legacy ML services")

            if self.legacy_ml_dir.exists():
                # Create archive directory in project
                archive_dir = self.project_root / "archive" / "legacy_ml_services"
                archive_dir.mkdir(parents=True, exist_ok=True)

                # Move legacy services to archive
                for item in self.legacy_ml_dir.iterdir():
                    if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                        archive_path = archive_dir / f"legacy_{item.name}"
                        shutil.move(str(item), str(archive_path))
                        self.log_action("ARCHIVED", f"{item.name} → {archive_path.name}")

                        # Add rollback action
                        self.add_rollback_action(
                            lambda: shutil.move(str(archive_path), str(item)),
                            f"Restore {item.name}",
                        )

                # Create empty __init__.py with deprecation notice
                init_file = self.legacy_ml_dir / "__init__.py"
                init_content = '''"""
Legacy ML Services - DEPRECATED
===============================

These services have been migrated to core microservices architecture.

New Usage:
    from apps.bot.services.ml_coordinator import create_ml_coordinator
    from apps.bot.services.bot_ml_facade import create_bot_ml_facade

Migration Date: {}
Archived Location: archive/legacy_ml_services/
"""\n\n# Legacy imports are deprecated\nraise ImportError("Legacy ML services have been migrated to core. Use ml_coordinator or bot_ml_facade instead.")
'''.format(datetime.now().strftime("%Y-%m-%d"))

                init_file.write_text(init_content)
                self.log_action("DEPRECATION_NOTICE", "Added to ml/__init__.py")

            self.log_action("PHASE_4_COMPLETE", "Legacy services archived successfully")
            return True

        except Exception as e:
            self.log_action("PHASE_4_ERROR", f"Archiving failed: {str(e)}")
            return False

    async def phase_5_verification(self) -> bool:
        """Phase 5: Verify migration success"""
        try:
            self.log_action("PHASE_5_START", "Verifying migration success")

            # Test new adapters work
            from apps.bot.services.bot_ml_facade import create_bot_ml_facade
            from apps.bot.services.ml_coordinator import create_ml_coordinator

            coordinator = create_ml_coordinator()
            facade = create_bot_ml_facade()

            # Test basic functionality
            health = await coordinator.health_check()
            self.log_action("COORDINATOR_HEALTH", f"Status: {health.get('status')}")

            # Test facade
            status = await facade.get_service_status()
            self.log_action("FACADE_STATUS", f"Success: {status.get('success')}")

            # Verify legacy imports fail appropriately
            try:
                import apps.bot.services.ml.ai_insights

                self.log_action(
                    "LEGACY_IMPORT_WARNING", "Legacy import still works - check deprecation"
                )
            except ImportError:
                self.log_action("LEGACY_IMPORT_BLOCKED", "Legacy imports properly blocked")

            self.log_action("PHASE_5_COMPLETE", "Migration verification successful")
            return True

        except Exception as e:
            self.log_action("PHASE_5_ERROR", f"Verification failed: {str(e)}")
            return False

    async def execute_migration(self) -> bool:
        """Execute complete migration process"""
        try:
            self.log_action("MIGRATION_START", "Starting professional ML services migration")

            # Phase 1: Backup
            if not await self.phase_1_backup_legacy_services():
                self.log_action("MIGRATION_FAILED", "Phase 1 backup failed")
                return False

            # Phase 2: Test adapters
            if not await self.phase_2_test_new_adapters():
                self.log_action("MIGRATION_FAILED", "Phase 2 adapter testing failed")
                return False

            # Phase 3: Update imports
            if not await self.phase_3_update_import_references():
                self.log_action("MIGRATION_FAILED", "Phase 3 import updates failed")
                await self.rollback()
                return False

            # Phase 4: Archive legacy
            if not await self.phase_4_archive_legacy_services():
                self.log_action("MIGRATION_FAILED", "Phase 4 archiving failed")
                await self.rollback()
                return False

            # Phase 5: Verification
            if not await self.phase_5_verification():
                self.log_action("MIGRATION_FAILED", "Phase 5 verification failed")
                await self.rollback()
                return False

            self.log_action("MIGRATION_SUCCESS", "All phases completed successfully")
            self._save_migration_report()
            return True

        except Exception as e:
            self.log_action("MIGRATION_CRITICAL_ERROR", f"Critical migration error: {str(e)}")
            await self.rollback()
            return False

    async def rollback(self):
        """Rollback migration changes"""
        self.log_action("ROLLBACK_START", "Rolling back migration changes")

        for rollback_action in reversed(self.rollback_actions):
            try:
                rollback_action["action"]()
                self.log_action("ROLLBACK_ACTION", rollback_action["description"])
            except Exception as e:
                self.log_action(
                    "ROLLBACK_ERROR", f"Failed to rollback {rollback_action['description']}: {e}"
                )

        self.log_action("ROLLBACK_COMPLETE", "Migration rollback completed")

    def _save_migration_report(self):
        """Save detailed migration report"""
        report_file = self.backup_dir / "migration_report.json"
        import json

        report = {
            "migration_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "backup_location": str(self.backup_dir),
            "migration_log": self.migration_log,
            "summary": {
                "total_actions": len(self.migration_log),
                "success": True,
                "legacy_services_archived": True,
                "new_adapters_active": True,
            },
        }

        report_file.write_text(json.dumps(report, indent=2))
        self.log_action("REPORT_SAVED", str(report_file))


async def main():
    """Main migration execution"""
    project_root = "/home/abcdeveloper/projects/analyticbot"

    migrator = MLServicesMigrator(project_root)

    print("🚀 Starting Professional ML Services Migration")
    print("=" * 50)

    success = await migrator.execute_migration()

    if success:
        print("\n✅ Migration completed successfully!")
        print(f"📁 Backup location: {migrator.backup_dir}")
        print("📊 New services ready for use:")
        print("   - apps.bot.services.ml_coordinator")
        print("   - apps.bot.services.bot_ml_facade")
    else:
        print("\n❌ Migration failed - check logs")
        print(f"📁 Backup preserved at: {migrator.backup_dir}")

    return success


if __name__ == "__main__":
    asyncio.run(main())
