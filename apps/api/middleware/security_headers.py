"""
Security Headers Middleware

Adds security headers to HTTP responses to protect against common web vulnerabilities.

Headers added:
- Content-Security-Policy: Prevents XSS and data injection attacks
- X-Content-Type-Options: Prevents MIME type sniffing
- X-Frame-Options: Prevents clickjacking
- X-XSS-Protection: Legacy XSS protection
- Referrer-Policy: Controls referrer information
- Permissions-Policy: Controls browser features
"""

import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Content-Security-Policy
        # Note: This is a permissive policy for the API. Frontend should have stricter CSP.
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Needed for some frontend frameworks
            "style-src 'self' 'unsafe-inline'",  # Needed for inline styles
            "img-src 'self' data: https:",  # Allow images from HTTPS and data URIs
            "font-src 'self' https://fonts.gstatic.com",
            "connect-src 'self' https://api.analyticbot.org wss://api.analyticbot.org",
            "frame-ancestors 'self'",  # Prevent embedding in iframes
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # Legacy XSS protection (for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature-Policy)
        permissions = [
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)

        # Strict Transport Security (only add if served over HTTPS)
        # This tells browsers to always use HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response


# Convenience function to get admin-specific CSP (stricter)
def get_admin_csp() -> str:
    """
    Get Content-Security-Policy for admin panel.
    Stricter than general API policy.
    """
    directives = [
        "default-src 'self'",
        "script-src 'self'",  # No unsafe-inline for admin
        "style-src 'self' 'unsafe-inline'",  # MUI needs inline styles
        "img-src 'self' data: https:",
        "font-src 'self' https://fonts.gstatic.com",
        "connect-src 'self' https://api.analyticbot.org",
        "frame-ancestors 'none'",  # Prevent all embedding
        "base-uri 'self'",
        "form-action 'self'",
        "upgrade-insecure-requests",
    ]
    return "; ".join(directives)
