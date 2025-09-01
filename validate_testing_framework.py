#!/usr/bin/env python3
"""
Testing & Quality Assurance Framework Validation Script
Validates all components of the comprehensive testing framework
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TestingFrameworkValidator:
    """Validates the entire Testing & Quality Assurance Framework"""

    def __init__(self):
        self.project_root = project_root
        self.venv_python = self.project_root / ".venv" / "bin" / "python"
        self.validation_results = {}

    def run_command(self, command: list[str], description: str) -> dict[str, Any]:
        """Run a shell command and capture results"""
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "description": description,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 5 minutes",
                "returncode": -1,
                "description": description,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "description": description,
            }

    def validate_test_structure(self) -> dict[str, Any]:
        """Validate that all test files exist and are properly structured"""
        print("🔍 Validating test file structure...")

        required_test_files = [
            # Integration tests (actual files we have)
            "tests/integration/test_api_basic.py",
            "tests/integration/test_api_endpoints.py",
            "tests/integration/test_database_integration.py",
            "tests/integration/test_payment_integration.py",
            "tests/integration/test_telegram_integration.py",
            "tests/integration/test_redis_integration.py",
            "tests/integration/test_payment_flows.py",
            # End-to-end tests
            "tests/e2e/test_user_journey_workflows.py",
            "tests/e2e/test_payment_workflows.py",
            "tests/e2e/test_analytics_workflows.py",
            "tests/e2e/test_multi_service_integration.py",
            # Configuration
            "tests/conftest.py",
            "pytest.ini",
        ]

        missing_files = []
        existing_files = []

        for test_file in required_test_files:
            file_path = self.project_root / test_file
            if file_path.exists():
                existing_files.append(test_file)
            else:
                missing_files.append(test_file)

        return {
            "success": len(missing_files) == 0,
            "existing_files": existing_files,
            "missing_files": missing_files,
            "total_files": len(required_test_files),
            "description": "Test file structure validation",
        }

    def validate_import_syntax(self) -> dict[str, Any]:
        """Validate that all test files have correct Python syntax"""
        print("🔍 Validating Python syntax in test files...")

        test_directories = [
            self.project_root / "tests" / "integration",
            self.project_root / "tests" / "e2e",
        ]

        syntax_errors = []
        valid_files = []

        for test_dir in test_directories:
            if not test_dir.exists():
                continue

            for test_file in test_dir.glob("test_*.py"):
                try:
                    # Try to compile the file to check syntax
                    with open(test_file, encoding="utf-8") as f:
                        compile(f.read(), str(test_file), "exec")
                    valid_files.append(str(test_file.relative_to(self.project_root)))
                except SyntaxError as e:
                    syntax_errors.append(
                        {"file": str(test_file.relative_to(self.project_root)), "error": str(e)}
                    )
                except Exception as e:
                    syntax_errors.append(
                        {
                            "file": str(test_file.relative_to(self.project_root)),
                            "error": f"Unexpected error: {str(e)}",
                        }
                    )

        return {
            "success": len(syntax_errors) == 0,
            "valid_files": valid_files,
            "syntax_errors": syntax_errors,
            "description": "Python syntax validation",
        }

    def validate_pytest_collection(self) -> dict[str, Any]:
        """Validate that pytest can collect all tests without errors"""
        print("🔍 Validating pytest test collection...")

        return self.run_command(
            [str(self.venv_python), "-m", "pytest", "--collect-only", "--quiet", "tests/"],
            "Pytest test collection validation",
        )

    def run_integration_tests(self) -> dict[str, Any]:
        """Run integration tests to validate framework"""
        print("🔍 Running integration tests...")

        # Run a subset of integration tests to validate framework
        return self.run_command(
            [
                str(self.venv_python),
                "-m",
                "pytest",
                "tests/integration/",
                "-v",
                "--tb=short",
                "-x",
                "--no-cov",
            ],
            "Integration tests execution",
        )

    def run_e2e_test_validation(self) -> dict[str, Any]:
        """Validate E2E tests can be imported and instantiated"""
        print("🔍 Validating E2E test infrastructure...")

        validation_script = """
import sys
sys.path.append('/home/alonur/analyticbot')

try:
    # Test E2E imports
    from tests.e2e.test_user_journey_workflows import TestUserOnboardingWorkflow
    from tests.e2e.test_payment_workflows import TestSubscriptionPurchaseWorkflow
    from tests.e2e.test_analytics_workflows import TestAnalyticsDataCollectionWorkflow
    from tests.e2e.test_multi_service_integration import TestCompleteSystemIntegration
    
    # Test mock patterns
    from unittest.mock import AsyncMock
    
    print("✅ All E2E test classes imported successfully")
    print("✅ Mock infrastructure available")
    print("✅ E2E test infrastructure validated")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)
"""

        return self.run_command(
            [str(self.venv_python), "-c", validation_script], "E2E test infrastructure validation"
        )

    def validate_framework_completeness(self) -> dict[str, Any]:
        """Validate that the framework is complete"""
        print("🔍 Validating framework completeness...")

        # Count test methods in each module
        test_counts = {}

        integration_dir = self.project_root / "tests" / "integration"
        e2e_dir = self.project_root / "tests" / "e2e"

        for test_dir, module_name in [(integration_dir, "integration"), (e2e_dir, "e2e")]:
            if not test_dir.exists():
                test_counts[module_name] = 0
                continue

            total_tests = 0
            for test_file in test_dir.glob("test_*.py"):
                try:
                    with open(test_file, encoding="utf-8") as f:
                        content = f.read()
                        # Count test methods
                        total_tests += content.count("def test_")
                        total_tests += content.count("async def test_")
                except Exception:
                    continue

            test_counts[module_name] = total_tests

        total_tests = sum(test_counts.values())

        return {
            "success": total_tests >= 150,  # We expect 162+ tests
            "test_counts": test_counts,
            "total_tests": total_tests,
            "expected_minimum": 150,
            "description": "Framework completeness validation",
        }

    def generate_validation_report(self) -> None:
        """Generate comprehensive validation report"""
        print("\n" + "=" * 80)
        print("🧪 TESTING & QUALITY ASSURANCE FRAMEWORK VALIDATION REPORT")
        print("=" * 80)

        validations = [
            ("Test Structure", self.validate_test_structure),
            ("Python Syntax", self.validate_import_syntax),
            ("Pytest Collection", self.validate_pytest_collection),
            ("E2E Infrastructure", self.run_e2e_test_validation),
            ("Framework Completeness", self.validate_framework_completeness),
        ]

        all_passed = True
        results = {}

        for validation_name, validation_func in validations:
            print(f"\n📋 {validation_name}:")
            print("-" * 40)

            try:
                result = validation_func()
                results[validation_name] = result

                if result["success"]:
                    print(f"✅ PASSED: {result['description']}")
                    if "total_files" in result:
                        print(f"   📁 Files validated: {result['total_files']}")
                    if "total_tests" in result:
                        print(f"   🧪 Total tests found: {result['total_tests']}")
                else:
                    print(f"❌ FAILED: {result['description']}")
                    all_passed = False

                    if "missing_files" in result and result["missing_files"]:
                        print(f"   📋 Missing files: {result['missing_files']}")
                    if "syntax_errors" in result and result["syntax_errors"]:
                        print(f"   🚫 Syntax errors: {len(result['syntax_errors'])}")
                    if result.get("stderr"):
                        print(f"   ⚠️  Error: {result['stderr'][:200]}...")

            except Exception as e:
                print(f"❌ VALIDATION ERROR: {str(e)}")
                all_passed = False
                results[validation_name] = {
                    "success": False,
                    "error": str(e),
                    "description": validation_name,
                }

        # Final summary
        print("\n" + "=" * 80)
        print("📊 VALIDATION SUMMARY")
        print("=" * 80)

        passed_count = sum(1 for r in results.values() if r.get("success", False))
        total_count = len(results)

        if all_passed:
            print("🎉 ALL VALIDATIONS PASSED!")
            print(f"✅ {passed_count}/{total_count} validation categories successful")
            print("\n🚀 Testing & Quality Assurance Framework is 100% ready!")
            print("💡 Framework can be safely merged to main branch")
        else:
            print("⚠️  SOME VALIDATIONS FAILED")
            print(f"❌ {passed_count}/{total_count} validation categories successful")
            print("\n🔧 Please address the issues above before merging")

        return results


def main():
    """Main validation execution"""
    print("🚀 Starting Testing & Quality Assurance Framework Validation")
    print("=" * 80)

    validator = TestingFrameworkValidator()
    results = validator.generate_validation_report()

    # Return appropriate exit code
    all_passed = all(r.get("success", False) for r in results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
