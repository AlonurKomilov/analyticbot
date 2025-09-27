"""
Demo Mode Middleware
Automatically detects demo users and switches API responses to demo data
while maintaining the same API structure
"""

import json
import logging
from collections.abc import Callable
from typing import Any

from apps.api.__mocks__.auth.mock_users import (
    get_demo_user_type,
    is_demo_user,
    is_demo_user_by_id,
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class DemoModeMiddleware(BaseHTTPMiddleware):
    """Middleware to handle demo user detection and response switching"""

    def __init__(self, app: Any):
        super().__init__(app)

        # Endpoints that should use demo data for demo users
        self.demo_endpoints = {
            "/api/initial-data",
            "/api/analytics/",
            "/api/channels/",
            "/api/posts/",
            "/api/ai-services/",
            "/api/admin/",
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and potentially modify response for demo users"""

        # Check if this is a demo user request
        demo_context = await self._detect_demo_user(request)

        # Add demo context to request state
        request.state.is_demo = demo_context.get("is_demo", False)
        request.state.demo_type = demo_context.get("demo_type", None)
        request.state.demo_user_id = demo_context.get("user_id", None)

        # Process the request normally
        response = await call_next(request)

        # Add demo headers for frontend detection
        if demo_context.get("is_demo", False):
            response.headers["X-Demo-Mode"] = "true"
            response.headers["X-Demo-Type"] = demo_context.get("demo_type", "limited")
            response.headers["X-Demo-User"] = demo_context.get("user_id", "unknown")

        return response

    async def _detect_demo_user(self, request: Request) -> dict:
        """Detect if request is from a demo user"""
        demo_context = {"is_demo": False, "demo_type": None, "user_id": None}

        # Method 1: Check Authorization header for JWT token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            user_info = await self._extract_user_from_token(auth_header[7:])
            if user_info:
                demo_context.update(user_info)

        # Method 2: Check for demo user ID in request
        user_id = request.path_params.get("user_id") or request.query_params.get("user_id")
        if user_id and is_demo_user_by_id(user_id):
            demo_context.update(
                {"is_demo": True, "user_id": user_id, "demo_type": "limited"}  # Default
            )

        # Method 3: Check for demo email in login request body
        if request.method == "POST" and "/auth/login" in str(request.url):
            try:
                body = await self._peek_request_body(request)
                if body and "email" in body:
                    email = body["email"]
                    if is_demo_user(email):
                        demo_type = get_demo_user_type(email)
                        demo_context.update(
                            {
                                "is_demo": True,
                                "demo_type": demo_type,
                                "user_id": f"demo_user_{demo_type}",
                            }
                        )
            except Exception as e:
                logger.debug(f"Could not parse request body for demo detection: {e}")

        return demo_context

    async def _extract_user_from_token(self, token: str) -> dict | None:
        """Extract user information from JWT token"""
        try:
            # In a real implementation, you would decode and verify the JWT
            # For demo purposes, we'll check if it's a demo user token

            # Demo tokens have a specific format: demo_<type>_<id>
            if token.startswith("demo_"):
                parts = token.split("_")
                if len(parts) >= 3:
                    demo_type = parts[1]
                    user_id = "_".join(parts[:3])  # demo_type_id

                    return {"is_demo": True, "demo_type": demo_type, "user_id": user_id}

            # Check if it's a real JWT token but for a demo user
            # This would require actual JWT decoding in production
            return None

        except Exception as e:
            logger.debug(f"Could not extract user from token: {e}")
            return None

    async def _peek_request_body(self, request: Request) -> dict | None:
        """Peek at request body without consuming it"""
        try:
            body = await request.body()
            if body:
                # Reset the request body stream for the actual handler
                pass

                async def receive():
                    return {"type": "http.request", "body": body}

                request._receive = receive

                # Try to parse JSON
                return json.loads(body.decode())
        except Exception:
            return None


# Convenience functions moved to deps_factory.py to avoid circular imports
# and provide proper Request-based demo detection
# Import from apps.api.deps_factory if needed in other modules
