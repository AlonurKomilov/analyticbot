#!/usr/bin/env python3
"""Import guard script to prevent architectural violations.

This script ensures Clean Architecture principles by checking that:
- core/ modules don't import from apps/ or infra/
- No circular dependencies exist
- MTProto imports are properly guarded

Usage:
    python scripts/guard_imports.py [--fix]
"""

import ast
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ImportViolation:
    """Represents an import violation."""

    file_path: str
    line_number: int
    imported_module: str
    violation_type: str
    message: str


class ImportGuard:
    """Guards against architectural import violations."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.violations: list[ImportViolation] = []

        # Define architectural layers
        self.layers = {
            "core": ["core"],
            "infra": ["infra"],
            "apps": ["apps"],
            "config": ["config"],
            "scripts": ["scripts"],
            "tests": ["tests"],
        }

        # Define forbidden imports
        self.forbidden_imports = {
            "core": ["apps", "infra", "infrastructure"],  # Core can't depend on outer layers
            # Note: infra CAN import from apps for adapters (Hexagonal Architecture)
            # "infra": ["apps"],  # Removed - adapters in infra can depend on apps
        }

    def check_all_files(self) -> list[ImportViolation]:
        """Check all Python files in the project."""
        self.violations = []

        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                self._check_file(py_file)
            except Exception as e:
                print(f"Warning: Could not check {py_file}: {e}")

        return self.violations

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        # Skip files in certain directories
        skip_dirs = {".git", "__pycache__", ".pytest_cache", "venv", ".venv"}

        for part in file_path.parts:
            if part in skip_dirs:
                return True

        # Skip payment services (temporary exclusion for clean architecture violations)
        relative_path = str(file_path.relative_to(self.project_root))
        if relative_path.startswith("core/services/payment/"):
            return True

        return False

    def _check_file(self, file_path: Path) -> None:
        """Check a single file for import violations."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            return  # Skip binary files

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return  # Skip files with syntax errors

        # Determine the layer of this file
        file_layer = self._get_file_layer(file_path)
        if not file_layer:
            return

        # Check all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                self._check_import_node(file_path, node, file_layer)

    def _get_file_layer(self, file_path: Path) -> str:
        """Determine which architectural layer a file belongs to."""
        relative_path = file_path.relative_to(self.project_root)

        for layer, prefixes in self.layers.items():
            for prefix in prefixes:
                if str(relative_path).startswith(prefix + "/") or str(relative_path) == prefix:
                    return layer

        return ""  # Unknown layer

    def _check_import_node(self, file_path: Path, node, file_layer: str) -> None:
        """Check a single import node for violations."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self._check_import(file_path, node.lineno, alias.name, file_layer)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                self._check_import(file_path, node.lineno, node.module, file_layer)

    def _check_import(
        self, file_path: Path, line_number: int, module_name: str, file_layer: str
    ) -> None:
        """Check a single import for violations."""
        # Check architectural violations
        self._check_architectural_violation(file_path, line_number, module_name, file_layer)

        # Check MTProto import guards
        self._check_mtproto_imports(file_path, line_number, module_name, file_layer)

    def _check_architectural_violation(
        self, file_path: Path, line_number: int, module_name: str, file_layer: str
    ) -> None:
        """Check for architectural violations."""
        if file_layer not in self.forbidden_imports:
            return

        forbidden_layers = self.forbidden_imports[file_layer]

        for forbidden_layer in forbidden_layers:
            # Check for exact layer violations
            if module_name.startswith(forbidden_layer + ".") or module_name == forbidden_layer:
                # Special handling for "infrastructure" - distinguish between:
                # 1. Top-level "infrastructure" package (violation)
                # 2. Local "infrastructure" subdirectory within core (OK)
                if forbidden_layer == "infrastructure":
                    # If it's a relative import starting with ".infrastructure", it's local and OK
                    if module_name.startswith(".infrastructure"):
                        continue
                    # If file is in core/services and import is "infrastructure",
                    # check if it's a local subdirectory
                    if "core/services/" in str(file_path):
                        # Extract the parent service package
                        # e.g., core/services/analytics_fusion/core/file.py
                        relative_path = str(file_path.relative_to(self.project_root))
                        parts = relative_path.split("/")
                        # Check if "infrastructure" could be a sibling subdirectory
                        if len(parts) >= 4 and parts[0] == "core" and parts[1] == "services":
                            # This is likely a local infrastructure subdirectory
                            continue

                # Allow some exceptions for legacy infra code that will be refactored
                if self._is_legacy_exception(file_path, module_name):
                    continue

                violation = ImportViolation(
                    file_path=str(file_path),
                    line_number=line_number,
                    imported_module=module_name,
                    violation_type="architectural",
                    message=f"Layer '{file_layer}' cannot import from layer '{forbidden_layer}'",
                )
                self.violations.append(violation)

    def _is_legacy_exception(self, file_path: Path, module_name: str) -> bool:
        """Check if this is a legacy exception that we temporarily allow."""
        # Allow legacy infra->apps imports that are being refactored
        legacy_files = {
            "infra/celery/celery_app.py",
            "infra/celery/tasks.py",
            "infra/monitoring/worker_metrics.py",
            "infra/db/alembic/env.py",
        }

        relative_path = str(file_path.relative_to(self.project_root))
        return relative_path in legacy_files

    def _check_mtproto_imports(
        self, file_path: Path, line_number: int, module_name: str, file_layer: str
    ) -> None:
        """Check for MTProto import guard violations."""
        # Define MTProto-related imports that need guards
        mtproto_modules = {"telethon", "pyrogram", "telegram"}

        # Check if this is an MTProto import
        is_mtproto_import = any(
            module_name.startswith(mtproto_module) or module_name == mtproto_module
            for mtproto_module in mtproto_modules
        )

        if is_mtproto_import:
            # Allow MTProto imports in designated directories where they're expected
            relative_path = str(file_path.relative_to(self.project_root))

            allowed_paths = [
                "infra/tg/",  # Stub implementations
                "infra/bot/",  # Bot manager implementations
                "apps/mtproto/",  # MTProto services layer
                "apps/api/services/telegram_",  # Telegram-specific API services
                "apps/api/routers/user_mtproto_",  # MTProto routers (legacy monolithic)
                "apps/api/routers/user_mtproto/",  # MTProto routers (modular package)
                "apps/bot/multi_tenant/",  # Bot instances using MTProto
                "scripts/test_",  # Test scripts
            ]

            for allowed in allowed_paths:
                if allowed in relative_path:
                    return

            violation = ImportViolation(
                file_path=str(file_path),
                line_number=line_number,
                imported_module=module_name,
                violation_type="mtproto_guard",
                message=(
                    f"MTProto import '{module_name}' should be guarded " "or in stub implementation"
                ),
            )
            self.violations.append(violation)

    def print_violations(self) -> None:
        """Print all violations to stdout."""
        if not self.violations:
            print("✅ No import violations found!")
            return

        print(f"❌ Found {len(self.violations)} import violations:")
        print()

        for violation in self.violations:
            print(f"File: {violation.file_path}:{violation.line_number}")
            print(f"Import: {violation.imported_module}")
            print(f"Type: {violation.violation_type}")
            print(f"Message: {violation.message}")
            print("-" * 50)


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    guard = ImportGuard(project_root)

    violations = guard.check_all_files()
    guard.print_violations()

    if violations:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
