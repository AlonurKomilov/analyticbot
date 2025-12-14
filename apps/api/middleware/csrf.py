"""
CSRF Protection Middleware

Provides CSRF (Cross-Site Request Forgery) protection for the admin panel.
Generates and validates CSRF tokens to prevent unauthorized state-changing requests.

Security Features:
- Double-submit cookie pattern
- Per-session token generation
- Constant-time token comparison
- Token rotation on sensitive operations
"""

import hashlib
import hmac
import logging
import os
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)

# CSRF Configuration
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", secrets.token_hex(32))
CSRF_TOKEN_LENGTH = 64
CSRF_TOKEN_LIFETIME_HOURS = 24
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_COOKIE_NAME = "csrf_token"

# Paths that don't require CSRF protection (read-only or auth endpoints)
CSRF_EXEMPT_PATHS = {
    "/auth/login",
    "/auth/telegram/login",
    "/auth/telegram/callback",
    "/auth/register",
    "/auth/csrf-token",
    "/auth/refresh",
    "/health",
    "/health/",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/webhook",  # Webhooks have their own validation
}

# Methods that don't require CSRF protection (safe methods)
CSRF_SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def generate_csrf_token() -> str:
    """
    Generate a cryptographically secure CSRF token.

    Returns:
        A hex-encoded random token
    """
    return secrets.token_hex(CSRF_TOKEN_LENGTH // 2)


def sign_csrf_token(token: str, timestamp: int) -> str:
    """
    Sign a CSRF token with timestamp for validation.

    Args:
        token: The raw CSRF token
        timestamp: Unix timestamp when token was created

    Returns:
        Signed token in format: token.timestamp.signature
    """
    message = f"{token}.{timestamp}"
    signature = hmac.new(CSRF_SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"{token}.{timestamp}.{signature}"


def verify_csrf_token(signed_token: str) -> tuple[bool, str]:
    """
    Verify a signed CSRF token.

    Args:
        signed_token: The signed token from client

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        parts = signed_token.split(".")
        if len(parts) != 3:
            return False, "Invalid token format"

        token, timestamp_str, signature = parts
        timestamp = int(timestamp_str)

        # Check if token has expired
        token_age = datetime.utcnow() - datetime.fromtimestamp(timestamp)
        if token_age > timedelta(hours=CSRF_TOKEN_LIFETIME_HOURS):
            return False, "Token expired"

        # Verify signature
        expected_message = f"{token}.{timestamp}"
        expected_signature = hmac.new(
            CSRF_SECRET_KEY.encode(), expected_message.encode(), hashlib.sha256
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(signature, expected_signature):
            return False, "Invalid signature"

        return True, ""

    except (ValueError, TypeError) as e:
        logger.warning(f"CSRF token verification error: {e}")
        return False, "Token verification failed"


def is_path_exempt(path: str) -> bool:
    """
    Check if a path is exempt from CSRF protection.

    Args:
        path: The request path

    Returns:
        True if path is exempt
    """
    # Exact match
    if path in CSRF_EXEMPT_PATHS:
        return True

    # Prefix match for certain paths
    exempt_prefixes = ["/docs", "/openapi", "/redoc", "/webhook/"]
    for prefix in exempt_prefixes:
        if path.startswith(prefix):
            return True

    return False


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware using double-submit cookie pattern.

    How it works:
    1. On first request, generate a CSRF token and set it in a cookie
    2. Client must include the token in X-CSRF-Token header for state-changing requests
    3. Middleware verifies the header token matches the cookie token
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and validate CSRF token for unsafe methods."""

        # Skip CSRF check for safe methods
        if request.method in CSRF_SAFE_METHODS:
            response = await call_next(request)
            # Ensure CSRF cookie is set even for GET requests
            return self._ensure_csrf_cookie(request, response)

        # Skip CSRF check for exempt paths
        if is_path_exempt(request.url.path):
            response = await call_next(request)
            return self._ensure_csrf_cookie(request, response)

        # Skip for non-browser requests (API-only, identified by no cookie)
        # This allows API clients with Bearer tokens to work without CSRF
        if not request.cookies.get(CSRF_COOKIE_NAME):
            # Check if this is an authenticated API request
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                # API request with Bearer token - skip CSRF
                # The admin panel uses cookies, so it will have CSRF cookie
                response = await call_next(request)
                return response

        # Validate CSRF token
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)

        if not cookie_token:
            logger.warning(f"CSRF: Missing cookie token for {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing. Please refresh the page.",
            )

        if not header_token:
            logger.warning(f"CSRF: Missing header token for {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token header missing. Please include X-CSRF-Token header.",
            )

        # Verify the cookie token is valid (signed correctly)
        is_valid, error_msg = verify_csrf_token(cookie_token)
        if not is_valid:
            logger.warning(f"CSRF: Cookie token invalid - {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"CSRF validation failed: {error_msg}",
            )

        # Verify header token matches cookie token (double-submit pattern)
        if not hmac.compare_digest(cookie_token, header_token):
            logger.warning(f"CSRF: Token mismatch for {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token mismatch. Please refresh the page.",
            )

        # CSRF validation passed
        response = await call_next(request)
        return response

    def _ensure_csrf_cookie(self, request: Request, response: Response) -> Response:
        """Ensure CSRF cookie is set in response."""

        # Check if cookie already exists and is valid
        existing_token = request.cookies.get(CSRF_COOKIE_NAME)
        if existing_token:
            is_valid, _ = verify_csrf_token(existing_token)
            if is_valid:
                return response

        # Generate new CSRF token
        raw_token = generate_csrf_token()
        timestamp = int(datetime.utcnow().timestamp())
        signed_token = sign_csrf_token(raw_token, timestamp)

        # Set cookie with security flags
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=signed_token,
            max_age=CSRF_TOKEN_LIFETIME_HOURS * 3600,
            httponly=False,  # Must be readable by JavaScript
            secure=True,  # Only send over HTTPS
            samesite="strict",  # Strict same-site policy
            path="/",
        )

        return response


# Utility function to get CSRF token for templates/API responses
def get_csrf_token_for_response() -> str:
    """
    Generate a new CSRF token for API response.

    Use this in the /auth/csrf-token endpoint.
    """
    raw_token = generate_csrf_token()
    timestamp = int(datetime.utcnow().timestamp())
    return sign_csrf_token(raw_token, timestamp)
