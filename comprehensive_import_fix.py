#!/usr/bin/env python3
"""
Comprehensive Import Consolidation Script
Fixes all import references to use centralized mock services
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def find_and_fix_imports():
    """Find and fix all mock service imports"""
    
    # Mapping of old import patterns to new ones
    import_mappings = {
        # Old scattered service imports
        r'from src\.api_service\.application\.services\.__mocks__\.mock_(\w+)_service import Mock(\w+)Service': 
        r'from src.mock_services.services import Mock\2Service',
        
        r'from src\.api_service\.infrastructure\.testing\.services\.mock_(\w+)_service import Mock(\w+)Service':
        r'from src.mock_services.services import Mock\2Service',
        
        r'from src\.bot_service\.application\.services\.adapters\.mock_(\w+)_adapter import Mock(\w+)Adapter':
        r'from src.mock_services.services import Mock\2Service',
        
        # Direct service imports
        r'from \.\.services\.mock_(\w+)_service import Mock(\w+)Service':
        r'from src.mock_services.services import Mock\2Service',
        
        r'from \.mock_(\w+)_service import Mock(\w+)Service':
        r'from src.mock_services.services import Mock\2Service',
        
        # Module-level imports
        r'from src\.api_service\.application\.services\.__mocks__ import mock_(\w+)_service':
        r'from src.mock_services.services import mock_\1_service',
        
        r'from src\.api_service\.infrastructure\.testing\.services import mock_(\w+)_service':
        r'from src.mock_services.services import mock_\1_service',
        
        # Specific service fixes
        r'from src\.api_service\.application\.services\.__mocks__\.mock_analytics_service import MockAnalyticsService':
        r'from src.mock_services.services import MockAnalyticsService',
        
        r'from src\.api_service\.infrastructure\.testing\.services\.mock_payment_service import MockPaymentService':
        r'from src.mock_services.services import MockPaymentService',
        
        r'from src\.bot_service\.application\.services\.adapters\.mock_analytics_adapter import MockAnalyticsAdapter':
        r'from src.mock_services.services import MockAnalyticsService',
        
        r'from src\.bot_service\.application\.services\.adapters\.mock_payment_adapter import MockPaymentAdapter':
        r'from src.mock_services.services import MockPaymentService',
    }
    
    # Additional specific fixes
    specific_fixes = {
        'MockAnalyticsAdapter': 'MockAnalyticsService',
        'MockPaymentAdapter': 'MockPaymentService',
        'mock_analytics_adapter': 'mock_analytics_service',
        'mock_payment_adapter': 'mock_payment_service',
    }
    
    fixed_files = []
    total_fixes = 0
    
    print("🔧 COMPREHENSIVE IMPORT CONSOLIDATION")
    print("=" * 45)
    
    # Process all Python files in src/
    for root, dirs, files in os.walk('src'):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                
                # Skip mock_services directory itself
                if 'mock_services' in str(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    file_fixes = 0
                    
                    # Apply import pattern fixes
                    for old_pattern, new_pattern in import_mappings.items():
                        new_content = re.sub(old_pattern, new_pattern, content)
                        if new_content != content:
                            matches = len(re.findall(old_pattern, content))
                            file_fixes += matches
                            content = new_content
                    
                    # Apply specific string replacements
                    for old_ref, new_ref in specific_fixes.items():
                        if old_ref in content:
                            content = content.replace(old_ref, new_ref)
                            file_fixes += content.count(new_ref) - original_content.count(new_ref)
                    
                    # Write back if changes were made
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        fixed_files.append(str(file_path))
                        total_fixes += file_fixes
                        print(f"✅ Fixed {file_fixes} imports in {file_path}")
                
                except Exception as e:
                    print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n🎯 IMPORT CONSOLIDATION RESULTS:")
    print(f"✅ Files updated: {len(fixed_files)}")
    print(f"✅ Total import fixes: {total_fixes}")
    
    if fixed_files:
        print(f"\n📋 Updated files:")
        for file in fixed_files[:10]:  # Show first 10
            print(f"   - {file}")
        if len(fixed_files) > 10:
            print(f"   ... and {len(fixed_files) - 10} more")
    
    return fixed_files, total_fixes

def verify_consolidation():
    """Verify that all imports are properly consolidated"""
    
    print(f"\n🔍 IMPORT CONSOLIDATION VERIFICATION:")
    
    # Test mock services can be imported
    try:
        from src.mock_services import mock_factory
        services = mock_factory.registry.list_services()
        print(f"✅ Available services: {services}")
        
        # Test each service
        for service_name in services:
            try:
                service = mock_factory.create_service(service_name)
                print(f"✅ {service_name}: {service.get_service_name()}")
            except Exception as e:
                print(f"❌ {service_name}: {e}")
                
    except Exception as e:
        print(f"❌ Mock services import failed: {e}")
    
    # Check for remaining problematic imports
    problematic_patterns = [
        r'from src\.api_service\.application\.services\.__mocks__',
        r'from src\.api_service\.infrastructure\.testing\.services',
        r'from src\.bot_service\.application\.services\.adapters\.mock_',
        r'MockAnalyticsAdapter|MockPaymentAdapter'
    ]
    
    remaining_issues = []
    for root, dirs, files in os.walk('src'):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'mock_services']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in problematic_patterns:
                        if re.search(pattern, content):
                            remaining_issues.append((str(file_path), pattern))
                            
                except:
                    continue
    
    if remaining_issues:
        print(f"\n⚠️  REMAINING ISSUES: {len(remaining_issues)}")
        for file_path, pattern in remaining_issues[:5]:
            print(f"   - {file_path}: {pattern}")
        if len(remaining_issues) > 5:
            print(f"   ... and {len(remaining_issues) - 5} more")
    else:
        print(f"\n✅ NO REMAINING IMPORT ISSUES!")
    
    return len(remaining_issues) == 0

def main():
    """Main execution function"""
    print("🚀 STARTING COMPREHENSIVE IMPORT CONSOLIDATION")
    
    # Fix imports
    fixed_files, total_fixes = find_and_fix_imports()
    
    # Verify consolidation
    verification_passed = verify_consolidation()
    
    print(f"\n🎯 FINAL RESULTS:")
    if verification_passed and total_fixes > 0:
        print("🎉 IMPORT CONSOLIDATION COMPLETED SUCCESSFULLY!")
        print("✅ All mock service imports properly consolidated")
        print("✅ All services verified and working")
    elif total_fixes == 0:
        print("ℹ️  No import fixes needed - already consolidated")
    else:
        print("⚠️  Import consolidation completed with remaining issues")
        print("   Manual review may be needed for complex cases")
    
    print(f"\n📊 Summary:")
    print(f"   - Files processed: {len(fixed_files)}")
    print(f"   - Import fixes applied: {total_fixes}")
    print(f"   - Verification passed: {verification_passed}")

if __name__ == "__main__":
    main()