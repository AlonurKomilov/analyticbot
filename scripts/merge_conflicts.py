#!/usr/bin/env python3
"""
Merge same-name different-content files into canonical locations.
"""
import os
import csv
import pathlib
import subprocess
import sys
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Priority patterns for canonical selection (higher number = higher priority)
CANONICAL_PATTERNS = [
    (r"^apps/api/", 100),
    (r"^apps/bot/", 90), 
    (r"^apps/frontend/", 80),
    (r"^core/", 70),
    (r"^infra/", 60),
    (r"^config/", 50),
    (r"^scripts/", 40),
    (r"^tests/", 30),
    (r"^docs/", 20),
]

# Patterns to deprioritize
DEPRIORITY_PATTERNS = [
    (r"^apis/", -50),
    (r"^bot/", -40),  # root bot/ vs apps/bot/
    (r"^archive/", -100),
    (r"^results/", -100),
    (r"/__pycache__/", -200),
    (r"\.pyc$", -200),
]

def score_path(path):
    """Score a path for canonical selection."""
    score = 0
    
    # Apply priority patterns
    for pattern, points in CANONICAL_PATTERNS:
        if re.search(pattern, path):
            score += points
            break
    
    # Apply depriority patterns
    for pattern, penalty in DEPRIORITY_PATTERNS:
        if re.search(pattern, path):
            score += penalty
    
    return score

def run_git_command(cmd):
    """Run git command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=ROOT, check=True, capture_output=True, text=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def should_skip_file(filename, paths):
    """Determine if we should skip processing this conflict."""
    # Skip binary/cache files
    if filename.endswith('.pyc') or '__pycache__' in ' '.join(paths):
        return True
    
    # Skip files that are only in cache directories
    cache_only = all('__pycache__' in p or '.pyc' in p for p in paths)
    if cache_only:
        return True
        
    # Skip node_modules
    if any('node_modules' in p for p in paths):
        return True
        
    return False

def choose_canonical(paths):
    """Choose the canonical path from a list of conflicting paths."""
    if not paths:
        return None
        
    # Score each path and return the highest scoring one
    scored_paths = [(score_path(p), p) for p in paths]
    scored_paths.sort(reverse=True)  # Highest score first
    
    return scored_paths[0][1]  # Return the path with highest score

def process_conflicts():
    """Process same-name conflicts and merge them."""
    conflicts_file = ROOT / "docs/reports/same_name_diff_content.csv"
    
    if not conflicts_file.exists():
        print("ERROR: docs/reports/same_name_diff_content.csv not found")
        return False
    
    processed = []
    
    # Increase CSV field size limit
    csv.field_size_limit(1000000)
    
    with open(conflicts_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        
        for row in reader:
            if len(row) < 3:
                continue
                
            filename, paths_str, hashes_str = row[0], row[1], row[2]
            
            # Parse paths and hashes
            paths = [p.strip() for p in paths_str.split('|') if p.strip()]
            hashes = [h.strip() for h in hashes_str.split('|') if h.strip()]
            
            if should_skip_file(filename, paths):
                continue
            
            # Focus on important files for manual review
            important_files = [
                'config.py', 'main.py', 'deps.py', 'models.py', '.env', 
                'index.html', '*.yaml', '*.yml', 'payment_routes.py'
            ]
            
            is_important = any(
                filename == imp_file or filename.endswith(imp_file.lstrip('*'))
                for imp_file in important_files
            )
            
            if not is_important:
                continue
            
            # Choose canonical path
            canonical = choose_canonical(paths)
            if not canonical:
                continue
                
            others = [p for p in paths if p != canonical]
            
            print(f"\n=== {filename} ===")
            print(f"Canonical: {canonical}")
            print(f"Others: {others}")
            print(f"Hashes: {len(hashes)} different versions")
            
            # Check if files exist
            canonical_exists = (ROOT / canonical).exists()
            others_exist = [p for p in others if (ROOT / p).exists()]
            
            print(f"Canonical exists: {canonical_exists}")
            print(f"Others exist: {len(others_exist)}/{len(others)}")
            
            if canonical_exists and others_exist:
                processed.append({
                    'filename': filename,
                    'canonical': canonical,
                    'others': others_exist,
                    'action': 'NEEDS_MANUAL_REVIEW'
                })
            
    return processed

def main():
    """Main execution."""
    print("=== Same-Name Conflicts Analysis ===")
    
    conflicts = process_conflicts()
    
    if not conflicts:
        print("No important conflicts found that need processing.")
        return True
    
    print(f"\n=== SUMMARY ===")
    print(f"Found {len(conflicts)} important conflicts that need manual review:")
    
    for conflict in conflicts:
        print(f"\n{conflict['filename']}:")
        print(f"  Canonical: {conflict['canonical']}")
        print(f"  Others: {conflict['others']}")
    
    print(f"\nNext steps:")
    print(f"1. Review each conflict manually")
    print(f"2. Merge logic into canonical files")
    print(f"3. Archive non-canonical versions")
    
    return True

if __name__ == "__main__":
    if main():
        print("\nConflict analysis complete!")
    else:
        print("\nAnalysis failed!")
        sys.exit(1)
