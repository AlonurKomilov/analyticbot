#!/usr/bin/env python3
"""
Mock Services Consolidation Script

This script helps consolidate all scattered mock services into 
the new centralized location: src/mock_services/

Steps:
1. Analyze existing mock files
2. Create consolidated versions
3. Update import references
4. Remove scattered files
"""

import os
import shutil
from pathlib import Path
import re
from typing import List, Dict

def find_all_mock_files() -> Dict[str, List[str]]:
    """Find all mock files in the project"""
    
    base_path = Path("/home/alonur/analyticbot")
    src_path = base_path / "src"
    
    mock_files = {
        "api_mocks_services": [],
        "api_testing_services": [], 
        "bot_adapters": [],
        "other": []
    }
    
    # API service __mocks__
    api_mocks_path = src_path / "api_service" / "application" / "services" / "__mocks__"
    if api_mocks_path.exists():
        for file in api_mocks_path.glob("*.py"):
            if file.name != "__init__.py":
                mock_files["api_mocks_services"].append(str(file))
    
    # API testing services
    api_testing_path = src_path / "api_service" / "infrastructure" / "testing" / "services"
    if api_testing_path.exists():
        for file in api_testing_path.glob("*.py"):
            if file.name != "__init__.py" and "mock" in file.name:
                mock_files["api_testing_services"].append(str(file))
    
    # Bot service adapters
    bot_adapters_path = src_path / "bot_service" / "application" / "services" / "adapters"
    if bot_adapters_path.exists():
        for file in bot_adapters_path.glob("mock*.py"):
            mock_files["bot_adapters"].append(str(file))
    
    return mock_files

def analyze_imports() -> Dict[str, List[str]]:
    """Analyze import statements that need to be updated"""
    
    base_path = Path("/home/alonur/analyticbot")
    src_path = base_path / "src"
    
    imports_to_fix = {
        "missing_mocks_imports": [],
        "existing_mocks_imports": [],
        "testing_services_imports": []
    }
    
    # Search for import statements
    for py_file in src_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            
            # Look for broken imports
            if "src.api_service.__mocks__" in content:
                imports_to_fix["missing_mocks_imports"].append(str(py_file))
            
            # Look for existing __mocks__ imports  
            if "from src.api_service.application.services.__mocks__" in content:
                imports_to_fix["existing_mocks_imports"].append(str(py_file))
            
            # Look for testing services imports
            if "from src.api_service.infrastructure.testing.services" in content and "mock" in content:
                imports_to_fix["testing_services_imports"].append(str(py_file))
                
        except (UnicodeDecodeError, IOError):
            continue
    
    return imports_to_fix

def generate_migration_plan():
    """Generate a comprehensive migration plan"""
    
    print("🏗️  MOCK SERVICES CONSOLIDATION PLAN")
    print("=" * 50)
    
    # Find files
    mock_files = find_all_mock_files()
    imports_to_fix = analyze_imports()
    
    total_files = sum(len(files) for files in mock_files.values())
    total_imports = sum(len(imports) for imports in imports_to_fix.values())
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"   Mock files found: {total_files}")
    print(f"   Import references: {total_imports}")
    
    print(f"\n📁 MOCK FILES BY LOCATION:")
    for location, files in mock_files.items():
        if files:
            print(f"\n{location.upper()} ({len(files)} files):")
            for file in files:
                print(f"   📄 {Path(file).name}")
    
    print(f"\n🔗 IMPORT REFERENCES TO FIX:")
    for import_type, files in imports_to_fix.items():
        if files:
            print(f"\n{import_type.replace('_', ' ').upper()} ({len(files)} files):")
            for file in files[:3]:  # Show first 3
                rel_path = Path(file).relative_to("/home/alonur/analyticbot")
                print(f"   🔗 {rel_path}")
            if len(files) > 3:
                print(f"   ... and {len(files) - 3} more")
    
    print(f"\n🎯 CONSOLIDATION STRATEGY:")
    print("=" * 30)
    print("1. ✅ Created: src/mock_services/ (centralized location)")
    print("2. 🔄 Migrate: Copy all mock services to centralized location")
    print("3. 🔧 Fix: Update all import references")
    print("4. 🧪 Test: Verify everything works")
    print("5. 🗑️  Clean: Remove scattered files")
    
    print(f"\n📋 BENEFITS AFTER MIGRATION:")
    print("-" * 28)
    print("✅ Single location for all mocks")
    print("✅ Consistent interfaces and patterns")
    print("✅ Easy service discovery")
    print("✅ Built-in metrics and state management")
    print("✅ Factory pattern for flexibility")
    
    # Create update script
    print(f"\n🤖 IMPORT UPDATE COMMANDS:")
    print("-" * 26)
    
    # Generate sed commands to fix imports
    print("# Fix broken __mocks__ imports")
    print("find src/ -name '*.py' -exec sed -i 's|from src.api_service.__mocks__|from src.mock_services|g' {} \\;")
    
    print("\n# Fix existing __mocks__ imports")  
    print("find src/ -name '*.py' -exec sed -i 's|from src.api_service.application.services.__mocks__|from src.mock_services|g' {} \\;")
    
    print("\n# Fix testing services imports")
    print("find src/ -name '*.py' -exec sed -i 's|from src.api_service.infrastructure.testing.services|from src.mock_services.services|g' {} \\;")

def test_consolidated_structure():
    """Test the consolidated mock services structure"""
    
    print(f"\n🧪 TESTING CONSOLIDATED STRUCTURE:")
    print("=" * 35)
    
    try:
        from src.mock_services import mock_factory
        print("✅ Import successful: src.mock_services.mock_factory")
        
        # Test service creation
        analytics = mock_factory.create_analytics_service()
        if analytics:
            print(f"✅ Service created: {analytics.get_service_name()}")
        else:
            print("❌ Failed to create analytics service")
        
        # Test registry
        services = mock_factory.registry.list_services()
        print(f"✅ Registry shows {len(services)} services: {services}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    """Main consolidation analysis and planning"""
    
    print("🚀 Mock Services Consolidation Analysis")
    print(f"Date: 2025-09-26")
    print("=" * 50)
    
    # Generate migration plan
    generate_migration_plan()
    
    # Test current structure
    test_consolidated_structure()
    
    print(f"\n✨ NEXT STEPS:")
    print("1. Run import update commands above")
    print("2. Migrate remaining services to src/mock_services/services/")
    print("3. Test all functionality")
    print("4. Remove old scattered files")
    
    print(f"\n🎉 CONSOLIDATION READY!")

if __name__ == "__main__":
    main()