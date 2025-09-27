#!/usr/bin/env python3
"""
Comprehensive Mock Import Fixer
Scans all project files and updates imports to use centralized mock_services
"""

import os
import re


def find_and_fix_mock_imports():
    """Find and fix all problematic mock imports"""

    print("🔧 COMPREHENSIVE MOCK IMPORT FIXER")
    print("=" * 50)

    # Import mapping - old imports to new centralized imports
    import_mappings = {
        # Old API service mock imports
        r"from src\.api_service\.infrastructure\.testing\.services\.mock_analytics_service import MockAnalyticsService": "from src.mock_services.services.mock_analytics_service import MockAnalyticsService",
        r"from src\.api_service\.infrastructure\.testing\.services\.mock_payment_service import MockPaymentService": "from src.mock_services.services.mock_payment_service import MockPaymentService",
        r"from src\.api_service\.infrastructure\.testing\.services\.mock_email_service import MockEmailService": "from src.mock_services.services.mock_email_service import MockEmailService",
        # Old generic service imports
        r"from src\.api_service\.infrastructure\.testing\.services import (.+)": r"from src.mock_services.services import \1",
        r"from src\.api_service\.application\.services\.__mocks__ import (.+)": r"from src.mock_services.services import \1",
        # Old test mock imports
        r"from tests\.mocks\.services\.mock_analytics_service import MockAnalyticsService": "from src.mock_services.services.mock_analytics_service import MockAnalyticsService",
        r"from tests\.mocks\.services\.mock_payment_service import MockPaymentService": "from src.mock_services.services.mock_payment_service import MockPaymentService",
        r"from tests\.mocks\.services\.mock_email_service import MockEmailService": "from src.mock_services.services.mock_email_service import MockEmailService",
        r"from tests\.mocks\.services import (.+)": r"from src.mock_services.services import \1",
        # Old bot service mock imports
        r"from src\.bot_service\.application\.services\.adapters\.mock_analytics_adapter import MockAnalyticsAdapter": "from src.mock_services.services.mock_analytics_service import MockAnalyticsService",
        r"from src\.bot_service\.application\.services\.adapters\.mock_payment_adapter import MockPaymentAdapter": "from src.mock_services.services.mock_payment_service import MockPaymentService",
        # Generic relative imports
        r"from \.\.testing\.services import (.+)": r"from src.mock_services.services import \1",
        r"from \.\.\.testing\.services import (.+)": r"from src.mock_services.services import \1",
        r"from \.\.infrastructure\.testing\.services import (.+)": r"from src.mock_services.services import \1",
    }

    # Find all Python files in the project (excluding venv and archive)
    python_files = []
    excluded_dirs = {".git", ".venv", "venv", "__pycache__", "archive", "node_modules"}

    for root, dirs, files in os.walk("."):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                python_files.append(file_path)

    print(f"📊 Scanning {len(python_files)} Python files...")

    # Track fixes
    files_fixed = []
    total_fixes = 0

    for file_path in python_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            fixes_in_file = 0

            # Apply each import mapping
            for old_pattern, new_import in import_mappings.items():
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_import, content)
                    fixes_in_file += re.subn(old_pattern, new_import, original_content)[1]

            # If we made changes, write them back
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                files_fixed.append(file_path)
                total_fixes += fixes_in_file
                print(f"   ✅ Fixed {fixes_in_file} imports in: {file_path}")

        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")
            continue

    return files_fixed, total_fixes


def verify_mock_services():
    """Verify that the centralized mock services are working"""
    print("\n🔍 VERIFYING CENTRALIZED MOCK SERVICES:")
    try:
        from src.mock_services import mock_factory

        services = mock_factory.registry.list_services()
        print(f"   ✅ Available services: {services}")

        # Test each service
        for service_name in services:
            service = mock_factory.create_service(service_name)
            print(f"   ✅ {service_name}: {service.get_service_name()}")

        return True
    except Exception as e:
        print(f"   ❌ Mock services verification failed: {e}")
        return False


def scan_remaining_issues():
    """Scan for any remaining import issues"""
    print("\n🔍 SCANNING FOR REMAINING ISSUES:")

    remaining_issues = []
    problematic_patterns = [
        r"from src\.api_service\..*testing.*mock",
        r"from src\.bot_service\..*mock_.*_adapter",
        r"from tests\.mocks\.services",
        r"import.*MockService.*from.*testing",
    ]

    for root, dirs, files in os.walk("src"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()

                    for i, line in enumerate(content.split("\n"), 1):
                        for pattern in problematic_patterns:
                            if re.search(pattern, line) and not line.strip().startswith("#"):
                                remaining_issues.append(
                                    {
                                        "file": file_path,
                                        "line": i,
                                        "content": line.strip(),
                                    }
                                )
                                break

                except Exception:
                    continue

    if remaining_issues:
        print(f"   ⚠️  Found {len(remaining_issues)} remaining issues:")
        for issue in remaining_issues[:5]:  # Show first 5
            print(f"      📄 {issue['file']}:{issue['line']}")
            print(f"         {issue['content']}")
    else:
        print("   ✅ No remaining import issues found!")

    return remaining_issues


def main():
    """Main execution"""

    # Fix imports
    files_fixed, total_fixes = find_and_fix_mock_imports()

    # Verify mock services work
    mock_services_ok = verify_mock_services()

    # Scan for remaining issues
    remaining_issues = scan_remaining_issues()

    # Final report
    print("\n🎯 IMPORT FIX SUMMARY:")
    print(f"   ✅ Files fixed: {len(files_fixed)}")
    print(f"   ✅ Total import fixes: {total_fixes}")
    print(
        f"   {'✅' if mock_services_ok else '❌'} Mock services: {'Working' if mock_services_ok else 'Failed'}"
    )
    print(f"   {'✅' if not remaining_issues else '⚠️ '} Remaining issues: {len(remaining_issues)}")

    if len(files_fixed) == 0 and len(remaining_issues) == 0:
        print("\n🎉 ALL IMPORTS ALREADY CLEAN! 🎉")
    elif len(remaining_issues) == 0:
        print(f"\n🎉 IMPORT FIX COMPLETE! All {total_fixes} imports updated successfully! 🎉")
    else:
        print(
            f"\n⚠️  Import fixes applied but {len(remaining_issues)} issues may need manual review"
        )

    return len(files_fixed), total_fixes, len(remaining_issues)


if __name__ == "__main__":
    main()
