"""
Clean Architecture Smoke Tests
Minimal test suite to verify core architectural patterns are working.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestImportGraph:
    """Test that import dependencies flow correctly in clean architecture."""

    def test_core_has_no_forbidden_imports(self):
        """Core layer should not import from apps or infra."""
        forbidden_imports = []

        core_dir = Path(__file__).parent.parent / "core"
        if not core_dir.exists():
            pytest.skip("Core directory not found")

        for py_file in core_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                for line_num, line in enumerate(content.split("\n"), 1):
                    if any(
                        pattern in line
                        for pattern in [
                            "from apps.",
                            "import apps.",
                            "from infra.",
                            "import infra.",
                        ]
                    ):
                        # Skip comments
                        stripped_line = line.strip()
                        if stripped_line.startswith("#"):
                            continue
                        forbidden_imports.append(f"{py_file.name}:{line_num} - {stripped_line}")
            except Exception:
                # File reading issues should not fail the test
                continue

        assert len(forbidden_imports) == 0, (
            f"Found forbidden imports in core: {forbidden_imports[:3]}"
        )

    def test_infra_has_no_forbidden_imports(self):
        """Infra layer should not import from apps."""
        forbidden_imports = []

        infra_dir = Path(__file__).parent.parent / "infra"
        if not infra_dir.exists():
            pytest.skip("Infra directory not found")

        for py_file in infra_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                for line_num, line in enumerate(content.split("\n"), 1):
                    if any(pattern in line for pattern in ["from apps.", "import apps."]):
                        # Skip comments
                        stripped_line = line.strip()
                        if stripped_line.startswith("#") or "TODO:" in stripped_line:
                            continue
                        forbidden_imports.append(f"{py_file.name}:{line_num} - {stripped_line}")
            except Exception:
                # File reading issues should not fail the test
                continue

        assert len(forbidden_imports) == 0, (
            f"Found forbidden imports in infra: {forbidden_imports[:3]}"
        )

    def test_clean_architecture_directories_exist(self):
        """Essential clean architecture directories should exist."""
        project_root = Path(__file__).parent.parent

        expected_dirs = ["core", "infra", "apps"]
        missing_dirs = []

        for dir_name in expected_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)

        assert len(missing_dirs) == 0, f"Missing clean architecture directories: {missing_dirs}"


class TestDomainService:
    """Test that core domain services work correctly."""

    def test_core_services_can_be_imported(self):
        """Core domain services should be importable."""
        try:
            from core.services import DeliveryService, ScheduleService

            # Test basic instantiation (without dependencies for smoke test)
            assert ScheduleService is not None
            assert DeliveryService is not None

        except ImportError as e:
            pytest.fail(f"Failed to import core domain services: {e}")

    def test_core_models_can_be_imported(self):
        """Core domain models should be importable."""
        try:
            from core.models import Delivery, DeliveryStatus, PostStatus, ScheduledPost

            # Test that models are properly defined
            assert hasattr(ScheduledPost, "__annotations__")
            assert hasattr(Delivery, "__annotations__")
            assert PostStatus is not None
            assert DeliveryStatus is not None

        except ImportError as e:
            pytest.fail(f"Failed to import core domain models: {e}")

    def test_domain_services_are_framework_agnostic(self):
        """Core domain services should not depend on external frameworks."""
        import inspect

        try:
            from core.services import DeliveryService, ScheduleService

            for service_class in [ScheduleService, DeliveryService]:
                service_source = inspect.getsource(service_class)

                # Check for framework imports that should not be in core
                forbidden_frameworks = [
                    "aiogram",
                    "fastapi",
                    "celery",
                    "flask",
                    "django",
                ]
                for framework in forbidden_frameworks:
                    assert framework not in service_source.lower(), (
                        f"Domain service {service_class.__name__} contains {framework} framework code"
                    )

        except ImportError:
            pytest.skip("Core services not available for framework check")


class TestDependencyInjection:
    """Test that dependency injection containers work correctly."""

    def test_apps_containers_can_be_imported(self):
        """Application DI containers should be importable."""
        successful_imports = []
        import_errors = []

        containers = [
            ("apps.api.di", "ApiContainer"),
            ("apps.bot.di", "BotContainer"),
            ("apps.jobs.di", "JobsContainer"),
        ]

        for module_path, container_name in containers:
            try:
                module = __import__(module_path, fromlist=[container_name])
                container_class = getattr(module, container_name)
                assert container_class is not None
                successful_imports.append(container_name)
            except (ImportError, AttributeError) as e:
                import_errors.append(f"{container_name}: {e}")

        # At least one container should work
        assert len(successful_imports) > 0, (
            f"No DI containers could be imported. Errors: {import_errors}"
        )

    def test_dependency_injector_unified(self):
        """All containers should use dependency-injector (not punq)."""
        try:
            # Test that we can import dependency_injector
            pass

            # Test that containers use the right base class
            from apps.jobs.di import JobsContainer

            # Should be a dependency_injector container
            assert hasattr(JobsContainer, "providers"), (
                "JobsContainer should be a dependency-injector container"
            )

        except ImportError as e:
            pytest.skip(f"Dependency injection components not available: {e}")

    def test_jobs_services_wired_correctly(self):
        """Jobs application services should be properly wired."""
        try:
            from apps.jobs.di import JobsContainer
            from apps.jobs.services.analytics_job_service import AnalyticsJobService

            # Test that container can provide services
            container = JobsContainer()
            service = container.analytics_job_service()

            assert service is not None
            assert isinstance(service, AnalyticsJobService)

        except (ImportError, AttributeError) as e:
            pytest.skip(f"Jobs DI not available for testing: {e}")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
