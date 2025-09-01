#!/usr/bin/env python3
"""
🧹 COMPREHENSIVE CODE CLEANUP SCRIPT
===================================

This script fixes all issues identified by GitHub Actions auto-fixer:
1. Removes unused imports from React components
2. Fixes security vulnerabilities
3. Optimizes code quality
"""

import os
import re
from pathlib import Path


def remove_unused_imports():
    """Remove unused imports from frontend components"""
    print("🧹 Cleaning up unused imports...")

    cleanup_tasks = [
        {
            "file": "/home/alonur/analyticbot/apps/frontend/src/components/AnalyticsDashboard.jsx",
            "remove_imports": ["Fab"],
            "description": "Remove unused Floating Action Button import",
        },
        {
            "file": "/home/alonur/analyticbot/apps/frontend/src/components/EnhancedMediaUploader.jsx",
            "remove_imports": ["RefreshIcon", "Button", "Tooltip"],
            "description": "Remove unused UI component imports",
        },
        {
            "file": "/home/alonur/analyticbot/apps/frontend/src/components/StorageFileBrowser.jsx",
            "remove_imports": ["DownloadIcon"],
            "description": "Remove unused icon import",
        },
        {
            "file": "/home/alonur/analyticbot/apps/frontend/src/components/PostViewDynamicsChart.jsx",
            "remove_imports": ["Line", "LineChart"],
            "description": "Remove unused chart component imports",
        },
        {
            "file": "/home/alonur/analyticbot/apps/frontend/src/components/BestTimeRecommender.jsx",
            "remove_imports": ["TimeIcon", "TrendingUpIcon", "IconButton"],
            "description": "Remove unused icon and button imports",
        },
    ]

    cleaned_files = 0

    for task in cleanup_tasks:
        file_path = Path(task["file"])

        if not file_path.exists():
            print(f"⚠️  File not found: {file_path.name}")
            continue

        print(f"🔧 Processing: {file_path.name}")
        print(f"   📝 {task['description']}")

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Remove each unused import
            for import_name in task["remove_imports"]:
                # Pattern to match import in various formats
                patterns = [
                    # Single import: import { ImportName } from '...'
                    rf'import\s*{{\s*{re.escape(import_name)}\s*}}\s*from\s*[\'"][^\'\"]+[\'"];?\n?',
                    # Multiple imports: import { ImportName, Other } from '...'
                    rf",\s*{re.escape(import_name)}\s*(?=\s*}})",
                    rf"{re.escape(import_name)}\s*,\s*(?=\w)",
                    # In the middle of multiple imports
                    rf"(?<=,\s){re.escape(import_name)}\s*(?=,)",
                ]

                for pattern in patterns:
                    if re.search(pattern, content):
                        content = re.sub(pattern, "", content)
                        print(f"   ✅ Removed: {import_name}")
                        break
                else:
                    print(f"   ⚠️  Could not find: {import_name}")

            # Clean up any empty import lines
            content = re.sub(r'import\s*{\s*}\s*from\s*[\'"][^\'\"]+[\'"];?\n', "", content)

            # Write back if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"   💾 Saved: {file_path.name}")
                cleaned_files += 1
            else:
                print(f"   📝 No changes needed: {file_path.name}")

        except Exception as e:
            print(f"   ❌ Error processing {file_path.name}: {e}")

    print(f"\n✅ Cleanup completed: {cleaned_files} files processed")
    return cleaned_files


def fix_security_issues():
    """Fix security vulnerabilities"""
    print("\n🔒 Fixing security issues...")

    # Fix regex pattern in content_optimizer.py
    optimizer_file = "/home/alonur/analyticbot/apps/bot/services/ml/content_optimizer.py"

    if not os.path.exists(optimizer_file):
        print(f"⚠️  File not found: {optimizer_file}")
        return False

    try:
        with open(optimizer_file, encoding="utf-8") as f:
            content = f.read()

        # Fix the problematic regex pattern
        # Old pattern: r"https?://(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?",
        # New pattern: more specific and secure
        old_pattern = r'r"https?://(?:\[a-zA-Z0-9\\-\]\+\\\.)\+\[a-zA-Z\]\{2,\}(?:/\[^\\s\]\*)?"'
        new_pattern = r'r"https?://(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}(?:/[^\s<>\"\']*)?\"'

        # Find and replace the specific problematic line
        problematic_line = r'r"https?://(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?'
        secure_line = 'r"https?://(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\\.)+[a-zA-Z]{2,6}(?:/[^\\s<>"\']*)?'

        if problematic_line in content:
            content = content.replace(problematic_line, secure_line)

            with open(optimizer_file, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ Fixed URL regex pattern in content_optimizer.py")
            print("   📝 Made regex more specific and secure")
            return True
        else:
            print("⚠️  Problematic regex pattern not found")
            return False

    except Exception as e:
        print(f"❌ Error fixing regex pattern: {e}")
        return False


def audit_github_workflows():
    """Audit GitHub Actions workflows for duplicates"""
    print("\n📋 Auditing GitHub Actions workflows...")

    github_dir = Path("/home/alonur/analyticbot/.github")
    if not github_dir.exists():
        print("⚠️  .github directory not found")
        return

    workflows_dir = github_dir / "workflows"
    if not workflows_dir.exists():
        print("⚠️  .github/workflows directory not found")
        return

    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))

    print(f"📁 Found {len(workflow_files)} workflow files:")

    # Categorize workflows
    categories = {
        "CI/CD": [],
        "Security": [],
        "Auto-fix": [],
        "Testing": [],
        "Deployment": [],
        "Other": [],
    }

    for workflow_file in workflow_files:
        file_name = workflow_file.name.lower()

        if "ci" in file_name or "build" in file_name:
            categories["CI/CD"].append(workflow_file.name)
        elif "security" in file_name or "codeql" in file_name:
            categories["Security"].append(workflow_file.name)
        elif "auto" in file_name or "fix" in file_name:
            categories["Auto-fix"].append(workflow_file.name)
        elif "test" in file_name:
            categories["Testing"].append(workflow_file.name)
        elif "deploy" in file_name:
            categories["Deployment"].append(workflow_file.name)
        else:
            categories["Other"].append(workflow_file.name)

    for category, files in categories.items():
        if files:
            print(f"   {category}: {len(files)} files")
            for file in files:
                print(f"     • {file}")

    # Check for potential duplicates
    potential_duplicates = []
    if len(categories["Auto-fix"]) > 1:
        potential_duplicates.append(f"Multiple auto-fix workflows: {categories['Auto-fix']}")
    if len(categories["CI/CD"]) > 2:
        potential_duplicates.append(f"Multiple CI/CD workflows: {categories['CI/CD']}")

    if potential_duplicates:
        print("\n⚠️  Potential duplicates found:")
        for dup in potential_duplicates:
            print(f"   • {dup}")
    else:
        print("\n✅ No obvious duplicates found")


def main():
    """Main cleanup function"""
    print("🚀 STARTING COMPREHENSIVE CODE CLEANUP")
    print("=" * 50)

    # Step 1: Remove unused imports
    cleaned_imports = remove_unused_imports()

    # Step 2: Fix security issues
    security_fixed = fix_security_issues()

    # Step 3: Audit GitHub workflows
    audit_github_workflows()

    # Summary
    print("\n📊 CLEANUP SUMMARY")
    print("=" * 50)
    print(f"🧹 Unused imports cleaned: {cleaned_imports} files")
    print(f"🔒 Security issues fixed: {'✅ Yes' if security_fixed else '❌ No'}")
    print("📋 GitHub workflows audited: ✅ Yes")

    if cleaned_imports > 0 or security_fixed:
        print("\n✅ CLEANUP SUCCESSFUL!")
        print("🎯 Next steps:")
        print("   1. Review the changes")
        print("   2. Test the application")
        print("   3. Commit and push changes")
        print("   4. Check if GitHub Actions pass")
    else:
        print("\n⚠️  No changes were made")
        print("🔍 Check if files exist and paths are correct")

    return True


if __name__ == "__main__":
    main()
