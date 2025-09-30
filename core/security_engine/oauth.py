"""
🔒 OAuth 2.0 Integration - Google & GitHub Authentication

Enterprise-grade OAuth 2.0 implementation with support for multiple providers.
Handles the complete OAuth flow with security best practices.
"""

import logging
import secrets
from typing import Any, Optional
from urllib.parse import urlencode

from core.ports.security_ports import HttpClientPort, SecurityEventsPort
from .config import SecurityConfig, get_security_config
from .models import AuthProvider, User, UserStatus

logger = logging.getLogger(__name__)


class OAuthError(Exception):
    """OAuth-specific error without FastAPI coupling"""
    def __init__(self, message: str, status_code: int = 400, error_code: str | None = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class OAuthManager:
    """
    🔐 OAuth 2.0 Manager

    Handles OAuth authentication with multiple providers:
    - Google OAuth 2.0
    - GitHub OAuth 2.0
    - State validation for CSRF protection
    - User creation from OAuth profiles
    """

    def __init__(
        self,
        http_client: Optional[HttpClientPort] = None,
        security_events: Optional[SecurityEventsPort] = None
    ):
        self.config = get_security_config()
        self.http_client = http_client
        self.security_events = security_events
        
        # No fallback HTTP client - apps layer must provide one
        # This enforces proper dependency injection

        # OAuth provider configurations
        self.providers = {
            "google": {
                "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "client_id": self.config.GOOGLE_CLIENT_ID,
                "client_secret": self.config.GOOGLE_CLIENT_SECRET,
                "scope": "openid email profile",
            },
            "github": {
                "authorize_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "user_info_url": "https://api.github.com/user",
                "client_id": self.config.GITHUB_CLIENT_ID,
                "client_secret": self.config.GITHUB_CLIENT_SECRET,
                "scope": "user:email",
            },
        }
    
    async def _make_http_request(self, method: str, url: str, **kwargs) -> dict:
        """Make HTTP request using injected HTTP client port"""
        if not self.http_client:
            raise OAuthError("HTTP client not configured - must be provided via dependency injection")
        
        try:
            # Use the injected HTTP client port
            if method.upper() == 'POST':
                return await self.http_client.post(url, **kwargs)
            else:
                return await self.http_client.get(url, **kwargs)
        except Exception as e:
            # Generic HTTP error handling - let apps layer map specific exceptions
            raise OAuthError(f"HTTP request failed: {str(e)}")

        # OAuth provider configurations
        self.providers = {
            "google": {
                "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "client_id": self.config.GOOGLE_CLIENT_ID,
                "client_secret": self.config.GOOGLE_CLIENT_SECRET,
                "scope": "openid email profile",
            },
            "github": {
                "authorize_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "user_info_url": "https://api.github.com/user",
                "client_id": self.config.GITHUB_CLIENT_ID,
                "client_secret": self.config.GITHUB_CLIENT_SECRET,
                "scope": "user:email",
            },
        }

    def get_authorization_url(self, provider: str, redirect_uri: str) -> tuple[str, str]:
        """
        Generate OAuth authorization URL with state parameter

        Args:
            provider: OAuth provider (google, github)
            redirect_uri: Callback redirect URI

        Returns:
            Tuple of (authorization_url, state)

        Raises:
            OAuthError: If provider not supported
        """
        if provider not in self.providers:
            raise OAuthError(f"Unsupported OAuth provider: {provider}", 400)

        provider_config = self.providers[provider]

        # Generate secure state parameter for CSRF protection
        state = secrets.token_urlsafe(32)

        # Build authorization parameters
        params = {
            "client_id": provider_config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": provider_config["scope"],
            "response_type": "code",
            "state": state,
            "access_type": "offline" if provider == "google" else None,
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        # Build authorization URL
        auth_url = f"{provider_config['authorize_url']}?{urlencode(params)}"

        # Log authorization request
        if self.security_events:
            self.security_events.log_security_event(
                user_id=None,
                event_type="oauth_authorization_requested",
                details={
                    "provider": provider,
                    "state": state[:8] + "...",  # Log partial state for security
                }
            )

        logger.info(f"Generated OAuth authorization URL for {provider}")
        return auth_url, state

    async def exchange_code_for_token(
        self, provider: str, code: str, redirect_uri: str
    ) -> dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            provider: OAuth provider
            code: Authorization code from OAuth callback
            redirect_uri: Callback redirect URI

        Returns:
            Token response dictionary

        Raises:
            OAuthError: If token exchange fails
        """
        if provider not in self.providers:
            raise OAuthError(f"Unsupported OAuth provider: {provider}")

        provider_config = self.providers[provider]

        # Token exchange parameters
        data = {
            "client_id": provider_config["client_id"],
            "client_secret": provider_config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            token_data = await self._make_http_request(
                "post",
                provider_config["token_url"], 
                data=data, 
                headers=headers
            )

            if "error" in token_data:
                raise OAuthError(
                    f"OAuth token exchange failed: {token_data.get('error_description', 'Unknown error')}",
                    400
                )

            # Log successful token exchange
            if self.security_events:
                self.security_events.log_security_event(
                    user_id=None,
                    event_type="oauth_token_exchanged",
                    details={
                        "provider": provider,
                        "token_type": token_data.get("token_type", "bearer")
                    }
                )

            logger.info(f"Successfully exchanged code for token with {provider}")
            return token_data

        except Exception as e:
            logger.error(f"OAuth token exchange failed: {e}")
            if isinstance(e, OAuthError):
                raise
            raise OAuthError("Token exchange failed", 400)

    async def get_user_info(self, provider: str, access_token: str) -> dict[str, Any]:
        """
        Get user information from OAuth provider

        Args:
            provider: OAuth provider
            access_token: Access token from token exchange

        Returns:
            User information dictionary

        Raises:
            OAuthError: If user info request fails
        """
        if provider not in self.providers:
            raise OAuthError(f"Unsupported OAuth provider: {provider}", 400)

        provider_config = self.providers[provider]

        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

        try:
            user_info = await self._make_http_request(
                "get",
                provider_config["user_info_url"], 
                headers=headers
            )

            # Handle GitHub email separately (might be private)
            if provider == "github" and not user_info.get("email"):
                user_info["email"] = await self._get_github_email(access_token)

            # Log user info request
            if self.security_events:
                self.security_events.log_security_event(
                    user_id=None,
                    event_type="oauth_user_info_requested",
                    details={
                        "provider": provider,
                        "has_email": 'email' in user_info
                    }
                )

            logger.info(f"Retrieved user info from {provider}")
            return user_info

        except Exception as e:
            logger.error(f"Failed to get user info from {provider}: {e}")
            if isinstance(e, OAuthError):
                raise
            raise OAuthError("Failed to retrieve user information", 400)

    async def _get_github_email(self, access_token: str) -> str | None:
        """Get primary email from GitHub API"""
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

        try:
            emails = await self._make_http_request(
                "get",
                "https://api.github.com/user/emails", 
                headers=headers
            )

            # Find primary email
            for email_info in emails:
                if email_info.get("primary") and email_info.get("verified"):
                    return email_info["email"]

            # Fallback to first verified email
            for email_info in emails:
                if email_info.get("verified"):
                    return email_info["email"]

            return None

        except Exception:
            # Generic HTTP error - let apps layer handle specific exceptions
            return None

    def create_user_from_oauth(self, provider: str, user_info: dict[str, Any]) -> User:
        """
        Create User object from OAuth user information

        Args:
            provider: OAuth provider
            user_info: User information from OAuth provider

        Returns:
            User object

        Raises:
            OAuthError: If required user info is missing
        """
        # Extract email (required)
        email = user_info.get("email")
        if not email:
            raise OAuthError("Email is required but not provided by OAuth provider")

        # Extract user information based on provider
        if provider == "google":
            email = user_info.get("email")
            username = email.split("@")[0] if email else "unknown"  # Use email prefix as username
            full_name = user_info.get("name")
            avatar_url = user_info.get("picture")
            provider_id = user_info.get("id")

        elif provider == "github":
            username = user_info.get("login")
            full_name = user_info.get("name")
            avatar_url = user_info.get("avatar_url")
            provider_id = str(user_info.get("id"))

        else:
            username = email.split("@")[0]
            full_name = None
            avatar_url = None
            provider_id = None

        # Ensure username is unique by appending provider
        username = (
            f"{username}_{provider}" if username else f"user_{provider}_{secrets.token_hex(4)}"
        )

        # Create user object  
        user = User(
            email=email or f"noemail_{secrets.token_hex(8)}@{provider}.com",
            username=username,
            full_name=full_name,
            auth_provider=AuthProvider(provider),
            provider_id=provider_id,
            avatar_url=avatar_url,
            status=UserStatus.ACTIVE,  # OAuth users are pre-verified
            email_verified_at=None,  # Will be set when we verify OAuth email
        )

        logger.info(f"Created user from OAuth {provider}: {username}")
        return user

    async def complete_oauth_flow(
        self, provider: str, code: str, state: str, expected_state: str, redirect_uri: str
    ) -> User:
        """
        Complete full OAuth authentication flow

        Args:
            provider: OAuth provider
            code: Authorization code
            state: State parameter from callback
            expected_state: Expected state parameter
            redirect_uri: Callback redirect URI

        Returns:
            User object

        Raises:
            OAuthError: If OAuth flow fails or state mismatch
        """
        # Validate state parameter (CSRF protection)
        if state != expected_state:
            logger.warning(f"OAuth state mismatch for {provider}")
            raise OAuthError("Invalid state parameter")

        # Exchange code for token
        token_data = await self.exchange_code_for_token(provider, code, redirect_uri)
        access_token = token_data.get("access_token")

        if not access_token:
            raise OAuthError("No access token received")

        # Get user information
        user_info = await self.get_user_info(provider, access_token)

        # Create user object
        user = self.create_user_from_oauth(provider, user_info)

        logger.info(f"Completed OAuth flow for {provider}: {user.username}")
        return user

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # No cleanup needed - HTTP client is managed by apps layer
        pass


# Global OAuth manager instance
# Global OAuth manager instance - lazy initialization
_oauth_manager = None

def get_oauth_manager() -> OAuthManager:
    """Get the global OAuth manager instance"""
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = OAuthManager()
    return _oauth_manager
