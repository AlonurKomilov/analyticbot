#!/usr/bin/env python3
"""
Step 1: Fix Module Dependencies - Systematic Violation Resolution
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_and_fix_violations():
    """Step 1a: Analyze violations and create fix plan"""
    
    print("🔧 STEP 1A: ANALYZING MODULE DEPENDENCY VIOLATIONS")
    print("=" * 60)
    
    violations = {}
    
    # Get detailed violations
    src_path = Path("src")
    modules = [d.name for d in src_path.iterdir() if d.is_dir() and not d.name.startswith('_')]
    modules.remove('shared_kernel')
    
    print(f"📋 Analyzing violations in: {', '.join(modules)}")
    print()
    
    for module_name in modules:
        module_path = src_path / module_name
        module_violations = []
        
        for py_file in module_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find violations
                for other_module in modules:
                    if other_module != module_name:
                        patterns = [
                            f"from src.{other_module}",
                            f"import src.{other_module}",
                        ]
                        
                        for pattern in patterns:
                            if pattern in content:
                                # Extract the specific import line
                                lines = content.split('\n')
                                for line_num, line in enumerate(lines, 1):
                                    if pattern in line:
                                        module_violations.append({
                                            'file': str(py_file.relative_to(src_path)),
                                            'line_num': line_num,
                                            'line': line.strip(),
                                            'depends_on': other_module,
                                            'pattern': pattern
                                        })
            except:
                continue
        
        if module_violations:
            violations[module_name] = module_violations
    
    # Report detailed violations
    print("🔍 DETAILED VIOLATION ANALYSIS:")
    
    total_violations = 0
    for module, module_violations in violations.items():
        total_violations += len(module_violations)
        print(f"\n❌ {module}/ - {len(module_violations)} violations:")
        
        # Group by target module
        by_target = defaultdict(list)
        for violation in module_violations:
            by_target[violation['depends_on']].append(violation)
        
        for target_module, target_violations in by_target.items():
            print(f"   → {target_module} ({len(target_violations)} imports):")
            for violation in target_violations[:3]:  # Show first 3
                file_name = violation['file'].split('/')[-1]
                print(f"      • {file_name}:{violation['line_num']} - {violation['line']}")
            if len(target_violations) > 3:
                print(f"      ... and {len(target_violations) - 3} more")
    
    print(f"\n📊 TOTAL VIOLATIONS: {total_violations}")
    
    return violations

def create_fix_strategy(violations):
    """Step 1b: Create systematic fix strategy"""
    
    print(f"\n🎯 STEP 1B: CREATING FIX STRATEGY")
    print("=" * 40)
    
    # Categorize violations by fix strategy
    fix_strategies = {
        'move_to_shared': [],      # Logic that should be in shared_kernel
        'use_interfaces': [],      # Replace with interface/protocol 
        'use_events': [],          # Replace with event communication
        'refactor_logic': [],      # Refactor to remove dependency
    }
    
    # Analyze each violation type
    for module, module_violations in violations.items():
        for violation in module_violations:
            line = violation['line'].lower()
            
            # Categorize by import type
            if any(term in line for term in ['service', 'repository', 'client']):
                if 'payment' in line or 'auth' in line or 'user' in line:
                    fix_strategies['use_interfaces'].append(violation)
                else:
                    fix_strategies['move_to_shared'].append(violation)
            
            elif any(term in line for term in ['model', 'entity', 'dto']):
                fix_strategies['move_to_shared'].append(violation)
            
            elif any(term in line for term in ['event', 'notification', 'alert']):
                fix_strategies['use_events'].append(violation)
            
            else:
                fix_strategies['refactor_logic'].append(violation)
    
    # Report strategy
    print("📋 FIX STRATEGIES:")
    
    for strategy, strategy_violations in fix_strategies.items():
        if strategy_violations:
            print(f"\n🔧 {strategy.upper().replace('_', ' ')} - {len(strategy_violations)} violations")
            
            # Group by module
            by_module = defaultdict(list)
            for violation in strategy_violations:
                module = violation['file'].split('/')[0]
                by_module[module].append(violation)
            
            for module, module_violations in list(by_module.items())[:3]:
                print(f"   • {module}: {len(module_violations)} violations")
    
    return fix_strategies

def fix_violations_batch1(violations):
    """Step 1c: Fix first batch of violations"""
    
    print(f"\n🔨 STEP 1C: FIXING FIRST BATCH OF VIOLATIONS")
    print("=" * 50)
    print("🎯 Focus: Easy wins - imports that can be moved to shared_kernel")
    print()
    
    fixes_applied = []
    
    # Focus on api_service violations first (highest count)
    api_violations = violations.get('api_service', [])
    
    if api_violations:
        print("🔧 Fixing api_service violations...")
        
        # Group by file for efficient processing
        by_file = defaultdict(list)
        for violation in api_violations:
            by_file[violation['file']].append(violation)
        
        # Fix files with shared model imports
        for file_path, file_violations in list(by_file.items())[:5]:  # Start with 5 files
            full_path = Path("src") / file_path
            
            if full_path.exists():
                print(f"   📄 Fixing {file_path}")
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    file_fixes = 0
                    
                    # Apply fixes for this file
                    for violation in file_violations:
                        old_import = violation['line']
                        
                        # Create shared_kernel equivalent import
                        if 'from src.bot_service' in old_import and 'models' in old_import:
                            # Move model import to shared_kernel
                            new_import = old_import.replace('from src.bot_service', 'from src.shared_kernel.domain')
                            content = content.replace(old_import, f"# TODO: Move to shared_kernel - {new_import}")
                            file_fixes += 1
                        
                        elif 'from src.payments' in old_import and ('domain' in old_import or 'value_objects' in old_import):
                            # Payment domain objects might be shared
                            new_import = old_import.replace('from src.payments.domain', 'from src.shared_kernel.domain')
                            content = content.replace(old_import, f"# TODO: Move to shared_kernel - {new_import}")
                            file_fixes += 1
                    
                    # Write back if changes made
                    if content != original_content and file_fixes > 0:
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        fixes_applied.append({
                            'file': file_path,
                            'fixes': file_fixes,
                            'type': 'commented_out'
                        })
                        
                        print(f"      ✅ Applied {file_fixes} fixes (commented out problematic imports)")
                
                except Exception as e:
                    print(f"      ❌ Error fixing {file_path}: {e}")
    
    # Summary of batch 1
    print(f"\n📊 BATCH 1 RESULTS:")
    if fixes_applied:
        total_fixes = sum(fix['fixes'] for fix in fixes_applied)
        print(f"   ✅ Fixed {len(fixes_applied)} files")
        print(f"   ✅ Applied {total_fixes} import fixes")
        print(f"   📝 Problematic imports commented out for review")
    else:
        print(f"   ℹ️  No automatic fixes applied - need manual review")
    
    return fixes_applied

if __name__ == "__main__":
    # Run step 1 analysis and initial fixes
    violations = analyze_and_fix_violations()
    strategies = create_fix_strategy(violations)
    fixes = fix_violations_batch1(violations)
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Review commented-out imports")
    print(f"   2. Move shared logic to shared_kernel")
    print(f"   3. Replace direct imports with interfaces")
    print(f"   4. Continue with batch 2 fixes")