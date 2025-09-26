#!/usr/bin/env python3
"""
Step 1d: Final Dependency Analysis and Progress Report
"""

import os
from pathlib import Path

def count_current_violations():
    """Count remaining dependency violations"""
    
    print("📊 STEP 1D: FINAL VIOLATION ANALYSIS")
    print("=" * 37)
    
    violation_count = 0
    detailed_violations = []
    
    # Get all Python files in src/ modules (excluding shared_kernel)
    src_path = Path("src")
    modules = [d for d in src_path.iterdir() if d.is_dir() and d.name != "shared_kernel"]
    
    for module_dir in modules:
        module_name = module_dir.name
        module_violations = []
        
        for py_file in module_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for imports from other modules
                for other_module in modules:
                    if other_module.name != module_name:
                        import_pattern = f"from src.{other_module.name}"
                        if import_pattern in content:
                            lines = content.split('\\n')
                            for i, line in enumerate(lines, 1):
                                if import_pattern in line and not line.strip().startswith('#'):
                                    module_violations.append({
                                        'file': str(py_file.relative_to(src_path)),
                                        'line': i,
                                        'target_module': other_module.name,
                                        'import_line': line.strip()
                                    })
                                    violation_count += 1
            
            except Exception:
                continue
        
        if module_violations:
            detailed_violations.append({
                'module': module_name,
                'violations': module_violations,
                'count': len(module_violations)
            })
    
    # Print summary
    print(f"🎯 TOTAL REMAINING VIOLATIONS: {violation_count}")
    print()
    
    # Print top violators
    sorted_violations = sorted(detailed_violations, key=lambda x: x['count'], reverse=True)
    
    print("📋 TOP MODULE VIOLATORS:")
    for violation_group in sorted_violations[:5]:  # Top 5
        module = violation_group['module']
        count = violation_group['count']
        print(f"   ❌ {module}: {count} violations")
        
        # Show some examples
        for violation in violation_group['violations'][:3]:  # First 3 examples
            print(f"      📄 {violation['file']}:{violation['line']} → {violation['target_module']}")
        
        if len(violation_group['violations']) > 3:
            remaining = len(violation_group['violations']) - 3
            print(f"      ... and {remaining} more")
        print()
    
    return violation_count, detailed_violations

def show_fixes_applied():
    """Show what fixes have been successfully applied"""
    
    print("✅ STEP 1A-C FIXES SUCCESSFULLY APPLIED:")
    print("=" * 42)
    
    fixes_applied = []
    
    # Check if shared interfaces were created
    interfaces_dir = Path("src/shared_kernel/domain/interfaces")
    if interfaces_dir.exists():
        interface_files = list(interfaces_dir.glob("*.py"))
        print(f"🎯 Created {len(interface_files)} shared interface files:")
        for f in interface_files:
            print(f"   📄 {f.name}")
            fixes_applied.append(f"interface: {f.name}")
        print()
    
    # Check if database utilities were created  
    db_dir = Path("src/shared_kernel/infrastructure/database")
    if db_dir.exists():
        db_files = list(db_dir.glob("*.py"))
        print(f"🎯 Created {len(db_files)} shared database utility files:")
        for f in db_files:
            print(f"   📄 {f.name}")
            fixes_applied.append(f"database: {f.name}")
        print()
    
    # Check if shared exceptions were created
    exceptions_file = Path("src/shared_kernel/domain/exceptions.py")
    if exceptions_file.exists():
        print(f"🎯 Created shared exception classes:")
        print(f"   📄 exceptions.py")
        fixes_applied.append("exceptions: exceptions.py")
        print()
    
    return fixes_applied

def recommend_next_actions(violations_data):
    """Recommend specific next actions based on remaining violations"""
    
    print("🚀 RECOMMENDED NEXT ACTIONS:")
    print("=" * 28)
    
    # Group violations by type for better recommendations
    recommendations = []
    
    for violation_group in violations_data:
        module = violation_group['module']
        violations = violation_group['violations']
        
        # Analyze violation patterns
        target_modules = {}
        for v in violations:
            target = v['target_module']
            if target not in target_modules:
                target_modules[target] = 0
            target_modules[target] += 1
        
        # Create specific recommendations
        for target, count in target_modules.items():
            if count >= 5:  # Many violations to same module
                recommendations.append({
                    'priority': 'HIGH',
                    'action': f'Create interface layer between {module} and {target}',
                    'count': count,
                    'type': 'interface_creation'
                })
            elif count >= 2:  # Few violations
                recommendations.append({
                    'priority': 'MEDIUM', 
                    'action': f'Move shared logic from {target} to shared_kernel',
                    'count': count,
                    'type': 'move_to_shared'
                })
            else:
                recommendations.append({
                    'priority': 'LOW',
                    'action': f'Refactor direct dependency: {module} → {target}',
                    'count': count,
                    'type': 'refactoring'
                })
    
    # Sort by priority and count
    priority_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    recommendations.sort(key=lambda x: (priority_order[x['priority']], x['count']), reverse=True)
    
    # Print top recommendations
    print("🎯 TOP PRIORITY ACTIONS:")
    for i, rec in enumerate(recommendations[:8], 1):  # Top 8 recommendations
        priority = rec['priority']
        action = rec['action']
        count = rec['count']
        
        priority_icon = "🔥" if priority == "HIGH" else "⚠️" if priority == "MEDIUM" else "💡"
        print(f"   {priority_icon} {priority}: {action} ({count} violations)")
    
    return recommendations

if __name__ == "__main__":
    print("🚀 STEP 1D: FINAL ANALYSIS & PROGRESS REPORT")
    print()
    
    # Count remaining violations
    total_violations, violations_data = count_current_violations()
    
    # Show fixes that were applied
    fixes_applied = show_fixes_applied()
    
    # Get recommendations for next steps
    recommendations = recommend_next_actions(violations_data)
    
    # Final summary
    print("📊 STEP 1 COMPLETION SUMMARY:")
    print("=" * 30)
    print(f"   📈 Violations remaining: {total_violations}")
    print(f"   ✅ Infrastructure fixes applied: {len(fixes_applied)}")
    print(f"   🎯 Priority recommendations: {len([r for r in recommendations if r['priority'] == 'HIGH'])}")
    print()
    
    if total_violations < 30:  # Less than 30 violations remaining
        print("🎉 STEP 1 MAJOR PROGRESS!")
        print("   📈 Significant reduction in module coupling")
        print("   🔧 Ready for Step 2: Complete shared infrastructure")
    else:
        print("⚠️  STEP 1 NEEDS MORE WORK")
        print("   🔧 Continue fixing high-priority violations")
        print("   🎯 Focus on interface creation and shared logic movement")
    
    print(f"\\n🔄 Next: Continue with Step 2 of Module Monolith optimization")