#!/usr/bin/env python3
"""
Frontend API Usage Scanner
=========================
Scans frontend files for API endpoint usage patterns
"""

import os
import re
from typing import Set, List, Dict
from pathlib import Path

def extract_api_calls_from_file(file_path: str) -> Set[str]:
    """Extract API endpoints from a single file"""
    api_calls = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, IOError):
        return api_calls
    
    # Patterns to match API calls
    patterns = [
        # Direct string literals for endpoints
        r'[\'"`](/[^\'"`\s]+)[\'"`]',
        # fetch(), axios, apiClient calls with string endpoints
        r'(?:fetch|get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"`\s]+)[\'"`]',
        # Template literals
        r'`([^`]*(?:/api/|/analytics/|/auth/|/health|/admin|/channels/|/payments/|/content/|/mobile/|/ai/|/exports/|/share/|/superadmin/|/clean/)[^`]*)`',
        # URL construction patterns
        r'url\s*[=:]\s*[\'"`]([^\'"`\s]+)[\'"`]',
        r'endpoint\s*[=:]\s*[\'"`]([^\'"`\s]+)[\'"`]',
        r'path\s*[=:]\s*[\'"`]([^\'"`\s]+)[\'"`]',
        # Route patterns in template literals
        r'`[^`]*/([a-z-]+(?:/[a-z-]+)*)/[^`]*`'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            path = match.group(1)
            # Filter for actual API paths
            if path and ('/' in path and 
                        any(api_part in path.lower() for api_part in [
                            'api/', 'analytics/', 'auth/', 'health', 'admin/',
                            'channels/', 'payments/', 'content/', 'mobile/',
                            'ai/', 'exports/', 'share/', 'superadmin/', 'clean/'
                        ])):
                api_calls.add(path)
    
    # Look for dynamic endpoint construction patterns
    dynamic_patterns = [
        r'/analytics/[^/\s\'"`]+',
        r'/api/v[0-9]+/[^/\s\'"`]+',
        r'/channels/[^/\s\'"`]+',
        r'/auth/[^/\s\'"`]+',
        r'/admin/[^/\s\'"`]+',
        r'/payments/[^/\s\'"`]+',
        r'/ai/[^/\s\'"`]+',
        r'/health[^/\s\'"`]*',
        r'/exports/[^/\s\'"`]+',
        r'/share/[^/\s\'"`]+',
        r'/mobile/[^/\s\'"`]+',
        r'/superadmin/[^/\s\'"`]+',
        r'/content/[^/\s\'"`]+',
        r'/clean/[^/\s\'"`]+'
    ]
    
    for pattern in dynamic_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            api_calls.add(match.group(0))
    
    # Clean up and standardize the paths
    cleaned_calls = set()
    for call in api_calls:
        # Remove query parameters and fragments
        cleaned_call = re.sub(r'[?#].*', '', call)
        # Remove trailing slashes except for root paths
        if len(cleaned_call) > 1:
            cleaned_call = cleaned_call.rstrip('/')
        cleaned_calls.add(cleaned_call)
    
    return cleaned_calls

def scan_directory_for_api_calls(directory: str) -> Dict[str, Set[str]]:
    """Scan directory for API calls"""
    results = {}
    
    # Supported file extensions
    extensions = ['.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte']
    
    for root, dirs, files in os.walk(directory):
        # Skip node_modules and other build directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'build', 'dist', '.git']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                api_calls = extract_api_calls_from_file(file_path)
                
                if api_calls:
                    relative_path = os.path.relpath(file_path, '/home/alonur/analyticbot')
                    results[relative_path] = api_calls
    
    return results

def normalize_endpoint(endpoint: str) -> str:
    """Normalize endpoint for comparison"""
    # Remove dynamic parts and parameters
    normalized = re.sub(r'\{[^}]+\}', '{id}', endpoint)
    normalized = re.sub(r'/[0-9]+', '/{id}', normalized)
    normalized = re.sub(r'\$\{[^}]+\}', '{id}', normalized)
    normalized = re.sub(r'[?#].*', '', normalized)
    
    # Remove trailing slash
    if len(normalized) > 1:
        normalized = normalized.rstrip('/')
    
    return normalized

def main():
    print("🔍 Frontend API Usage Scanner")
    print("=" * 50)
    
    # Scan frontend directory
    frontend_results = scan_directory_for_api_calls('/home/alonur/analyticbot/apps/frontend/src')
    
    # Collect all unique API calls
    all_api_calls = set()
    total_files = len(frontend_results)
    
    print(f"\n📊 Found API calls in {total_files} frontend files\n")
    
    for file_path, api_calls in sorted(frontend_results.items()):
        print(f"📁 {file_path}")
        print(f"   API calls: {len(api_calls)}")
        
        for call in sorted(api_calls):
            print(f"   - {call}")
            all_api_calls.add(call)
        
        print()
    
    print(f"📈 SUMMARY:")
    print(f"   Total Files: {total_files}")
    print(f"   Total Unique API Calls: {len(all_api_calls)}")
    
    # Generate normalized endpoint list
    print(f"\n📋 All Frontend API Calls (Normalized):")
    print(f"=" * 50)
    
    normalized_calls = set()
    for call in all_api_calls:
        normalized_calls.add(normalize_endpoint(call))
    
    for call in sorted(normalized_calls):
        print(call)
    
    return normalized_calls

if __name__ == "__main__":
    main()