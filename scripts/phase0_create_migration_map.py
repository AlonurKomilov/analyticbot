"""
Phase 0: Create detailed migration map
Maps every current endpoint to its target location for Option A (Flat Resources)
"""

import json
from pathlib import Path

print("=" * 100)
print("🗺️  PHASE 0: CREATING ENDPOINT MIGRATION MAP")
print("=" * 100)

# Check if openapi_current.json exists
if not Path("reports/openapi_current.json").exists():
    print("❌ Error: reports/openapi_current.json not found")
    print("⚠️  Please run phase0_analyze_current_structure.py first")
    exit(1)

# Load current structure
with open("reports/openapi_current.json") as f:
    spec = json.load(f)

# Define migration rules for Option A (Flat Resources)
# No /api prefix needed (using subdomain api.analyticbot.org)
migration_rules = {
    # Duplicates to remove (redirect to correct endpoint)
    "/payment": {
        "action": "REDIRECT",
        "target": "/payments",
        "reason": "Remove duplicate - use /payments",
    },
    "/ai-chat": {
        "action": "REDIRECT",
        "target": "/ai",
        "reason": "Consolidate AI endpoints under /ai",
    },
    "/ai-insights": {
        "action": "REDIRECT",
        "target": "/ai",
        "reason": "Consolidate AI endpoints under /ai",
    },
    "/ai-services": {
        "action": "REDIRECT",
        "target": "/ai",
        "reason": "Consolidate AI endpoints under /ai",
    },
    "/content-protection": {
        "action": "REDIRECT",
        "target": "/content",
        "reason": "Consolidate content endpoints",
    },
    # Nested redundancy to flatten
    "/ml/ml": {
        "action": "MOVE",
        "target": "/ai/ml",
        "reason": "Flatten nested path + consolidate to AI",
    },
    "/trends/trends": {
        "action": "MOVE",
        "target": "/analytics/trends",
        "reason": "Flatten nested path",
    },
    "/competitive/competitive": {
        "action": "MOVE",
        "target": "/analytics/competitive",
        "reason": "Flatten nested path",
    },
    "/optimization/optimization": {
        "action": "MOVE",
        "target": "/analytics/optimization",
        "reason": "Flatten nested path",
    },
    "/strategy/strategy": {
        "action": "MOVE",
        "target": "/analytics/strategy",
        "reason": "Flatten nested path",
    },
    "/superadmin/superadmin": {
        "action": "MOVE",
        "target": "/admin/super",
        "reason": "Flatten nested path",
    },
    # Consolidate analytics under /analytics
    "/statistics": {
        "action": "MOVE",
        "target": "/analytics/statistics",
        "reason": "Consolidate analytics",
    },
    "/insights": {
        "action": "MOVE",
        "target": "/analytics/insights",
        "reason": "Consolidate analytics",
    },
    "/trends": {"action": "MOVE", "target": "/analytics/trends", "reason": "Consolidate analytics"},
    "/competitive": {
        "action": "MOVE",
        "target": "/analytics/competitive",
        "reason": "Consolidate analytics",
    },
    "/optimization": {
        "action": "MOVE",
        "target": "/analytics/optimization",
        "reason": "Consolidate analytics",
    },
    "/strategy": {
        "action": "MOVE",
        "target": "/analytics/strategy",
        "reason": "Consolidate analytics",
    },
    # Consolidate admin under /admin
    "/superadmin": {
        "action": "MOVE",
        "target": "/admin/super",
        "reason": "Consolidate admin operations",
    },
    "/auth/admin": {
        "action": "MOVE",
        "target": "/admin/auth",
        "reason": "Consolidate admin operations",
    },
    # Consolidate AI/ML under /ai
    "/ml": {"action": "MOVE", "target": "/ai/ml", "reason": "Consolidate AI services"},
    # Remove /api prefix (subdomain handles this)
    "/api/storage": {
        "action": "MOVE",
        "target": "/storage",
        "reason": "Remove /api prefix (subdomain routing)",
    },
    "/api/user-mtproto": {
        "action": "MOVE",
        "target": "/user-sessions",
        "reason": "Remove /api prefix + rename for clarity",
    },
    "/api/user-bot": {"action": "MOVE", "target": "/user-bots", "reason": "Remove /api prefix"},
    "/api/admin": {"action": "MOVE", "target": "/admin/bots", "reason": "Consolidate under /admin"},
    "/api/channels": {
        "action": "DEPRECATE",
        "target": None,
        "reason": "Old endpoint - replaced by /channels microservice",
    },
    "/api/posts": {"action": "MOVE", "target": "/posts", "reason": "Remove /api prefix"},
    # Rename for consistency
    "/webhook": {"action": "MOVE", "target": "/webhooks", "reason": "Plural for consistency"},
    # Keep as-is (already good)
    "/health": {
        "action": "KEEP",
        "target": "/health",
        "reason": "Health checks at root - standard practice",
    },
    "/channels": {
        "action": "KEEP",
        "target": "/channels",
        "reason": "New microservice - already follows Option A",
    },
    "/analytics": {
        "action": "KEEP",
        "target": "/analytics",
        "reason": "Already good - central analytics hub",
    },
    "/auth": {"action": "KEEP", "target": "/auth", "reason": "Already good structure"},
    "/admin": {
        "action": "KEEP",
        "target": "/admin",
        "reason": "Already good - will be central admin hub",
    },
    "/ai": {"action": "KEEP", "target": "/ai", "reason": "Already good - will be central AI hub"},
    "/content": {"action": "KEEP", "target": "/content", "reason": "Already good structure"},
    "/payments": {
        "action": "KEEP",
        "target": "/payments",
        "reason": "Already good structure (correct plural)",
    },
    "/exports": {"action": "KEEP", "target": "/exports", "reason": "Already good structure"},
    "/share": {"action": "KEEP", "target": "/share", "reason": "Already good structure"},
    "/mobile": {"action": "KEEP", "target": "/mobile", "reason": "Already good structure"},
    "/demo": {"action": "KEEP", "target": "/demo", "reason": "Already good structure"},
}

# Create migration map
migration_map = []

for path, methods in spec["paths"].items():
    # Find which rule applies (use longest matching prefix)
    rule = None
    matched_prefix = None

    for prefix, prefix_rule in migration_rules.items():
        if path.startswith(prefix):
            if not matched_prefix or len(prefix) > len(matched_prefix):
                matched_prefix = prefix
                rule = prefix_rule

    # If no rule matched, mark as REVIEW
    if not rule:
        rule = {
            "action": "REVIEW",
            "target": path,
            "reason": "No migration rule defined - needs review",
        }
        matched_prefix = path.split("/")[1] if len(path.split("/")) > 1 else "/"

    # Create new path
    if rule["action"] in ["REDIRECT", "MOVE"] and matched_prefix:
        new_path = path.replace(matched_prefix, rule["target"], 1)
    elif rule["action"] == "KEEP":
        new_path = path
    elif rule["action"] == "DEPRECATE":
        new_path = None
    else:
        new_path = path

    for method in methods.keys():
        if method in ["get", "post", "put", "delete", "patch"]:
            migration_map.append(
                {
                    "method": method.upper(),
                    "current_path": path,
                    "new_path": new_path,
                    "action": rule["action"],
                    "reason": rule["reason"],
                    "summary": methods[method].get("summary", "No description"),
                    "tags": methods[method].get("tags", ["untagged"]),
                    "priority": "HIGH"
                    if rule["action"] in ["DEPRECATE", "REDIRECT"]
                    else "MEDIUM"
                    if rule["action"] == "MOVE"
                    else "LOW",
                }
            )

# Sort by action priority
action_priority = {"DEPRECATE": 1, "REDIRECT": 2, "MOVE": 3, "KEEP": 4, "REVIEW": 5}
migration_map.sort(key=lambda x: (action_priority.get(x["action"], 99), x["current_path"]))

# Save migration map
with open("reports/phase0_migration_map.json", "w") as f:
    json.dump(migration_map, f, indent=2)

# Create human-readable report
with open("reports/phase0_migration_map.txt", "w") as report:
    report.write("=" * 120 + "\n")
    report.write("PHASE 0: ENDPOINT MIGRATION MAP (Option A - Flat Resources)\n")
    report.write("Target: https://api.analyticbot.org/{resource}/{action}\n")
    report.write("=" * 120 + "\n\n")

    # Group by action
    for action in ["DEPRECATE", "REDIRECT", "MOVE", "KEEP", "REVIEW"]:
        endpoints = [e for e in migration_map if e["action"] == action]
        if not endpoints:
            continue

        report.write("\n" + "=" * 120 + "\n")
        report.write(f"{action} - {len(endpoints)} endpoints\n")
        report.write("=" * 120 + "\n\n")

        for ep in endpoints:
            report.write(f"{ep['method']:6} {ep['current_path']}\n")
            if ep["new_path"] and ep["new_path"] != ep["current_path"]:
                report.write(f"       → NEW: {ep['new_path']}\n")
            elif ep["action"] == "DEPRECATE":
                report.write("       → WILL BE REMOVED\n")
            report.write(f"       Reason: {ep['reason']}\n")
            report.write(f"       Summary: {ep['summary']}\n")
            report.write(f"       Priority: {ep['priority']}\n")
            report.write("\n")

print("\n✅ Migration map created:")
print("   - JSON: reports/phase0_migration_map.json")
print("   - Report: reports/phase0_migration_map.txt")

# Print summary
print("\n" + "=" * 100)
print("📊 MIGRATION SUMMARY")
print("=" * 100)

for action in ["DEPRECATE", "REDIRECT", "MOVE", "KEEP", "REVIEW"]:
    endpoints = [e for e in migration_map if e["action"] == action]
    if endpoints:
        high_priority = len([e for e in endpoints if e.get("priority") == "HIGH"])
        print(f"{action:12} {len(endpoints):3} endpoints", end="")
        if high_priority > 0:
            print(f" ({high_priority} HIGH priority)", end="")
        print()

print("\n" + "=" * 100)
print("✅ PHASE 0 STEP 4 COMPLETE")
print("=" * 100)
print("\nNext: Review the migration map and proceed to Step 5 (Safety Setup)")
print("      Read: reports/phase0_migration_map.txt")
