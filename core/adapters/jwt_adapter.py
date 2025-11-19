"""
🔑 JWT Token Adapter - Jose Implementation

Adapter implementing JWT operations using the jose library.
This keeps the jose dependency isolated from the core security engine.
"""

from datetime import datetime, timedelta

try:
    from jose import JWTError, jwt
except ImportError:
    # Graceful fallback if jose is not available
    jwt = None
    JWTError = Exception

from core.ports.security_ports import TokenClaims, TokenGeneratorPort


class JoseJWTAdapter(TokenGeneratorPort):
    """JWT adapter using jose library"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

        # Check if jose is available
        if jwt is None:
            raise ImportError("jose library is required for JWT operations")

    def generate_jwt_token(
        self, claims: TokenClaims, expires_delta: timedelta | None = None
    ) -> str:
        """Generate JWT token with claims"""
        if jwt is None:
            raise RuntimeError("JWT library not available")

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        # Convert datetime to Unix timestamp (int) for JWT standard compliance
        expire_timestamp = int(expire.timestamp())
        iat_timestamp = int(datetime.utcnow().timestamp())

        payload = {
            "sub": claims.user_id,
            "email": claims.email,
            "username": claims.username,
            "role": claims.role,
            "status": claims.status,
            "exp": expire_timestamp,  # Must be Unix timestamp (int)
            "iat": iat_timestamp,  # Must be Unix timestamp (int)
            "session_id": claims.session_id,
            "mfa_verified": claims.mfa_verified,
            "auth_provider": claims.auth_provider,
            "jti": claims.token_id,
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_jwt_token(self, token: str) -> TokenClaims:
        """Verify and decode JWT token"""
        if jwt is None:
            raise RuntimeError("JWT library not available")

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            return TokenClaims(
                user_id=payload.get("sub", ""),
                email=payload.get("email", ""),
                username=payload.get("username", ""),
                role=payload.get("role", ""),
                status=payload.get("status", ""),
                session_id=payload.get("session_id"),
                mfa_verified=payload.get("mfa_verified", False),
                auth_provider=payload.get("auth_provider", "local"),
                token_id=payload.get("jti"),
            )
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")

    def refresh_token(self, old_token: str, expires_delta: timedelta | None = None) -> str:
        """Refresh an existing token"""
        if jwt is None:
            raise RuntimeError("JWT library not available")

        try:
            # Verify old token (ignore expiration for refresh)
            payload = jwt.decode(
                old_token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},
            )

            # Create new claims from old token
            claims = TokenClaims(
                user_id=payload.get("sub", ""),
                email=payload.get("email", ""),
                username=payload.get("username", ""),
                role=payload.get("role", ""),
                status=payload.get("status", ""),
                session_id=payload.get("session_id"),
                mfa_verified=payload.get("mfa_verified", False),
                auth_provider=payload.get("auth_provider", "local"),
                token_id=payload.get("jti"),
            )

            return self.generate_jwt_token(claims, expires_delta)
        except JWTError as e:
            raise ValueError(f"Cannot refresh token: {str(e)}")

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token"""
        import secrets

        return secrets.token_urlsafe(length)
