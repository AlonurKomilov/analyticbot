# 🎯 API RESTRUCTURE - PHASE 0: PREPARATION

**Architecture Choice:** Option A - Flat Resources
**Start Date:** November 23, 2025
**Timeline:** 2-3 days for Phase 0
**Risk Level:** LOW (read-only analysis, no changes yet)

---

## 📋 PHASE 0 OBJECTIVES

**Goal:** Understand exactly what we have before making ANY changes

1. ✅ Map all current endpoints
2. ✅ Identify which endpoints are actually used
3. ✅ Find all frontend API calls
4. ✅ Create detailed migration plan for each endpoint
5. ✅ Set up safety mechanisms (backups, monitoring)

**NO CODE CHANGES in Phase 0** - only analysis and planning!

---

## 🔍 STEP 1: ANALYZE CURRENT API STRUCTURE

### 1.1 Extract All Router Registrations

**What we're doing:** Find every `include_router` call in main.py

**Script:**
```bash
cd /home/abcdeveloper/projects/analyticbot

# Extract all router registrations
grep -n "include_router" apps/api/main.py > reports/current_routers.txt

# Count them
echo "Total routers registered: $(grep -c 'include_router' apps/api/main.py)"
```

**Expected output:** List of all ~25-30 router registrations with line numbers

---

### 1.2 Map Current Endpoint Structure

**What we're doing:** Get actual endpoint list from OpenAPI spec

**Script:**
```python
# scripts/phase0_analyze_current_structure.py
"""
Phase 0: Analyze current API structure
Creates detailed reports of all endpoints
"""

import json
import requests
from collections import defaultdict
from pathlib import Path

# Ensure reports directory exists
Path("reports").mkdir(exist_ok=True)

print("=" * 100)
print("🔍 PHASE 0: ANALYZING CURRENT API STRUCTURE")
print("=" * 100)

# Download OpenAPI spec
print("\n📥 Downloading OpenAPI spec from http://localhost:11400/openapi.json")
try:
    response = requests.get("http://localhost:11400/openapi.json", timeout=5)
    spec = response.json()

    # Save for reference
    with open("reports/openapi_current.json", "w") as f:
        json.dump(spec, f, indent=2)
    print("✅ Saved to reports/openapi_current.json")
except Exception as e:
    print(f"❌ Error: {e}")
    print("⚠️  Make sure API server is running: make dev")
    exit(1)

# Analyze endpoints by prefix
print("\n" + "=" * 100)
print("📊 CURRENT ENDPOINT DISTRIBUTION")
print("=" * 100)

prefix_groups = defaultdict(list)
all_endpoints = []

for path, methods in spec['paths'].items():
    for method in methods.keys():
        if method in ['get', 'post', 'put', 'delete', 'patch']:
            endpoint_info = {
                'method': method.upper(),
                'path': path,
                'summary': methods[method].get('summary', 'No description'),
                'tags': methods[method].get('tags', ['untagged']),
                'operationId': methods[method].get('operationId', 'unknown')
            }
            all_endpoints.append(endpoint_info)

            # Group by first-level prefix
            parts = path.strip('/').split('/')
            prefix = '/' + parts[0] if parts else '/'
            prefix_groups[prefix].append(endpoint_info)

# Sort by endpoint count
sorted_prefixes = sorted(prefix_groups.items(), key=lambda x: len(x[1]), reverse=True)

print(f"\n📈 Total Endpoints: {len(all_endpoints)}")
print(f"📁 Total Prefix Groups: {len(prefix_groups)}")
print("\n" + "-" * 100)

# Create detailed report
with open("reports/phase0_current_structure.txt", "w") as report:
    report.write("=" * 100 + "\n")
    report.write("PHASE 0: CURRENT API STRUCTURE ANALYSIS\n")
    report.write("=" * 100 + "\n\n")
    report.write(f"Total Endpoints: {len(all_endpoints)}\n")
    report.write(f"Total Prefix Groups: {len(prefix_groups)}\n\n")

    for prefix, endpoints in sorted_prefixes:
        count = len(endpoints)
        print(f"{prefix:30} → {count:3} endpoints")

        report.write("-" * 100 + "\n")
        report.write(f"PREFIX: {prefix} ({count} endpoints)\n")
        report.write("-" * 100 + "\n")

        for ep in endpoints:
            report.write(f"  {ep['method']:6} {ep['path']}\n")
            report.write(f"         Summary: {ep['summary']}\n")
            report.write(f"         Tags: {', '.join(ep['tags'])}\n")
            report.write(f"         OperationId: {ep['operationId']}\n")
            report.write("\n")

    print("\n✅ Detailed report saved to reports/phase0_current_structure.txt")

# Identify duplicates and issues
print("\n" + "=" * 100)
print("🚨 POTENTIAL ISSUES DETECTED")
print("=" * 100)

issues = []

# Check for duplicate patterns
duplicate_patterns = [
    ('/payment', '/payments'),
    ('/ai', '/ai-chat'),
    ('/ai', '/ai-insights'),
    ('/ai', '/ai-services'),
    ('/content', '/content-protection'),
]

for old, new in duplicate_patterns:
    if old in prefix_groups and new in prefix_groups:
        issues.append(f"DUPLICATE: {old} ({len(prefix_groups[old])}) and {new} ({len(prefix_groups[new])})")

# Check for nested redundancy
for prefix in prefix_groups.keys():
    parts = prefix.strip('/').split('/')
    if len(parts) > 1 and parts[0] == parts[1]:
        issues.append(f"NESTED REDUNDANCY: {prefix}")

# Check for inconsistent /api prefix
api_prefixes = [p for p in prefix_groups.keys() if p.startswith('/api/')]
non_api_prefixes = [p for p in prefix_groups.keys() if not p.startswith('/api/') and p != '/health']

if api_prefixes and non_api_prefixes:
    issues.append(f"INCONSISTENT PREFIX: {len(api_prefixes)} with /api, {len(non_api_prefixes)} without")

if issues:
    for issue in issues:
        print(f"⚠️  {issue}")
else:
    print("✅ No major issues detected")

# Save issues
with open("reports/phase0_issues.txt", "w") as f:
    for issue in issues:
        f.write(issue + "\n")

print("\n" + "=" * 100)
print("✅ PHASE 0 STEP 1 COMPLETE")
print("=" * 100)
print("\nGenerated files:")
print("  - reports/openapi_current.json")
print("  - reports/phase0_current_structure.txt")
print("  - reports/phase0_issues.txt")
print("\nNext: Run Step 2 to analyze API usage from logs")
```

**Run it:**
```bash
cd /home/abcdeveloper/projects/analyticbot
python3 scripts/phase0_analyze_current_structure.py
```

---

## 📊 STEP 2: ANALYZE ACTUAL ENDPOINT USAGE

### 2.1 Analyze API Logs

**What we're doing:** Find out which endpoints are actually being used

**Script:**
```python
# scripts/phase0_analyze_usage.py
"""
Phase 0: Analyze which endpoints are actually used
Parse logs to understand traffic patterns
"""

import re
from collections import Counter
from pathlib import Path
import glob

print("=" * 100)
print("📊 PHASE 0: ANALYZING API USAGE FROM LOGS")
print("=" * 100)

# Parse all log files
endpoint_usage = Counter()
method_usage = Counter()
error_endpoints = Counter()

log_files = glob.glob("logs/*.log")
print(f"\n🔍 Scanning {len(log_files)} log files...")

http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']

for log_file in log_files:
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Look for HTTP method and path
                for method in http_methods:
                    if method in line:
                        # Try to extract the endpoint path
                        # Pattern: METHOD /path/to/endpoint
                        match = re.search(rf'{method}\s+(/[^\s\?"]*)', line)
                        if match:
                            path = match.group(1)
                            endpoint = f"{method} {path}"
                            endpoint_usage[endpoint] += 1
                            method_usage[method] += 1

                            # Check for errors (status code 4xx or 5xx)
                            if re.search(r'\s[45]\d{2}\s', line):
                                error_endpoints[endpoint] += 1
    except Exception as e:
        print(f"⚠️  Error reading {log_file}: {e}")

print(f"✅ Analyzed {sum(endpoint_usage.values())} API requests")

# Save detailed usage report
print("\n" + "=" * 100)
print("🔥 TOP 50 MOST-USED ENDPOINTS")
print("=" * 100)

with open("reports/phase0_endpoint_usage.txt", "w") as report:
    report.write("=" * 100 + "\n")
    report.write("PHASE 0: ENDPOINT USAGE ANALYSIS\n")
    report.write("=" * 100 + "\n\n")
    report.write(f"Total API Requests: {sum(endpoint_usage.values())}\n")
    report.write(f"Unique Endpoints: {len(endpoint_usage)}\n\n")

    report.write("METHOD DISTRIBUTION:\n")
    report.write("-" * 50 + "\n")
    for method, count in method_usage.most_common():
        report.write(f"  {method:8} {count:>8} requests\n")

    report.write("\n\nTOP 50 MOST-USED ENDPOINTS:\n")
    report.write("-" * 100 + "\n")

    for i, (endpoint, count) in enumerate(endpoint_usage.most_common(50), 1):
        print(f"{i:2}. {count:>6} requests → {endpoint}")
        report.write(f"{i:2}. {count:>6} requests → {endpoint}\n")

    if error_endpoints:
        report.write("\n\nENDPOINTS WITH ERRORS:\n")
        report.write("-" * 100 + "\n")
        for endpoint, count in error_endpoints.most_common(20):
            report.write(f"  {count:>6} errors → {endpoint}\n")

print(f"\n✅ Report saved to reports/phase0_endpoint_usage.txt")

# Identify unused endpoints (need to compare with current structure)
print("\n" + "=" * 100)
print("📋 SUMMARY")
print("=" * 100)
print(f"Total API requests analyzed: {sum(endpoint_usage.values())}")
print(f"Unique endpoints used: {len(endpoint_usage)}")
print(f"Endpoints with errors: {len(error_endpoints)}")
print("\nNext: Run Step 3 to analyze frontend API calls")
```

**Run it:**
```bash
cd /home/abcdeveloper/projects/analyticbot
python3 scripts/phase0_analyze_usage.py
```

---

## 🖥️ STEP 3: ANALYZE FRONTEND API CALLS

### 3.1 Find All API Calls in Frontend

**What we're doing:** Extract every API call from frontend code

**Script:**
```bash
#!/bin/bash
# scripts/phase0_analyze_frontend.sh

cd /home/abcdeveloper/projects/analyticbot

echo "=============================================="
echo "🔍 PHASE 0: ANALYZING FRONTEND API CALLS"
echo "=============================================="

# Create reports directory
mkdir -p reports

echo ""
echo "📂 Scanning frontend files..."

# Find all files that might contain API calls
find apps/frontend/src -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -exec grep -l "fetch\|axios\|api\." {} \; > reports/files_with_api_calls.txt

FILES_COUNT=$(wc -l < reports/files_with_api_calls.txt)
echo "✅ Found $FILES_COUNT files with API calls"

echo ""
echo "🔎 Extracting API endpoint patterns..."

# Extract all API endpoint patterns
{
  echo "=============================================="
  echo "FRONTEND API CALLS ANALYSIS"
  echo "=============================================="
  echo ""

  # Look for fetch calls
  echo "FETCH CALLS:"
  echo "----------------------------------------------"
  find apps/frontend/src -type f \( -name "*.ts" -o -name "*.tsx" \) \
    -exec grep -h "fetch(" {} \; | \
    grep -oE "fetch\(['\"\`][^'\"\`]+" | \
    sed "s/fetch(['\"\`]//" | \
    sort | uniq

  echo ""
  echo ""

  # Look for axios calls
  echo "AXIOS CALLS:"
  echo "----------------------------------------------"
  find apps/frontend/src -type f \( -name "*.ts" -o -name "*.tsx" \) \
    -exec grep -h "axios\." {} \; | \
    grep -oE "axios\.(get|post|put|delete|patch)\(['\"\`][^'\"\`]+" | \
    sed "s/axios\.(get|post|put|delete|patch)(['\"\`]/\U\1 /" | \
    sort | uniq

  echo ""
  echo ""

  # Look for API base URLs
  echo "API BASE URLS:"
  echo "----------------------------------------------"
  find apps/frontend/src -type f \( -name "*.ts" -o -name "*.tsx" \) \
    -exec grep -h "API_BASE\|API_URL\|baseURL\|VITE_API" {} \; | \
    grep -v "^//" | \
    head -20

} > reports/phase0_frontend_api_calls.txt

echo "✅ Report saved to reports/phase0_frontend_api_calls.txt"

echo ""
echo "🔍 Extracting unique endpoint paths..."

# Extract just the endpoint paths
grep -rh "fetch\|axios" apps/frontend/src | \
  grep -oE "['\"\`]/(api/)?[a-z-]+/[^'\"\`]*['\"\`]" | \
  tr -d "'\"" | \
  sort | uniq > reports/phase0_frontend_endpoints.txt

ENDPOINTS_COUNT=$(wc -l < reports/phase0_frontend_endpoints.txt)
echo "✅ Found $ENDPOINTS_COUNT unique endpoint patterns"
echo "✅ Saved to reports/phase0_frontend_endpoints.txt"

echo ""
echo "=============================================="
echo "✅ FRONTEND ANALYSIS COMPLETE"
echo "=============================================="
echo ""
echo "Generated files:"
echo "  - reports/files_with_api_calls.txt ($FILES_COUNT files)"
echo "  - reports/phase0_frontend_api_calls.txt"
echo "  - reports/phase0_frontend_endpoints.txt ($ENDPOINTS_COUNT endpoints)"
```

**Run it:**
```bash
cd /home/abcdeveloper/projects/analyticbot
chmod +x scripts/phase0_analyze_frontend.sh
./scripts/phase0_analyze_frontend.sh
```

---

## 🎯 STEP 4: CREATE ENDPOINT MIGRATION MAP

### 4.1 Map Current → Target Structure

**What we're doing:** Create exact mapping of old paths to new paths

**Script:**
```python
# scripts/phase0_create_migration_map.py
"""
Phase 0: Create detailed migration map
Maps every current endpoint to its target location
"""

import json
from pathlib import Path

print("=" * 100)
print("🗺️  PHASE 0: CREATING ENDPOINT MIGRATION MAP")
print("=" * 100)

# Load current structure
with open("reports/openapi_current.json") as f:
    spec = json.load(f)

# Define migration rules for Option A (Flat Resources)
migration_rules = {
    # Duplicates to remove (redirect to correct endpoint)
    '/payment': {'action': 'REDIRECT', 'target': '/payments', 'reason': 'Remove duplicate'},
    '/ai-chat': {'action': 'REDIRECT', 'target': '/ai', 'reason': 'Consolidate AI endpoints'},
    '/ai-insights': {'action': 'REDIRECT', 'target': '/ai', 'reason': 'Consolidate AI endpoints'},
    '/ai-services': {'action': 'REDIRECT', 'target': '/ai', 'reason': 'Consolidate AI endpoints'},
    '/content-protection': {'action': 'REDIRECT', 'target': '/content', 'reason': 'Consolidate content'},

    # Nested redundancy to flatten
    '/ml/ml': {'action': 'MOVE', 'target': '/ai/ml', 'reason': 'Flatten nested path'},
    '/trends/trends': {'action': 'MOVE', 'target': '/analytics/trends', 'reason': 'Flatten nested path'},
    '/competitive/competitive': {'action': 'MOVE', 'target': '/analytics/competitive', 'reason': 'Flatten nested path'},
    '/optimization/optimization': {'action': 'MOVE', 'target': '/analytics/optimization', 'reason': 'Flatten nested path'},
    '/strategy/strategy': {'action': 'MOVE', 'target': '/analytics/strategy', 'reason': 'Flatten nested path'},
    '/superadmin/superadmin': {'action': 'MOVE', 'target': '/admin/super', 'reason': 'Flatten nested path'},

    # Consolidate analytics
    '/statistics': {'action': 'MOVE', 'target': '/analytics/statistics', 'reason': 'Consolidate analytics'},
    '/insights': {'action': 'MOVE', 'target': '/analytics/insights', 'reason': 'Consolidate analytics'},
    '/trends': {'action': 'MOVE', 'target': '/analytics/trends', 'reason': 'Consolidate analytics'},
    '/competitive': {'action': 'MOVE', 'target': '/analytics/competitive', 'reason': 'Consolidate analytics'},
    '/optimization': {'action': 'MOVE', 'target': '/analytics/optimization', 'reason': 'Consolidate analytics'},
    '/strategy': {'action': 'MOVE', 'target': '/analytics/strategy', 'reason': 'Consolidate analytics'},

    # Consolidate admin
    '/superadmin': {'action': 'MOVE', 'target': '/admin/super', 'reason': 'Consolidate admin'},
    '/auth/admin': {'action': 'MOVE', 'target': '/admin/auth', 'reason': 'Consolidate admin'},

    # Consolidate AI/ML
    '/ml': {'action': 'MOVE', 'target': '/ai/ml', 'reason': 'Consolidate AI services'},

    # Remove /api prefix (already have subdomain)
    '/api/storage': {'action': 'MOVE', 'target': '/storage', 'reason': 'Remove /api prefix (using subdomain)'},
    '/api/user-mtproto': {'action': 'MOVE', 'target': '/user-sessions', 'reason': 'Remove /api prefix + rename'},
    '/api/user-bot': {'action': 'MOVE', 'target': '/user-bots', 'reason': 'Remove /api prefix'},
    '/api/admin': {'action': 'MOVE', 'target': '/admin/bots', 'reason': 'Consolidate admin'},
    '/api/channels': {'action': 'DEPRECATE', 'target': None, 'reason': 'Old endpoint, replaced by /channels'},
    '/api/posts': {'action': 'MOVE', 'target': '/posts', 'reason': 'Remove /api prefix'},

    # Keep as-is (already good)
    '/health': {'action': 'KEEP', 'target': '/health', 'reason': 'Standard practice - health at root'},
    '/channels': {'action': 'KEEP', 'target': '/channels', 'reason': 'New microservice - already good'},
    '/analytics': {'action': 'KEEP', 'target': '/analytics', 'reason': 'Already good structure'},
    '/auth': {'action': 'KEEP', 'target': '/auth', 'reason': 'Already good structure'},
    '/admin': {'action': 'KEEP', 'target': '/admin', 'reason': 'Already good structure'},
    '/ai': {'action': 'KEEP', 'target': '/ai', 'reason': 'Already good structure'},
    '/content': {'action': 'KEEP', 'target': '/content', 'reason': 'Already good structure'},
    '/webhook': {'action': 'KEEP', 'target': '/webhooks', 'reason': 'Minor rename for consistency'},
    '/payments': {'action': 'KEEP', 'target': '/payments', 'reason': 'Already good structure'},
    '/exports': {'action': 'KEEP', 'target': '/exports', 'reason': 'Already good structure'},
    '/share': {'action': 'KEEP', 'target': '/share', 'reason': 'Already good structure'},
    '/mobile': {'action': 'KEEP', 'target': '/mobile', 'reason': 'Already good structure'},
    '/demo': {'action': 'KEEP', 'target': '/demo', 'reason': 'Already good structure'},
}

# Create migration map
migration_map = []

for path, methods in spec['paths'].items():
    # Find which rule applies
    rule = None
    matched_prefix = None

    for prefix, prefix_rule in migration_rules.items():
        if path.startswith(prefix):
            # Use longest matching prefix
            if not matched_prefix or len(prefix) > len(matched_prefix):
                matched_prefix = prefix
                rule = prefix_rule

    # If no rule matched, mark as REVIEW
    if not rule:
        rule = {'action': 'REVIEW', 'target': path, 'reason': 'No migration rule defined'}

    # Create new path
    if rule['action'] in ['REDIRECT', 'MOVE']:
        new_path = path.replace(matched_prefix, rule['target'], 1) if matched_prefix else path
    elif rule['action'] == 'KEEP':
        new_path = path
    elif rule['action'] == 'DEPRECATE':
        new_path = None
    else:
        new_path = path

    for method in methods.keys():
        if method in ['get', 'post', 'put', 'delete', 'patch']:
            migration_map.append({
                'method': method.upper(),
                'current_path': path,
                'new_path': new_path,
                'action': rule['action'],
                'reason': rule['reason'],
                'summary': methods[method].get('summary', 'No description'),
                'tags': methods[method].get('tags', ['untagged'])
            })

# Sort by action priority
action_priority = {'DEPRECATE': 1, 'REDIRECT': 2, 'MOVE': 3, 'KEEP': 4, 'REVIEW': 5}
migration_map.sort(key=lambda x: (action_priority.get(x['action'], 99), x['current_path']))

# Save migration map
with open("reports/phase0_migration_map.json", "w") as f:
    json.dump(migration_map, f, indent=2)

# Create human-readable report
with open("reports/phase0_migration_map.txt", "w") as report:
    report.write("=" * 120 + "\n")
    report.write("PHASE 0: ENDPOINT MIGRATION MAP (Option A - Flat Resources)\n")
    report.write("=" * 120 + "\n\n")

    # Group by action
    for action in ['DEPRECATE', 'REDIRECT', 'MOVE', 'KEEP', 'REVIEW']:
        endpoints = [e for e in migration_map if e['action'] == action]
        if not endpoints:
            continue

        report.write("\n" + "=" * 120 + "\n")
        report.write(f"{action} ({len(endpoints)} endpoints)\n")
        report.write("=" * 120 + "\n\n")

        for ep in endpoints:
            report.write(f"{ep['method']:6} {ep['current_path']}\n")
            if ep['new_path'] and ep['new_path'] != ep['current_path']:
                report.write(f"       → {ep['new_path']}\n")
            report.write(f"       Reason: {ep['reason']}\n")
            report.write(f"       Summary: {ep['summary']}\n")
            report.write("\n")

print(f"\n✅ Migration map created:")
print(f"   - JSON: reports/phase0_migration_map.json")
print(f"   - Report: reports/phase0_migration_map.txt")

# Print summary
print("\n" + "=" * 100)
print("📊 MIGRATION SUMMARY")
print("=" * 100)

for action in ['DEPRECATE', 'REDIRECT', 'MOVE', 'KEEP', 'REVIEW']:
    count = len([e for e in migration_map if e['action'] == action])
    if count > 0:
        print(f"{action:12} {count:3} endpoints")

print("\n✅ PHASE 0 STEP 4 COMPLETE")
```

**Run it:**
```bash
cd /home/abcdeveloper/projects/analyticbot
python3 scripts/phase0_create_migration_map.py
```

---

## 🛡️ STEP 5: SET UP SAFETY MECHANISMS

### 5.1 Create Git Backup

**What we're doing:** Create safety checkpoint before any changes

```bash
cd /home/abcdeveloper/projects/analyticbot

echo "🔒 Creating safety backup..."

# Create backup branch
git checkout -b backup-before-api-restructure-$(date +%Y%m%d)
git add .
git commit -m "Backup before API restructure - Phase 0 complete"
git push origin backup-before-api-restructure-$(date +%Y%m%d)

# Return to main and create feature branch
git checkout main
git checkout -b feature/api-restructure-phase1

echo "✅ Backup branches created:"
echo "   - backup-before-api-restructure-$(date +%Y%m%d)"
echo "   - feature/api-restructure-phase1 (current)"
```

### 5.2 Create Rollback Script

```bash
# scripts/rollback_api_restructure.sh
#!/bin/bash

echo "🔄 ROLLING BACK API RESTRUCTURE"
echo "================================"

BACKUP_BRANCH="backup-before-api-restructure-$(date +%Y%m%d)"

read -p "Are you sure you want to rollback? (yes/no): " CONFIRM

if [ "$CONFIRM" = "yes" ]; then
    git checkout main
    git reset --hard origin/$BACKUP_BRANCH
    echo "✅ Rolled back to $BACKUP_BRANCH"
    echo "⚠️  Restart the API server"
else
    echo "❌ Rollback cancelled"
fi
```

---

## 📋 PHASE 0 CHECKLIST

Track your progress:

- [ ] **Step 1: Analyze Current Structure**
  - [ ] Run `phase0_analyze_current_structure.py`
  - [ ] Review `reports/phase0_current_structure.txt`
  - [ ] Review `reports/phase0_issues.txt`

- [ ] **Step 2: Analyze Usage**
  - [ ] Run `phase0_analyze_usage.py`
  - [ ] Review `reports/phase0_endpoint_usage.txt`
  - [ ] Identify critical endpoints (top 20 most-used)

- [ ] **Step 3: Analyze Frontend**
  - [ ] Run `phase0_analyze_frontend.sh`
  - [ ] Review `reports/phase0_frontend_api_calls.txt`
  - [ ] Review `reports/phase0_frontend_endpoints.txt`

- [ ] **Step 4: Create Migration Map**
  - [ ] Run `phase0_create_migration_map.py`
  - [ ] Review `reports/phase0_migration_map.txt`
  - [ ] Verify all endpoints have migration plan

- [ ] **Step 5: Safety Setup**
  - [ ] Create backup branch
  - [ ] Create feature branch
  - [ ] Create rollback script
  - [ ] Verify backups

---

## 📊 EXPECTED DELIVERABLES

After Phase 0, you should have:

```
reports/
├── openapi_current.json                   # Current OpenAPI spec
├── current_routers.txt                    # Router registrations from main.py
├── phase0_current_structure.txt           # Detailed endpoint analysis
├── phase0_issues.txt                      # Detected issues
├── phase0_endpoint_usage.txt              # Usage statistics from logs
├── phase0_frontend_api_calls.txt          # Frontend API calls
├── phase0_frontend_endpoints.txt          # Frontend endpoint list
├── phase0_migration_map.json              # Migration map (JSON)
└── phase0_migration_map.txt               # Migration map (readable)
```

---

## 🚀 NEXT STEPS

After completing Phase 0:

1. **Review all reports** - Understand what we're changing
2. **Identify critical endpoints** - Mark must-not-break endpoints
3. **Discuss migration map** - Confirm the plan
4. **Move to Phase 1** - Start actual implementation

**Phase 1 will be:**
- Week 1: Remove duplicate endpoints (redirects only, no deletion)
- Safe, reversible changes
- One endpoint group at a time

---

## ❓ QUESTIONS TO ANSWER

Before moving to Phase 1:

- [ ] Are all top 20 most-used endpoints accounted for?
- [ ] Do we have external API consumers we need to notify?
- [ ] Is there a mobile app using these endpoints?
- [ ] What's our rollback plan if something breaks?
- [ ] Who will test each phase?
- [ ] When is the best time to deploy (low traffic period)?

---

**Phase 0 Status:** 📋 Ready to execute
**Risk Level:** ✅ LOW (read-only analysis)
**Time Required:** 2-3 hours
**Next Phase:** Phase 1 - Duplicate Removal (after review)
