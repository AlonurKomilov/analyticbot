"""
Phase 0: Analyze which endpoints are actually used
Parse logs to understand traffic patterns
"""

import glob
import re
from collections import Counter

print("=" * 100)
print("📊 PHASE 0: ANALYZING API USAGE FROM LOGS")
print("=" * 100)

# Parse all log files
endpoint_usage = Counter()
method_usage = Counter()
error_endpoints = Counter()

log_files = glob.glob("logs/*.log")
print(f"\n🔍 Scanning {len(log_files)} log files...")

http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]

for log_file in log_files:
    try:
        with open(log_file, encoding="utf-8", errors="ignore") as f:
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
                            if re.search(r"\s[45]\d{2}\s", line):
                                error_endpoints[endpoint] += 1
    except Exception as e:
        print(f"⚠️  Error reading {log_file}: {e}")

print(f"✅ Analyzed {sum(endpoint_usage.values())} API requests")

# Save detailed usage report
print("\n" + "=" * 100)
print("🔥 TOP 50 MOST-USED ENDPOINTS")
print("=" * 100)

with open("docs/reports/phase0_endpoint_usage.txt", "w") as report:
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

print("\n✅ Report saved to reports/phase0_endpoint_usage.txt")

# Identify unused endpoints (need to compare with current structure)
print("\n" + "=" * 100)
print("📋 SUMMARY")
print("=" * 100)
print(f"Total API requests analyzed: {sum(endpoint_usage.values())}")
print(f"Unique endpoints used: {len(endpoint_usage)}")
print(f"Endpoints with errors: {len(error_endpoints)}")
print("\nNext: Run Step 3 to analyze frontend API calls")
print("      ./scripts/phase0_analyze_frontend.sh")
