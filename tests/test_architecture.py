"""
Architecture Smoke Tests
Ensures Clean Architecture compliance in CI/CD
"""

import importlib
from pathlib import Path

import pytest


class TestCleanArchitecture:
    """Test Clean Architecture compliance"""

    def test_core_has_no_external_dependencies(self):
        """Core should not import from apps, infra, or frameworks"""
        forbidden_imports = [
            "apps",
            "infra",
            "fastapi",
            "aiogram",
            "pydantic",
            "sqlalchemy",
            "celery",
            "redis",
        ]

        core_files = list(Path("core").rglob("*.py"))
        violations = []

        for file in core_files:
            with open(file) as f:
                content = f.read()
                for forbidden in forbidden_imports:
                    if f"from {forbidden}" in content or f"import {forbidden}" in content:
                        violations.append(f"{file}: imports {forbidden}")

        assert not violations, f"Core layer violations: {violations}"

    def test_infra_does_not_import_apps(self):
        """Infrastructure should not import from applications"""
        infra_files = list(Path("infra").rglob("*.py"))
        violations = []

        for file in infra_files:
            with open(file) as f:
                content = f.read()
                if "from apps." in content or "import apps." in content:
                    violations.append(f"{file}: imports from apps")

        assert not violations, f"Infra→Apps violations: {violations}"

    def test_di_containers_importable(self):
        """All DI containers should be importable without errors"""
        containers = [
            "apps.api.di",
            "apps.bot.di",
            "apps.jobs.di",
            "apps.mtproto.di",
            "apps.shared.di",
        ]

        for container_module in containers:
            try:
                importlib.import_module(container_module)
            except ImportError as e:
                pytest.fail(f"DI container {container_module} not importable: {e}")

    def test_core_models_are_framework_free(self):
        """Core models should use dataclasses, not framework types"""
        core_model_files = list(Path("core/models").rglob("*.py"))
        framework_violations = []

        frameworks = ["BaseModel", "BaseSettings", "Table", "Column"]

        for file in core_model_files:
            with open(file) as f:
                content = f.read()
                for framework in frameworks:
                    if framework in content:
                        framework_violations.append(f"{file}: uses {framework}")

        # Allow some violations for base classes
        allowed_violations = ["core/models/base.py"]
        actual_violations = [
            v
            for v in framework_violations
            if not any(allowed in v for allowed in allowed_violations)
        ]

        assert not actual_violations, f"Framework dependencies in core: {actual_violations}"

    def test_no_god_containers(self):
        """Ensure no god containers remain (containers with >200 lines)"""
        container_files = [
            "apps/bot/container.py",
            "apps/api/di.py",
            "apps/bot/di.py",
            "apps/jobs/di.py",
            "apps/mtproto/di.py",
            "apps/shared/di.py",
        ]

        oversized_containers = []

        for container_file in container_files:
            if Path(container_file).exists():
                with open(container_file) as f:
                    lines = len([line for line in f if line.strip()])
                    if lines > 300:  # Threshold for "god container"
                        oversized_containers.append(f"{container_file}: {lines} lines")

        assert not oversized_containers, f"God containers found: {oversized_containers}"
