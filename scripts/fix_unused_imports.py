#!/usr/bin/env python3
"""
Script to fix unused imports in React/JavaScript files using Pylance
"""
import os
import sys
from pathlib import Path

def get_workspace_root():
    """Get the workspace root directory"""
    return "file:///home/alonur/analyticbot"

def check_and_fix_unused_imports():
    """Check for unused imports in frontend files and fix them"""
    
    # Correct frontend directory
    frontend_files = [
        "/home/alonur/analyticbot/apps/frontend/src/components/AnalyticsDashboard.jsx",
        "/home/alonur/analyticbot/apps/frontend/src/components/DataSourceSettings.jsx", 
        "/home/alonur/analyticbot/apps/frontend/src/components/EnhancedMediaUploader.jsx",
        "/home/alonur/analyticbot/apps/frontend/src/components/StorageFileBrowser.jsx",
        "/home/alonur/analyticbot/apps/frontend/src/components/PostViewDynamicsChart.jsx",
        "/home/alonur/analyticbot/apps/frontend/src/components/BestTimeRecommender.jsx",
        "/home/alonur/analyticbot/apps/frontend/src/App.jsx",
        "/home/alonur/analyticbot/apps/frontend/src/main.jsx"
    ]
    
    print("🔧 Checking for unused imports in frontend files...")
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {os.path.basename(file_path)}")
            
            # Check if file has unused imports
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for common unused import patterns
            lines = content.split('\n')
            import_lines = []
            used_imports = set()
            
            # Find import statements
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') and 'from ' in line:
                    import_lines.append((i, line))
                    
            # Basic check for unused imports
            for line_num, import_line in import_lines:
                # Extract imported names
                if ' from ' in import_line:
                    parts = import_line.split(' from ')
                    if len(parts) >= 2:
                        imported_part = parts[0].replace('import', '').strip()
                        
                        # Handle different import styles
                        if imported_part.startswith('{') and imported_part.endswith('}'):
                            # Named imports: import { A, B, C } from 'module'
                            imports = imported_part[1:-1].split(',')
                            for imp in imports:
                                import_name = imp.strip()
                                # Check if this import is used in the file
                                if import_name and import_name in content.replace(import_line, ''):
                                    used_imports.add(import_name)
                                else:
                                    print(f"  ⚠️  Potentially unused import: {import_name}")
                                    
        else:
            print(f"❌ Not found: {file_path}")
            
def analyze_file_imports(file_path):
    """Analyze a specific file for unused imports"""
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        issues = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for imports
            if line.startswith('import ') and ' from ' in line:
                # Extract module name
                parts = line.split(' from ')
                if len(parts) >= 2:
                    module = parts[1].strip().strip('\'";\'')
                    imported_part = parts[0].replace('import', '').strip()
                    
                    # Check different import patterns
                    if imported_part.startswith('{') and imported_part.endswith('}'):
                        # Named imports
                        imports = imported_part[1:-1].split(',')
                        for imp in imports:
                            imp_name = imp.strip()
                            # Simple usage check
                            rest_of_file = '\n'.join(lines[i:])  # Don't include the import line itself
                            if imp_name and imp_name not in rest_of_file:
                                issues.append(f"Line {i}: Potentially unused import '{imp_name}' from {module}")
                                
        return issues
        
    except Exception as e:
        return [f"Error analyzing {file_path}: {str(e)}"]

if __name__ == "__main__":
    print("🔍 Frontend Import Analysis")
    print("=" * 50)
    
    # Analyze key frontend files
    files_to_check = [
        "/home/alonur/analyticbot/apps/frontend/src/components/AnalyticsDashboard.jsx",
        "/home/alonur/analyticbot/apps/frontend/src/components/DataSourceSettings.jsx",
        "/home/alonur/analyticbot/apps/frontend/src/App.jsx"
    ]
    
    for file_path in files_to_check:
        print(f"\n📄 Analyzing: {os.path.basename(file_path)}")
        print("-" * 40)
        
        issues = analyze_file_imports(file_path)
        if isinstance(issues, list):
            if issues:
                for issue in issues:
                    print(f"⚠️  {issue}")
            else:
                print("✅ No unused imports detected")
        else:
            print(f"❌ {issues}")
            
    print("\n" + "=" * 50)
    print("Analysis complete!")
