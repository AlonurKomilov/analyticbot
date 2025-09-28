#!/usr/bin/env python3
"""
Services Layer Separation Verification
Check that services are properly separated between core and apps layers
"""

import ast
import os
import sys
from pathlib import Path


def analyze_service_dependencies():
    """Analyze service dependencies for clean architecture violations"""
    core_services = []
    app_services = []
    violations = []
    
    # Change to project root directory
    project_root = Path.cwd()
    
    # Scan core services
    core_services_path = project_root / 'core' / 'services'
    if core_services_path.exists():
        for py_file in core_services_path.rglob('*.py'):
            if py_file.name != '__init__.py':
                violations.extend(check_core_service_purity(py_file))
                try:
                    core_services.append(str(py_file.relative_to(project_root)))
                except ValueError:
                    core_services.append(str(py_file))
    
    # Scan app services  
    for app_dir in ['apps/bot/services', 'apps/api/services', 'apps/jobs/services']:
        app_path = project_root / app_dir
        if app_path.exists():
            for py_file in app_path.rglob('*.py'):
                if py_file.name != '__init__.py':
                    try:
                        app_services.append(str(py_file.relative_to(project_root)))
                    except ValueError:
                        app_services.append(str(py_file))
    
    return core_services, app_services, violations


def check_core_service_purity(service_file: Path) -> list:
    """Check if core service has framework dependencies (violations)"""
    violations = []
    
    try:
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse AST to find imports
        tree = ast.parse(content)
        
        # Framework dependencies that shouldn't be in core
        forbidden_imports = [
            'fastapi', 'pydantic', 'aiogram', 'django', 'flask',
            'requests', 'httpx', 'redis', 'sqlalchemy', 'asyncpg'
        ]
        
        project_root = Path.cwd()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    for forbidden in forbidden_imports:
                        if forbidden in node.module:
                            try:
                                file_path = str(service_file.relative_to(project_root))
                            except ValueError:
                                file_path = str(service_file)
                            violations.append({
                                'file': file_path,
                                'line': node.lineno,
                                'violation': f"Framework import: {node.module}",
                                'type': 'framework_dependency'
                            })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in forbidden_imports:
                        if forbidden in alias.name:
                            try:
                                file_path = str(service_file.relative_to(project_root))
                            except ValueError:
                                file_path = str(service_file)
                            violations.append({
                                'file': file_path,
                                'line': node.lineno, 
                                'violation': f"Framework import: {alias.name}",
                                'type': 'framework_dependency'
                            })
                            
    except Exception as e:
        print(f"Error analyzing {service_file}: {e}")
    
    return violations


def check_service_duplication():
    """Check for service duplication across layers"""
    core_service_names = set()
    app_service_names = set()
    duplicates = []
    
    # Get core service names
    core_services_path = Path('core/services')
    if core_services_path.exists():
        for py_file in core_services_path.rglob('*.py'):
            if py_file.name != '__init__.py':
                service_name = py_file.stem.replace('_service', '').replace('service', '')
                core_service_names.add(service_name)
    
    # Get app service names and check for duplication
    for app_dir in ['apps/bot/services', 'apps/api/services']:
        app_path = Path(app_dir)
        if app_path.exists():
            for py_file in app_path.rglob('*.py'):
                if py_file.name != '__init__.py':
                    service_name = py_file.stem.replace('_service', '').replace('service', '')
                    if service_name in core_service_names:
                        duplicates.append({
                            'service': service_name,
                            'core_file': f"core/services/{service_name}_service.py",
                            'app_file': str(py_file.relative_to(Path.cwd()))
                        })
                    app_service_names.add(service_name)
    
    return duplicates


def check_business_logic_placement():
    """Check for business logic in wrong places"""
    issues = []
    project_root = Path.cwd()
    
    # Services that should be in core (contain business logic)
    business_services = ['channel_management', 'payment', 'subscription', 'user_management']
    
    for service_name in business_services:
        core_path = project_root / f'core/services/{service_name}_service.py'
        bot_path = project_root / f'apps/bot/services/{service_name}_service.py'
        api_path = project_root / f'apps/api/services/{service_name}_service.py'
        
        if not core_path.exists() and (bot_path.exists() or api_path.exists()):
            found_paths = []
            for p in [bot_path, api_path]:
                if p.exists():
                    try:
                        found_paths.append(str(p.relative_to(project_root)))
                    except ValueError:
                        found_paths.append(str(p))
            
            issues.append({
                'service': service_name,
                'issue': 'Business logic service not in core layer',
                'found_in': found_paths
            })
    
    return issues


def main():
    """Main verification function"""
    print("🔍 VERIFYING SERVICES LAYER SEPARATION (Issue #5)")
    print("=" * 60)
    
    core_services, app_services, violations = analyze_service_dependencies()
    duplicates = check_service_duplication()
    business_logic_issues = check_business_logic_placement()
    
    print(f"\n📊 SERVICES ANALYSIS:")
    print(f"   • Core services: {len(core_services)}")
    print(f"   • App services: {len(app_services)}")
    print(f"   • Framework violations in core: {len(violations)}")
    print(f"   • Service duplications: {len(duplicates)}")
    print(f"   • Business logic misplacements: {len(business_logic_issues)}")
    
    if core_services:
        print(f"\n✅ CORE SERVICES (Domain Logic):")
        for service in core_services:
            print(f"   📁 {service}")
    
    if violations:
        print(f"\n❌ CORE SERVICE VIOLATIONS:")
        for violation in violations:
            print(f"   📁 {violation['file']}:{violation['line']}")
            print(f"      {violation['violation']}")
    
    if duplicates:
        print(f"\n⚠️  SERVICE DUPLICATIONS:")
        for dup in duplicates:
            print(f"   🔄 {dup['service']}: {dup['core_file']} ↔ {dup['app_file']}")
    
    if business_logic_issues:
        print(f"\n❌ BUSINESS LOGIC MISPLACEMENT:")
        for issue in business_logic_issues:
            print(f"   📁 {issue['service']}: {issue['issue']}")
            print(f"      Found in: {issue['found_in']}")
    
    print(f"\n🏆 ISSUE #5 FIX STATUS:")
    total_issues = len(violations) + len(duplicates) + len(business_logic_issues)
    if total_issues == 0:
        print("✅ SERVICES PROPERLY SEPARATED!")
        print("   • Core services are framework-agnostic")
        print("   • No business logic in application layer")
        print("   • Clean separation of concerns achieved")
        return 0
    else:
        print(f"🔄 SERVICES PARTIALLY SEPARATED ({total_issues} issues remaining)")
        print(f"   • Framework violations: {len(violations)}")
        print(f"   • Duplications: {len(duplicates)}")
        print(f"   • Misplacements: {len(business_logic_issues)}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)