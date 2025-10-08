"""
Demo Middleware
===============

Automatically detects demo users and enhances API responses with demo context.
Provides seamless demo experience while maintaining normal API structure.
"""

import json
import logging
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class DemoMiddleware(BaseHTTPMiddleware):
    """Middleware to handle demo user detection and response enhancement"""

    def __init__(self, app: Any):
        super().__init__(app)

        # Endpoints that should be enhanced with demo context
        self.demo_enhanced_endpoints = {
            "/api/initial-data",
            "/api/analytics/",
            "/api/channels/",
            "/api/posts/",
            "/api/ai-services/",
            "/api/admin/",
            "/demo/",  # All demo endpoints
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and enhance with demo context"""

        # Detect demo user context
        demo_context = await self._detect_demo_user(request)

        # Add demo context to request state
        request.state.is_demo = demo_context.get("is_demo", False)
        request.state.demo_type = demo_context.get("demo_type", None)
        request.state.demo_user_id = demo_context.get("user_id", None)

        # Process the request normally
        response = await call_next(request)

        # Enhance response with demo headers for frontend
        if demo_context.get("is_demo", False):
            response.headers["X-Demo-Active"] = "true"
            response.headers["X-Demo-Type"] = demo_context.get("demo_type", "standard")
            response.headers["X-Demo-User"] = str(demo_context.get("user_id", ""))

            # Add showcase quality indicator
            from apps.demo.config import demo_config

            response.headers["X-Demo-Quality"] = demo_config.get_demo_quality_level()

        return response

    async def _detect_demo_user(self, request: Request) -> dict:
        """Detect if request is from a demo user"""
        demo_context = {"is_demo": False, "demo_type": None, "user_id": None}

        # Method 1: Check Authorization header for demo token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            user_info = await self._extract_user_from_token(auth_header[7:])
            if user_info:
                demo_context.update(user_info)

        # Method 2: Check for demo user ID in request parameters
        user_id = request.path_params.get("user_id") or request.query_params.get("user_id")
        if user_id:
            from apps.demo.services.demo_service import is_demo_user_by_id

            if is_demo_user_by_id(user_id):
                demo_context.update({"is_demo": True, "user_id": user_id, "demo_type": "standard"})

        # Method 3: Check for demo email in login/auth requests
        if request.method == "POST" and any(
            path in str(request.url) for path in ["/auth/login", "/auth/register"]
        ):
            try:
                body = await self._peek_request_body(request)
                if body and "email" in body:
                    email = body["email"]
                    from apps.demo.config import demo_config

                    if demo_config.is_demo_email(email):
                        demo_type = self._get_demo_type_from_email(email)
                        demo_context.update(
                            {
                                "is_demo": True,
                                "demo_type": demo_type,
                                "user_id": f"demo_{email.split('@')[0]}",
                            }
                        )
            except Exception as e:
                logger.debug(f"Could not parse request body for demo detection: {e}")

        # Method 4: Check if accessing /demo/* endpoints
        if str(request.url.path).startswith("/demo/"):
            # All /demo/* endpoints are inherently demo requests
            demo_context.update(
                {"is_demo": True, "demo_type": "showcase", "user_id": "showcase_user"}
            )

        return demo_context

    async def _extract_user_from_token(self, token: str) -> dict | None:
        """Extract demo user information from token"""
        try:
            # Demo tokens have format: demo_<type>_<identifier>
            if token.startswith("demo_"):
                parts = token.split("_")
                if len(parts) >= 3:
                    demo_type = parts[1]
                    user_id = "_".join(parts[:3])

                    return {"is_demo": True, "demo_type": demo_type, "user_id": user_id}

            # For real JWT tokens, would decode and check user info
            # Placeholder for actual JWT verification
            return None

        except Exception as e:
            logger.debug(f"Could not extract user from token: {e}")
            return None

    def _get_demo_type_from_email(self, email: str) -> str:
        """Determine demo type based on email pattern"""
        email_lower = email.lower()

        if "showcase@" in email_lower or "demo@" in email_lower:
            return "full"  # Full feature demo
        elif "viewer@" in email_lower or "guest@" in email_lower:
            return "limited"  # Read-only demo
        elif "test@" in email_lower:
            return "testing"  # Testing demo with different data
        else:
            return "standard"  # Default demo experience

    async def _peek_request_body(self, request: Request) -> dict | None:
        """Peek at request body without consuming it"""
        try:
            body = await request.body()
            if body:
                # Reset the request body stream for the actual handler

                async def receive():
                    return {"type": "http.request", "body": body}

                request._receive = receive

                # Parse JSON body
                return json.loads(body.decode())
        except Exception as e:
            logger.debug(f"Could not peek request body: {e}")
            return None


# Maintain backward compatibility
DemoModeMiddleware = DemoMiddleware
