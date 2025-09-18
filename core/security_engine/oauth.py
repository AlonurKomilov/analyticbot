"""
🔒 OAuth 2.0 Integration - Google & GitHub Authentication

Enterprise-grade OAuth 2.0 implementation with support for multiple providers.
Handles the complete OAuth flow with security best practices.
"""

import logging
import secrets
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from .config import SecurityConfig, get_security_config
from .models import AuthProvider, User, UserStatus

logger = logging.getLogger(__name__)


class OAuthManager:
    """
    🔐 OAuth 2.0 Manager

    Handles OAuth authentication with multiple providers:
    - Google OAuth 2.0
    - GitHub OAuth 2.0
    - State validation for CSRF protection
    - User creation from OAuth profiles
    """

    def __init__(self):
        self.config = get_security_config()
        self.client = httpx.AsyncClient()

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
            HTTPException: If provider not supported
        """
        if provider not in self.providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}",
            )

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
            HTTPException: If token exchange fails
        """
        if provider not in self.providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}",
            )

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
            response = await self.client.post(
                provider_config["token_url"], data=data, headers=headers
            )
            response.raise_for_status()

            token_data = response.json()

            if "error" in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"OAuth token exchange failed: {token_data.get('error_description', 'Unknown error')}",
                )

            logger.info(f"Successfully exchanged code for token with {provider}")
            return token_data

        except httpx.HTTPStatusError as e:
            logger.error(f"OAuth token exchange failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code for token",
            )

    async def get_user_info(self, provider: str, access_token: str) -> dict[str, Any]:
        """
        Get user information from OAuth provider

        Args:
            provider: OAuth provider
            access_token: Access token from token exchange

        Returns:
            User information dictionary

        Raises:
            HTTPException: If user info request fails
        """
        if provider not in self.providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}",
            )

        provider_config = self.providers[provider]

        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

        try:
            response = await self.client.get(provider_config["user_info_url"], headers=headers)
            response.raise_for_status()

            user_info = response.json()

            # Handle GitHub email separately (might be private)
            if provider == "github" and not user_info.get("email"):
                user_info["email"] = await self._get_github_email(access_token)

            logger.info(f"Retrieved user info from {provider}")
            return user_info

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get user info from {provider}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user information",
            )

    async def _get_github_email(self, access_token: str) -> str | None:
        """Get primary email from GitHub API"""
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

        try:
            response = await self.client.get("https://api.github.com/user/emails", headers=headers)
            response.raise_for_status()

            emails = response.json()

            # Find primary email
            for email_info in emails:
                if email_info.get("primary") and email_info.get("verified"):
                    return email_info["email"]

            # Fallback to first verified email
            for email_info in emails:
                if email_info.get("verified"):
                    return email_info["email"]

            return None

        except httpx.HTTPStatusError:
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
            HTTPException: If required user info is missing
        """
        # Extract email (required)
        email = user_info.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required but not provided by OAuth provider",
            )

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
            HTTPException: If OAuth flow fails or state mismatch
        """
        # Validate state parameter (CSRF protection)
        if state != expected_state:
            logger.warning(f"OAuth state mismatch for {provider}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter"
            )

        # Exchange code for token
        token_data = await self.exchange_code_for_token(provider, code, redirect_uri)
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No access token received"
            )

        # Get user information
        user_info = await self.get_user_info(provider, access_token)

        # Create user object
        user = self.create_user_from_oauth(provider, user_info)

        logger.info(f"Completed OAuth flow for {provider}: {user.username}")
        return user

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


# Global OAuth manager instance
# Global OAuth manager instance - lazy initialization
_oauth_manager = None

def get_oauth_manager() -> OAuthManager:
    """Get the global OAuth manager instance"""
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = OAuthManager()
    return _oauth_manager
