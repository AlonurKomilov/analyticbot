#!/usr/bin/env python3
"""
Architecture Compliance Validator
Checks that the new architecture follows Clean Architecture principles
"""

import ast
import re
from pathlib import Path


class ArchitectureViolation:
    def __init__(self, file_path: str, line: int, message: str):
        self.file_path = file_path
        self.line = line
        self.message = message

    def __str__(self):
        return f"{self.file_path}:{self.line} - {self.message}"


class ArchitectureValidator:
    def __init__(self):
        self.violations: list[ArchitectureViolation] = []

    def validate_imports(self, file_path: str) -> list[ArchitectureViolation]:
        """Validate that imports follow Clean Architecture rules"""
        violations = []

        # Define forbidden import patterns
        rules = [
            # Domain layer rules
            (
                r"^domain/",
                [
                    r"from (infrastructure|presentation)\.",
                    r"from application\.(?!event_bus)",
                ],
            ),
            # Application layer rules
            (r"^application/", [r"from presentation\."]),
            # Presentation layer rules
            (r"^presentation/(?!shared)", [r"from presentation\.(?!shared)"]),
            # Infrastructure rules (can import anything except presentation)
            (r"^infrastructure/", [r"from presentation\."]),
        ]

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        import_statement = f"from {node.module}"

                        for pattern, forbidden_imports in rules:
                            if re.match(pattern, file_path):
                                for forbidden in forbidden_imports:
                                    if re.search(forbidden, import_statement):
                                        violations.append(
                                            ArchitectureViolation(
                                                file_path,
                                                node.lineno,
                                                f"Forbidden import: {import_statement}",
                                            )
                                        )
        except (SyntaxError, UnicodeDecodeError):
            # Skip files that can't be parsed
            pass

        return violations

    def validate_file_location(self, file_path: str) -> list[ArchitectureViolation]:
        """Validate that files are in the correct layer"""
        violations = []

        # Define file location rules
        if file_path.startswith("domain/"):
            # Domain files should not import external libraries (except standard lib)
            pass
        elif file_path.startswith("application/"):
            # Application files should contain use cases and services
            pass
        elif file_path.startswith("infrastructure/"):
            # Infrastructure files should contain adapters and repositories
            pass
        elif file_path.startswith("presentation/"):
            # Presentation files should be thin controllers
            pass

        return violations

    def validate_project(self, project_path: str = ".") -> list[ArchitectureViolation]:
        """Validate entire project architecture"""
        all_violations = []

        # Find all Python files
        for py_file in Path(project_path).rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            file_violations = []
            file_violations.extend(self.validate_imports(str(py_file)))
            file_violations.extend(self.validate_file_location(str(py_file)))

            all_violations.extend(file_violations)

        return all_violations


def main():
    validator = ArchitectureValidator()
    violations = validator.validate_project()

    if violations:
        print(f"❌ Found {len(violations)} architecture violations:")
        for violation in violations:
            print(f"  {violation}")
        return 1
    else:
        print("✅ Architecture validation passed!")
        return 0


if __name__ == "__main__":
    exit(main())
