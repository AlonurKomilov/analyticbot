#!/usr/bin/env python3
"""
Analyze Current src/ Structure - Learn the existing Module Monolith architecture
"""

import os
from pathlib import Path
from collections import defaultdict

def analyze_src_structure():
    """Deep analysis of existing src/ structure"""
    
    print("🔍 ANALYZING EXISTING src/ MODULE MONOLITH STRUCTURE")
    print("=" * 70)
    
    if not os.path.exists('src'):
        print("❌ src/ directory not found!")
        return
    
    # Analyze each module
    modules = {}
    for item in sorted(os.listdir('src')):
        module_path = Path('src') / item
        if module_path.is_dir() and not item.startswith('_'):
            
            # Get module structure
            module_info = {
                'layers': [],
                'files': [],
                'submodules': {}
            }
            
            if module_path.exists():
                for subitem in os.listdir(module_path):
                    subpath = module_path / subitem
                    if subpath.is_dir():
                        if subitem in ['domain', 'application', 'infrastructure', 'presentation']:
                            module_info['layers'].append(subitem)
                            # Count files in each layer
                            layer_files = []
                            for root, dirs, files in os.walk(subpath):
                                for file in files:
                                    if file.endswith('.py'):
                                        layer_files.append(Path(root) / file)
                            module_info['submodules'][subitem] = len(layer_files)
                        else:
                            module_info['submodules'][subitem] = 'other'
                    elif subitem.endswith('.py'):
                        module_info['files'].append(subitem)
            
            modules[item] = module_info
    
    # Display analysis
    print("📊 CURRENT MODULE STRUCTURE:")
    
    for module_name, info in modules.items():
        print(f"\n📂 {module_name}/")
        
        if info['layers']:
            print(f"   🏗️  Layers: {', '.join(info['layers'])}")
            for layer in info['layers']:
                file_count = info['submodules'].get(layer, 0)
                print(f"      • {layer}/: {file_count} files")
        
        if info['files']:
            print(f"   📄 Root files: {', '.join(info['files'])}")
        
        other_dirs = [k for k, v in info['submodules'].items() if v == 'other']
        if other_dirs:
            print(f"   📁 Other directories: {', '.join(other_dirs)}")
    
    # Analyze shared_kernel specifically
    print(f"\n🔍 DETAILED shared_kernel/ ANALYSIS:")
    shared_path = Path('src/shared_kernel')
    if shared_path.exists():
        for layer in ['domain', 'application', 'infrastructure']:
            layer_path = shared_path / layer
            if layer_path.exists():
                print(f"   📂 {layer}/:")
                for item in sorted(os.listdir(layer_path)):
                    item_path = layer_path / item
                    if item_path.is_dir():
                        file_count = len([f for f in item_path.rglob('*.py')])
                        print(f"      • {item}/: {file_count} files")
                    elif item.endswith('.py'):
                        print(f"      • {item}")
    
    # Check what should be in shared_kernel
    print(f"\n🎯 MODULE MONOLITH INTEGRATION POINTS:")
    
    integration_points = [
        ("DI Container", "Should be in shared_kernel/infrastructure/"),
        ("Service Protocols", "Should be in shared_kernel/domain/"),
        ("Database Connection", "Should be in shared_kernel/infrastructure/"),
        ("Common Utilities", "Should be in shared_kernel/infrastructure/common/"),
        ("Cross-Module Events", "Should be in shared_kernel/domain/events/"),
    ]
    
    for component, location in integration_points:
        print(f"   • {component}: {location}")
    
    # Check for existing cross-module dependencies
    print(f"\n🔗 CROSS-MODULE DEPENDENCIES ANALYSIS:")
    
    # Look for imports between modules
    cross_imports = defaultdict(list)
    for module_name in modules.keys():
        module_path = Path('src') / module_name
        for py_file in module_path.rglob('*.py'):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    for other_module in modules.keys():
                        if other_module != module_name and f'src.{other_module}' in content:
                            cross_imports[module_name].append(other_module)
            except:
                continue
    
    for module, imports in cross_imports.items():
        if imports:
            print(f"   • {module} imports from: {', '.join(set(imports))}")
    
    # Recommendations based on analysis
    print(f"\n💡 RECOMMENDATIONS FOR COMPLETING MODULE MONOLITH:")
    
    recommendations = []
    
    # Check if shared_kernel has proper structure
    shared_layers = modules.get('shared_kernel', {}).get('layers', [])
    if 'infrastructure' not in shared_layers:
        recommendations.append("Create src/shared_kernel/infrastructure/ for DI container and common infrastructure")
    
    if 'domain' not in shared_layers:
        recommendations.append("Create src/shared_kernel/domain/ for service protocols and shared entities")
    
    # Check for modules without proper layers
    for module_name, info in modules.items():
        if module_name != 'shared_kernel' and module_name != 'migration_adapters':
            expected_layers = ['domain', 'application', 'infrastructure', 'presentation']
            missing_layers = [layer for layer in expected_layers if layer not in info['layers']]
            if missing_layers:
                recommendations.append(f"Module {module_name} missing layers: {', '.join(missing_layers)}")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    return modules

if __name__ == "__main__":
    analyze_src_structure()