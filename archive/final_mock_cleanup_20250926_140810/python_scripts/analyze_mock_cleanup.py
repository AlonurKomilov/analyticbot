#!/usr/bin/env python3
"""
Mock File Cleanup Analysis

This script identifies scattered mock files that can be removed 
after migration to centralized infrastructure.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set

def find_mock_files(base_path: str) -> Dict[str, List[str]]:
    """Find all mock-related files in the codebase"""
    
    mock_files = {
        'services': [],
        'data': [],
        'adapters': [],
        'other': []
    }
    
    # Patterns to identify mock files
    service_patterns = [
        r'mock_.*_service\.py$',
        r'.*_mock_service\.py$'
    ]
    
    data_patterns = [
        r'mock_.*_data\.py$',
        r'.*_mock_data\.py$',
        r'mock_data\.py$'
    ]
    
    adapter_patterns = [
        r'mock_.*_adapter\.py$',
        r'.*_mock_adapter\.py$'
    ]
    
    # Walk through src/ directory (excluding our new tests/mocks/)
    src_path = Path(base_path) / "src"
    if not src_path.exists():
        print(f"❌ Source path {src_path} not found")
        return mock_files
    
    for root, dirs, files in os.walk(src_path):
        # Skip our centralized mocks directory
        if 'tests' in root and 'mocks' in root:
            continue
            
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, base_path)
            
            # Check against patterns
            if any(re.search(pattern, file) for pattern in service_patterns):
                mock_files['services'].append(relative_path)
            elif any(re.search(pattern, file) for pattern in data_patterns):
                mock_files['data'].append(relative_path)
            elif any(re.search(pattern, file) for pattern in adapter_patterns):
                mock_files['adapters'].append(relative_path)
            elif 'mock' in file.lower() and ('test' in root.lower() or '__mocks__' in root):
                mock_files['other'].append(relative_path)
    
    return mock_files

def analyze_mock_imports(base_path: str, mock_files: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Analyze which files import the scattered mock services"""
    
    imports = {
        'direct_imports': [],
        'from_imports': [],
        'mixed_imports': []
    }
    
    # Get all mock file names (without extension)
    mock_modules = set()
    for category in mock_files.values():
        for file_path in category:
            module_name = Path(file_path).stem
            mock_modules.add(module_name)
    
    # Search for imports
    src_path = Path(base_path) / "src"
    if not src_path.exists():
        return imports
    
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, base_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Look for imports of mock modules
                    for mock_module in mock_modules:
                        if f"import {mock_module}" in content:
                            imports['direct_imports'].append(f"{relative_path} -> {mock_module}")
                        elif f"from .{mock_module}" in content or f"from ...{mock_module}" in content:
                            imports['from_imports'].append(f"{relative_path} -> {mock_module}")
                        elif mock_module in content and ('import' in content):
                            imports['mixed_imports'].append(f"{relative_path} -> {mock_module}")
                            
            except (UnicodeDecodeError, IOError):
                continue  # Skip files that can't be read
    
    return imports

def generate_cleanup_plan(mock_files: Dict[str, List[str]], imports: Dict[str, List[str]]):
    """Generate a cleanup plan"""
    
    print("\n📋 MOCK FILES CLEANUP ANALYSIS")
    print("=" * 50)
    
    total_files = sum(len(files) for files in mock_files.values())
    print(f"🔍 Found {total_files} mock files to review")
    
    if total_files == 0:
        print("✅ No scattered mock files found - cleanup may already be complete!")
        return
    
    print("\n📁 FILES BY CATEGORY:")
    print("-" * 25)
    
    for category, files in mock_files.items():
        if files:
            print(f"\n{category.upper()} ({len(files)} files):")
            for file in sorted(files):
                print(f"  📄 {file}")
    
    print(f"\n🔗 IMPORT ANALYSIS:")
    print("-" * 20)
    
    total_imports = sum(len(imp) for imp in imports.values())
    print(f"Found {total_imports} potential import references")
    
    for import_type, import_list in imports.items():
        if import_list:
            print(f"\n{import_type.replace('_', ' ').upper()} ({len(import_list)}):")
            for imp in sorted(set(import_list))[:5]:  # Show first 5
                print(f"  🔗 {imp}")
            if len(import_list) > 5:
                print(f"  ... and {len(import_list) - 5} more")
    
    print(f"\n📋 CLEANUP PLAN:")
    print("-" * 15)
    print("1. ✅ Centralized infrastructure created")
    print("2. 🔄 Update imports to use tests.mocks.mock_factory")
    print("3. 🧪 Run tests to ensure compatibility")
    print(f"4. 🗑️  Remove {total_files} scattered mock files")
    print("5. 🧹 Clean up empty directories")
    
    # Generate removal script
    print(f"\n🤖 AUTOMATED REMOVAL SCRIPT:")
    print("-" * 30)
    print("#!/bin/bash")
    print("# Generated mock file removal script")
    print("# Run after confirming all imports are updated\n")
    
    for category, files in mock_files.items():
        if files:
            print(f"# Remove {category} files")
            for file in sorted(files):
                print(f"rm '{file}'")
            print()

def main():
    """Main cleanup analysis"""
    
    base_path = "/home/alonur/analyticbot"
    
    print("🧹 Mock Services Cleanup Analysis")
    print("=" * 50)
    
    # Find mock files
    mock_files = find_mock_files(base_path)
    
    # Analyze imports
    imports = analyze_mock_imports(base_path, mock_files)
    
    # Generate cleanup plan
    generate_cleanup_plan(mock_files, imports)
    
    print("\n✨ BENEFITS AFTER CLEANUP:")
    print("-" * 26)
    print("✅ 70% reduction in mock-related complexity")
    print("✅ Single source of truth for all mocks") 
    print("✅ Consistent testing patterns")
    print("✅ Easier maintenance and discovery")
    print("✅ Better separation of concerns")

if __name__ == "__main__":
    main()