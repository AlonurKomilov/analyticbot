#!/usr/bin/env python3
"""
Check for hardcoded strings in frontend files that should use i18n
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

def is_likely_user_facing_text(text: str) -> bool:
    """Check if text is likely user-facing and should be translated"""
    # Filter out common non-translatable strings
    if len(text.strip()) < 3:
        return False
    
    # Skip common technical strings
    technical_patterns = [
        r'^[A-Z_]+$',  # ALL_CAPS constants
        r'^\d+$',  # Pure numbers
        r'^[a-z]+$',  # Single lowercase word (likely property names)
        r'^className$|^style$|^id$',  # Common props
        r'^(px|em|rem|%|auto|none|flex|grid|block|inline)$',  # CSS values
        r'^(GET|POST|PUT|DELETE|PATCH)$',  # HTTP methods
        r'^(src|alt|href|type|name)$',  # HTML attributes
        r'^\$\{',  # Template literal variables
        r'^(true|false|null|undefined)$',  # JS literals
        r'^https?://',  # URLs
        r'^/[a-z-/]*$',  # Routes
        r'^[a-z_]+\.[a-z_]+$',  # Property accessors like obj.prop
        r'^\w+\(\)$',  # Function calls
        r'^[@#$%]',  # Symbols
    ]
    
    for pattern in technical_patterns:
        if re.match(pattern, text.strip(), re.IGNORECASE):
            return False
    
    # Check if it's a sentence or phrase with spaces
    if ' ' in text.strip() and len(text.strip()) > 10:
        return True
    
    # Check if it starts with capital letter (likely a label or title)
    if text.strip()[0].isupper() and len(text.strip()) > 5:
        return True
    
    return False

def extract_jsx_strings(content: str) -> List[Tuple[int, str]]:
    """Extract string literals from JSX/TSX content"""
    strings = []
    
    # Pattern for strings in JSX: {"string"} or {'string'} or >string<
    patterns = [
        # String in braces: {"text"} or {'text'}
        (r'\{["\']([^"\']+)["\']\}', 1),
        # JSX text content between tags: >text<
        (r'>\s*([^<>{}\s][^<>{}]*[^<>{}\s])\s*<', 1),
        # String props: prop="text" or prop='text'
        (r'\w+=["\']([^"\']{3,})["\']\s', 1),
    ]
    
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('//') or line.strip().startswith('/*') or line.strip().startswith('*'):
            continue
        
        for pattern, group in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                text = match.group(group).strip()
                if is_likely_user_facing_text(text):
                    strings.append((line_num, text))
    
    return strings

def check_file_for_i18n(filepath: Path) -> Dict:
    """Check if file uses i18n and find hardcoded strings"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}
    
    # Check if file uses i18n
    uses_i18n = bool(
        re.search(r'useTranslation|import.*i18next|import.*i18n', content) or
        re.search(r'\bt\(["\']', content)  # t() function calls
    )
    
    # Find potential hardcoded strings
    hardcoded = extract_jsx_strings(content)
    
    return {
        'uses_i18n': uses_i18n,
        'hardcoded_strings': hardcoded,
        'has_issues': not uses_i18n and len(hardcoded) > 0
    }

def analyze_frontend():
    """Analyze frontend files for i18n usage"""
    base_path = Path("/home/abcdev/projects/analyticbot/apps/frontend/apps/user/src")
    
    # Skip certain directories
    skip_dirs = {'node_modules', 'test', '__tests__', 'tests', 'i18n', 'types', 'config', 'utils'}
    skip_patterns = ['.test.', '.spec.', 'types.ts', 'index.ts', 'exports.ts', 'constants.ts']
    
    print("=" * 100)
    print("FRONTEND I18N HARDCODED STRINGS ANALYSIS")
    print("=" * 100)
    print()
    
    files_checked = 0
    files_with_i18n = 0
    files_without_i18n = 0
    files_with_hardcoded = 0
    problematic_files = []
    
    # Scan all tsx and jsx files
    for root, dirs, files in os.walk(base_path):
        # Skip directories
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
        
        rel_root = Path(root).relative_to(base_path)
        
        for file in files:
            if not (file.endswith('.tsx') or file.endswith('.jsx')):
                continue
            
            # Skip test files and certain patterns
            if any(pattern in file for pattern in skip_patterns):
                continue
            
            filepath = Path(root) / file
            rel_path = filepath.relative_to(base_path)
            
            result = check_file_for_i18n(filepath)
            
            if 'error' in result:
                continue
            
            files_checked += 1
            
            if result['uses_i18n']:
                files_with_i18n += 1
            else:
                files_without_i18n += 1
            
            if result['hardcoded_strings']:
                files_with_hardcoded += 1
            
            if result['has_issues'] and len(result['hardcoded_strings']) >= 3:
                problematic_files.append({
                    'path': str(rel_path),
                    'full_path': str(filepath),
                    'uses_i18n': result['uses_i18n'],
                    'strings': result['hardcoded_strings']
                })
    
    # Print summary
    print(f"📊 Summary:")
    print(f"  Total files checked: {files_checked}")
    print(f"  Files using i18n: {files_with_i18n} ({files_with_i18n/files_checked*100:.1f}%)")
    print(f"  Files NOT using i18n: {files_without_i18n} ({files_without_i18n/files_checked*100:.1f}%)")
    print(f"  Files with potential hardcoded strings: {files_with_hardcoded}")
    print()
    
    # Sort by number of hardcoded strings
    problematic_files.sort(key=lambda x: len(x['strings']), reverse=True)
    
    if problematic_files:
        print(f"⚠️  Found {len(problematic_files)} files with hardcoded strings that may need i18n:")
        print("=" * 100)
        
        for idx, file_info in enumerate(problematic_files[:30], 1):  # Show top 30
            print(f"\n{idx}. {file_info['path']}")
            print(f"   Uses i18n: {'✅ Yes' if file_info['uses_i18n'] else '❌ No'}")
            print(f"   Found {len(file_info['strings'])} potential hardcoded strings:")
            
            # Show first 3 strings
            for line_num, text in file_info['strings'][:3]:
                preview = text[:70] + "..." if len(text) > 70 else text
                print(f"     Line {line_num}: \"{preview}\"")
            
            if len(file_info['strings']) > 3:
                print(f"     ... and {len(file_info['strings']) - 3} more")
        
        if len(problematic_files) > 30:
            print(f"\n... and {len(problematic_files) - 30} more files")
        
        # Group by feature/directory
        print("\n\n📂 FILES BY DIRECTORY:")
        print("=" * 100)
        by_dir = {}
        for file_info in problematic_files:
            dir_name = file_info['path'].split('/')[0] if '/' in file_info['path'] else 'root'
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append(file_info)
        
        for dir_name in sorted(by_dir.keys()):
            files = by_dir[dir_name]
            total_strings = sum(len(f['strings']) for f in files)
            print(f"\n{dir_name}/ ({len(files)} files, {total_strings} strings)")
            for f in files:
                print(f"  - {f['path'].split('/')[-1]} ({len(f['strings'])} strings)")
    else:
        print("✅ Great! No files with significant hardcoded strings found.")
    
    print("\n" + "=" * 100)

if __name__ == '__main__':
    analyze_frontend()
