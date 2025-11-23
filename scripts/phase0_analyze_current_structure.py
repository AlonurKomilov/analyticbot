"""
Phase 0: Analyze current API structure
Creates detailed reports of all endpoints
"""

import json
from collections import defaultdict
from pathlib import Path

import requests

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

for path, methods in spec["paths"].items():
    for method in methods.keys():
        if method in ["get", "post", "put", "delete", "patch"]:
            endpoint_info = {
                "method": method.upper(),
                "path": path,
                "summary": methods[method].get("summary", "No description"),
                "tags": methods[method].get("tags", ["untagged"]),
                "operationId": methods[method].get("operationId", "unknown"),
            }
            all_endpoints.append(endpoint_info)

            # Group by first-level prefix
            parts = path.strip("/").split("/")
            prefix = "/" + parts[0] if parts else "/"
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
    ("/payment", "/payments"),
    ("/ai", "/ai-chat"),
    ("/ai", "/ai-insights"),
    ("/ai", "/ai-services"),
    ("/content", "/content-protection"),
]

for old, new in duplicate_patterns:
    if old in prefix_groups and new in prefix_groups:
        issues.append(
            f"DUPLICATE: {old} ({len(prefix_groups[old])}) and {new} ({len(prefix_groups[new])})"
        )

# Check for nested redundancy
for prefix in prefix_groups.keys():
    parts = prefix.strip("/").split("/")
    if len(parts) > 1 and parts[0] == parts[1]:
        issues.append(f"NESTED REDUNDANCY: {prefix}")

# Check for inconsistent /api prefix
api_prefixes = [p for p in prefix_groups.keys() if p.startswith("/api/")]
non_api_prefixes = [p for p in prefix_groups.keys() if not p.startswith("/api/") and p != "/health"]

if api_prefixes and non_api_prefixes:
    issues.append(
        f"INCONSISTENT PREFIX: {len(api_prefixes)} with /api, {len(non_api_prefixes)} without"
    )

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
print("      python3 scripts/phase0_analyze_usage.py")
