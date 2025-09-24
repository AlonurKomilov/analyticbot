#!/usr/bin/env python3
"""
Backend API Endpoint Usage Audit - Final Report Generator
========================================================
Compares backend endpoints with frontend usage to generate comprehensive audit report
"""

import re
from typing import Set, List, Dict, Tuple

def load_backend_endpoints() -> Set[str]:
    """Load backend endpoints from previous scan"""
    backend_endpoints = {
        # Admin endpoints
        "DELETE /admin/channels/{channel_id}",
        "GET /admin/audit/recent",
        "GET /admin/channels",
        "GET /admin/stats/system",
        "GET /admin/users/{user_id}/channels",
        "POST /admin/channels/{channel_id}/suspend",
        "POST /admin/channels/{channel_id}/unsuspend",
        
        # AI Services endpoints
        "GET /ai/churn/stats",
        "GET /ai/content/stats",
        "GET /ai/security/stats",
        "GET /ai/stats",
        "POST /ai/churn/analyze",
        "POST /ai/content/analyze",
        "POST /ai/security/analyze",
        
        # Analytics Core endpoints
        "GET /analytics/core/channels/{channel_id}/growth",
        "GET /analytics/core/channels/{channel_id}/sources",
        "GET /analytics/core/channels/{channel_id}/top-posts",
        "GET /analytics/core/dashboard/{channel_id}",
        "GET /analytics/core/metrics/{channel_id}",
        "GET /analytics/core/overview/{channel_id}",
        "POST /analytics/core/refresh/{channel_id}",
        
        # Analytics Alerts endpoints
        "DELETE /analytics/alerts/rules/{channel_id}/{rule_id}",
        "GET /analytics/alerts/check/{channel_id}",
        "GET /analytics/alerts/history/{channel_id}",
        "GET /analytics/alerts/rules/{channel_id}",
        "GET /analytics/alerts/stats/{channel_id}",
        "POST /analytics/alerts/notifications/{channel_id}/test",
        "POST /analytics/alerts/rules/{channel_id}",
        "PUT /analytics/alerts/rules/{channel_id}/{rule_id}",
        
        # Analytics Demo endpoints
        "GET /analytics/demo/ai-recommendations",
        "GET /analytics/demo/best-time",
        "GET /analytics/demo/health",
        "GET /analytics/demo/post-dynamics",
        "GET /analytics/demo/top-posts",
        
        # Analytics Insights endpoints
        "GET /analytics/insights/capabilities",
        "GET /analytics/insights/channels/{channel_id}/trending",
        "GET /analytics/insights/comparison/{channel_id}",
        "GET /analytics/insights/reports/{channel_id}",
        "GET /analytics/insights/trends/posts/top",
        "POST /analytics/insights/channel-data",
        "POST /analytics/insights/metrics/performance",
        
        # Analytics Predictive endpoints
        "GET /analytics/predictive/insights/{channel_id}",
        "GET /analytics/predictive/summary/{channel_id}",
        "POST /analytics/predictive/data/analyze",
        "POST /analytics/predictive/predictions/forecast",
        
        # Analytics Realtime endpoints
        "GET /analytics/realtime/channels/{channel_id}/reach",
        "GET /analytics/realtime/live-metrics/{channel_id}",
        "GET /analytics/realtime/metrics/{channel_id}",
        "GET /analytics/realtime/monitor/{channel_id}",
        "GET /analytics/realtime/performance/{channel_id}",
        "GET /analytics/realtime/recommendations/{channel_id}",
        
        # Auth endpoints
        "GET /auth/me",
        "GET /auth/mfa/status",
        "POST /auth/login",
        "POST /auth/logout",
        "POST /auth/password/forgot",
        "POST /auth/password/reset",
        "POST /auth/refresh",
        "POST /auth/register",
        
        # Channel Management endpoints
        "DELETE /channels/{channel_id}",
        "GET /channels/{channel_id}",
        "GET /channels/{channel_id}/status",
        "POST /channels/{channel_id}/activate",
        "POST /channels/{channel_id}/deactivate",
        "PUT /channels/{channel_id}",
        
        # Clean Analytics endpoints (demo/educational)
        "GET /clean/analytics/channels/{channel_id}/audience",
        "GET /clean/analytics/channels/{channel_id}/best-times",
        "GET /clean/analytics/channels/{channel_id}/engagement",
        "GET /clean/analytics/channels/{channel_id}/metrics",
        "GET /clean/analytics/channels/{channel_id}/posts/{post_id}/performance",
        "GET /clean/analytics/demo/admin/stats",
        "GET /clean/analytics/demo/ai/suggestions",
        "GET /clean/analytics/demo/auth/permissions/{user_id}",
        "GET /clean/analytics/service-info",
        "GET /clean/analytics/status",
        
        # Content Protection endpoints
        "GET /content/files/{filename}",
        "GET /content/premium-features/{tier}",
        "GET /content/usage/{user_id}",
        "POST /content/custom-emoji",
        "POST /content/theft-detection",
        "POST /content/watermark/image",
        "POST /content/watermark/video",
        
        # Core System endpoints
        "GET /delivery/stats",
        "GET /initial-data",
        "GET /performance",
        "DELETE /schedule/{post_id}",
        "GET /schedule/user/{user_id}",
        "GET /schedule/{post_id}",
        "POST /schedule",
        
        # Exports endpoints
        "GET /exports/csv/growth/{channel_id}",
        "GET /exports/csv/overview/{channel_id}",
        "GET /exports/csv/reach/{channel_id}",
        "GET /exports/csv/sources/{channel_id}",
        "GET /exports/png/growth/{channel_id}",
        "GET /exports/png/reach/{channel_id}",
        "GET /exports/png/sources/{channel_id}",
        "GET /exports/status",
        
        # Health endpoints
        "GET /health/",
        "GET /health/debug",
        "GET /health/detailed",
        "GET /health/live",
        "GET /health/metrics",
        "GET /health/ready",
        "GET /health/trends",
        
        # Mobile API endpoints
        "GET /mobile/dashboard/{user_id}",
        "GET /mobile/metrics/summary/{channel_id}",
        "POST /mobile/analytics/quick",
        
        # Payment endpoints
        "DELETE /payments/subscriptions/{subscription_id}",
        "GET /payments/plans",
        "GET /payments/stats/payments",
        "GET /payments/stats/subscriptions",
        "GET /payments/status",
        "GET /payments/user/{user_id}/history",
        "GET /payments/user/{user_id}/subscription",
        "POST /payments/subscriptions",
        "POST /payments/webhook/stripe",
        
        # Share endpoints
        "DELETE /share/revoke/{share_token}",
        "GET /share/cleanup",
        "GET /share/info/{share_token}",
        "GET /share/report/{share_token}",
        "POST /share/create/{report_type}/{channel_id}",
        
        # SuperAdmin endpoints
        "GET /superadmin/audit-logs",
        "GET /superadmin/config",
        "GET /superadmin/stats",
        "GET /superadmin/users",
        "POST /superadmin/auth/login",
        "POST /superadmin/auth/logout",
        "POST /superadmin/users/{user_id}/reactivate",
        "POST /superadmin/users/{user_id}/suspend",
        "PUT /superadmin/config/{key}",
    }
    
    return backend_endpoints

def load_frontend_api_calls() -> Set[str]:
    """Load frontend API calls based on scan results"""
    frontend_calls = {
        # Core system calls
        "/initial-data",
        "/health",
        "/performance",
        "/schedule",
        "/schedule/{post_id}",
        "/schedule/user/{user_id}",
        "/delivery/stats",
        
        # Auth calls
        "/auth/login",
        "/auth/logout", 
        "/auth/register",
        "/auth/refresh",
        "/auth/me",
        "/auth/password/forgot",
        "/auth/password/reset",
        "/auth/mfa/setup",
        "/auth/mfa/verify-setup",
        "/auth/mfa/status",
        
        # Analytics calls (legacy v2 endpoints being used)
        "/analytics/v2/post-dynamics/{channel_id}",
        "/analytics/v2/top-posts/{channel_id}",
        "/analytics/v2/best-time/{channel_id}",
        "/analytics/v2/engagement-metrics/{channel_id}",
        "/analytics/overview/{channel_id}",
        "/analytics/channels/{channel_id}",
        "/analytics/growth/{channel_id}",
        "/analytics/reach/{channel_id}",
        "/analytics/post-dynamics/{channel_id}",
        "/analytics/best-time/{channel_id}",
        "/analytics/top-posts/{channel_id}",
        "/analytics/engagement/{channel_id}",
        "/analytics/insights/{channel_id}",
        "/analytics/predictions/{channel_id}",
        "/analytics/trends/{channel_id}",
        "/analytics/metrics/{channel_id}",
        "/analytics/quick",
        "/analytics/demo",
        "/analytics/demo/top-posts",
        "/analytics/advanced",
        "/analytics/web-vitals",
        
        # API v2 advanced analytics calls (many legacy)
        "/api/v2/analytics/channels/{channel_id}/overview",
        "/api/v2/analytics/channels/{channel_id}/growth",
        "/api/v2/analytics/channels/{channel_id}/reach",
        "/api/v2/analytics/channels/{channel_id}/top-posts",
        "/api/v2/analytics/channels/{channel_id}/trending",
        "/api/v2/analytics/channels/{channel_id}/performance",
        "/api/v2/analytics/channels/{channel_id}/best-times",
        "/api/v2/analytics/channels/{channel_id}/engagement",
        "/api/v2/analytics/channels/{channel_id}/post-dynamics",
        "/api/v2/analytics/channels/{channel_id}/alerts",
        "/api/v2/analytics/channels/{channel_id}/real-time",
        "/api/v2/analytics/channels/{channel_id}/export/{type}",
        "/api/v2/analytics/advanced/dashboard/{channel_id}",
        "/api/v2/analytics/advanced/metrics/real-time/{channel_id}",
        "/api/v2/analytics/advanced/performance/score/{channel_id}",
        "/api/v2/analytics/advanced/recommendations/{channel_id}",
        "/api/v2/analytics/advanced/alerts/check/{channel_id}",
        "/api/v2/analytics/metrics/performance",
        "/api/v2/analytics/channel-data",
        "/api/v2/analytics/trends/top-posts",
        
        # AI Services calls
        "/ai/security/analyze",
        "/ai/churn/predict",
        "/ai/churn/predictions",
        "/ai/churn/stats",
        "/ai/content/optimize",
        "/ai/content/stats",
        "/ai/security/stats",
        "/ai/predictive/insights",
        "/ai/predictive/forecasts",
        "/ai/predictive/stats",
        "/ai/recommendations/{channel_id}",
        
        # Channel management calls
        "/channels/{channel_id}",
        
        # Export calls
        "/api/v2/exports/csv/{type}/{channel_id}",
        "/api/v2/exports/png/{type}/{channel_id}",
        "/api/v2/exports/status",
        "/exports/csv",
        "/exports/png",
        "/exports/status",
        
        # Share calls
        "/api/v2/share/create/{type}/{channel_id}",
        "/api/v2/share/report/{token}",
        "/api/v2/share/info/{token}",
        "/api/v2/share/revoke/{token}",
        "/share/create",
        "/share/report",
        "/share/info",
        "/share/revoke",
        
        # Mobile API calls
        "/api/mobile/v1/analytics/quick",
        
        # Media/Upload calls
        "/api/v1/media/upload-direct",
        "/api/v1/media/storage-files",
        "/upload-media",
        
        # Admin calls
        "/api/analytics/admin/all-channels",
        "/api/analytics/admin/system-stats",
        "/admin/channels/{channel_id}",
        "/admin/system-stats",
        "/admin/all-channels",
        
        # SuperAdmin calls
        "/api/v1/superadmin/system-status",
        "/api/v1/superadmin/users",
        "/api/v1/superadmin/{user_id}",
        "/superadmin/system-status",
        "/superadmin/users",
        "/superadmin/{user_id}",
        
        # Content Protection calls
        "/api/v1/content-protection/detection/scan",
        "/content/optimize",
        
        # Payment calls
        "/payments/{payment_id}",
    }
    
    return frontend_calls

def normalize_endpoint(endpoint: str) -> str:
    """Normalize endpoint for comparison"""
    # Remove HTTP method prefix
    endpoint = re.sub(r'^(GET|POST|PUT|DELETE|PATCH)\s+', '', endpoint)
    
    # Normalize parameter patterns
    endpoint = re.sub(r'\{[^}]+\}', '{id}', endpoint)
    endpoint = re.sub(r'/[0-9]+', '/{id}', endpoint)
    endpoint = re.sub(r'\$\{[^}]+\}', '{id}', endpoint)
    
    # Clean up
    endpoint = re.sub(r'[?#].*', '', endpoint)
    if len(endpoint) > 1:
        endpoint = endpoint.rstrip('/')
    
    return endpoint

def compare_endpoints(backend_endpoints: Set[str], frontend_calls: Set[str]) -> Tuple[Set[str], Set[str], Set[str]]:
    """Compare backend and frontend endpoints"""
    
    # Normalize all endpoints
    normalized_backend = {normalize_endpoint(ep) for ep in backend_endpoints}
    normalized_frontend = {normalize_endpoint(call) for call in frontend_calls}
    
    # Find matches and unused endpoints
    used_endpoints = set()
    unused_endpoints = set()
    frontend_only = set()
    
    for backend_ep in normalized_backend:
        found_match = False
        for frontend_call in normalized_frontend:
            # Check if frontend call matches backend endpoint
            if backend_ep == frontend_call or backend_ep.endswith(frontend_call) or frontend_call.endswith(backend_ep.split('/')[-2:][0] if '/' in backend_ep else backend_ep):
                used_endpoints.add(backend_ep)
                found_match = True
                break
        
        if not found_match:
            unused_endpoints.add(backend_ep)
    
    # Find frontend calls that don't match any backend endpoint
    for frontend_call in normalized_frontend:
        found_match = False
        for backend_ep in normalized_backend:
            if backend_ep == frontend_call or backend_ep.endswith(frontend_call) or frontend_call.endswith(backend_ep.split('/')[-2:][0] if '/' in backend_ep else backend_ep):
                found_match = True
                break
        
        if not found_match:
            frontend_only.add(frontend_call)
    
    return used_endpoints, unused_endpoints, frontend_only

def generate_audit_report():
    """Generate comprehensive audit report"""
    
    print("🔍 Backend API Endpoint Usage Audit - Final Report")
    print("=" * 80)
    
    backend_endpoints = load_backend_endpoints()
    frontend_calls = load_frontend_api_calls()
    
    used_endpoints, unused_endpoints, frontend_only = compare_endpoints(backend_endpoints, frontend_calls)
    
    total_backend = len(backend_endpoints)
    total_used = len(used_endpoints)
    total_unused = len(unused_endpoints)
    usage_percentage = (total_used / total_backend) * 100 if total_backend > 0 else 0
    
    print(f"\n📊 EXECUTIVE SUMMARY")
    print(f"   Backend Endpoints: {total_backend}")
    print(f"   Used by Frontend: {total_used}")
    print(f"   Unused by Frontend: {total_unused}")
    print(f"   Usage Rate: {usage_percentage:.1f}%")
    print(f"   Frontend-only calls: {len(frontend_only)}")
    
    print(f"\n✅ SECTION A: USED API ENDPOINTS ({total_used} endpoints)")
    print("=" * 60)
    print("These backend endpoints are confirmed to be used by the frontend:")
    for endpoint in sorted(used_endpoints):
        print(f"   ✓ {endpoint}")
    
    print(f"\n❌ SECTION B: POTENTIALLY UNUSED API ENDPOINTS ({total_unused} endpoints)")
    print("=" * 60)
    print("These backend endpoints were NOT found in the frontend codebase:")
    print("⚠️  Note: Some may be used by external clients, admin tools, or webhooks")
    for endpoint in sorted(unused_endpoints):
        print(f"   • {endpoint}")
    
    print(f"\n🔍 SECTION C: FRONTEND-ONLY API CALLS ({len(frontend_only)} calls)")
    print("=" * 60)
    print("These API calls are made by frontend but don't match backend endpoints:")
    print("⚠️  Note: These may be legacy calls, mocked endpoints, or routing patterns")
    for call in sorted(frontend_only):
        print(f"   ? {call}")
    
    # Analysis by domain
    print(f"\n📈 DOMAIN ANALYSIS")
    print("=" * 40)
    
    domains = {
        'Analytics': ['analytics', 'metrics'],
        'Authentication': ['auth'],
        'Channels': ['channels'],
        'Admin': ['admin', 'superadmin'],
        'AI Services': ['ai'],
        'Exports': ['exports'],
        'Payments': ['payments'],
        'Content': ['content'],
        'Health': ['health'],
        'Mobile': ['mobile'],
        'Share': ['share']
    }
    
    for domain, keywords in domains.items():
        domain_backend = {ep for ep in backend_endpoints if any(kw in ep.lower() for kw in keywords)}
        domain_used = {ep for ep in used_endpoints if any(kw in ep.lower() for kw in keywords)}
        domain_unused = {ep for ep in unused_endpoints if any(kw in ep.lower() for kw in keywords)}
        
        if domain_backend:
            domain_usage = (len(domain_used) / len(domain_backend)) * 100
            print(f"   {domain:15} | Total: {len(domain_backend):2d} | Used: {len(domain_used):2d} | Unused: {len(domain_unused):2d} | Usage: {domain_usage:5.1f}%")
    
    print(f"\n🎯 RECOMMENDATIONS")
    print("=" * 40)
    print("1. Review unused endpoints for potential removal or deprecation")
    print("2. Update frontend to use new Clean 5-Router Analytics Architecture")
    print("3. Migrate legacy /api/v2/analytics/* calls to /analytics/core/*, /analytics/realtime/*, etc.")
    print("4. Verify external integrations before removing unused endpoints")
    print("5. Consider API versioning strategy for breaking changes")

if __name__ == "__main__":
    generate_audit_report()