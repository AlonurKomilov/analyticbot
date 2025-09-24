#!/usr/bin/env python3
"""
Backend API Endpoint Extractor
=============================
Extracts all FastAPI endpoints from router files
"""

import os
import re
from typing import Dict, List, Tuple
from pathlib import Path

def extract_router_info(file_path: str) -> Tuple[str, List[Dict[str, str]]]:
    """Extract router prefix and endpoints from a Python router file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract router prefix
    prefix_match = re.search(r'router\s*=\s*APIRouter\s*\([^)]*prefix\s*=\s*["\']([^"\']+)["\']', content)
    prefix = prefix_match.group(1) if prefix_match else ""
    
    # Extract all endpoints
    endpoints = []
    # Pattern to match @router.method("path")
    endpoint_pattern = r'@router\.(get|post|put|delete|patch|head|options)\s*\(\s*["\']([^"\']+)["\']'
    
    for match in re.finditer(endpoint_pattern, content, re.IGNORECASE):
        method = match.group(1).upper()
        path = match.group(2)
        full_path = f"{prefix}{path}" if prefix else path
        
        endpoints.append({
            'method': method,
            'path': path,
            'full_path': full_path,
            'file': os.path.basename(file_path)
        })
    
    return prefix, endpoints

def scan_directory(directory: str) -> Dict[str, List[Dict[str, str]]]:
    """Scan directory for router files and extract endpoints"""
    results = {}
    
    router_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file not in ['__init__.py']:
                router_files.append(os.path.join(root, file))
    
    for file_path in router_files:
        try:
            prefix, endpoints = extract_router_info(file_path)
            if endpoints:  # Only include files with actual endpoints
                relative_path = os.path.relpath(file_path, '/home/alonur/analyticbot')
                results[relative_path] = {
                    'prefix': prefix,
                    'endpoints': endpoints
                }
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return results

def main():
    print("🔍 Backend API Endpoint Discovery")
    print("=" * 50)
    
    # Scan API routers
    api_results = scan_directory('/home/alonur/analyticbot/apps/api/routers')
    
    # Scan Bot API routers  
    bot_results = scan_directory('/home/alonur/analyticbot/apps/bot/api')
    
    # Combine results
    all_results = {**api_results, **bot_results}
    
    # Print detailed results
    total_endpoints = 0
    total_files = len(all_results)
    
    print(f"\n📊 Found {total_files} router files with endpoints\n")
    
    for file_path, data in sorted(all_results.items()):
        prefix = data['prefix']
        endpoints = data['endpoints']
        
        print(f"📁 {file_path}")
        print(f"   Prefix: {prefix if prefix else '(no prefix)'}")
        print(f"   Endpoints: {len(endpoints)}")
        
        for endpoint in endpoints:
            print(f"   - {endpoint['method']:6} {endpoint['full_path']}")
        
        print()
        total_endpoints += len(endpoints)
    
    print(f"📈 SUMMARY:")
    print(f"   Total Files: {total_files}")
    print(f"   Total Endpoints: {total_endpoints}")
    
    # Generate endpoint list for comparison
    print(f"\n📋 Complete Endpoint List:")
    print(f"=" * 50)
    
    all_endpoints = []
    for data in all_results.values():
        all_endpoints.extend(data['endpoints'])
    
    # Sort by method then path
    all_endpoints.sort(key=lambda x: (x['method'], x['full_path']))
    
    for endpoint in all_endpoints:
        print(f"{endpoint['method']:6} {endpoint['full_path']}")

if __name__ == "__main__":
    main()