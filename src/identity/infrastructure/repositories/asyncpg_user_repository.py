"""
AsyncPG User Repository Implementation
"""

import asyncpg

from src.identity.domain.entities.user import AuthProvider, User, UserRole, UserStatus
from src.identity.domain.repositories.user_repository import UserRepository
from src.shared_kernel.domain.value_objects import EmailAddress, UserId, Username


class AsyncpgUserRepository(UserRepository):
    """
    User repository implementation using AsyncPG for PostgreSQL.

    This adapter translates between our domain model and the database schema.
    """

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def get_by_id(self, user_id: UserId) -> User | None:
        """Get user by ID"""
        query = """
            SELECT id, email, username, full_name, hashed_password, auth_provider, provider_id,
                   role, status, is_mfa_enabled, mfa_secret, failed_login_attempts, 
                   locked_until, last_login, last_password_change, email_verified_at,
                   password_reset_token, email_verification_token, avatar_url, 
                   timezone, language, created_at, updated_at
            FROM users WHERE id = $1
        """
        row = await self._pool.fetchrow(query, user_id.value)
        return self._map_row_to_user(row) if row else None

    async def get_by_email(self, email: EmailAddress) -> User | None:
        """Find user by email address"""
        query = """
            SELECT id, email, username, full_name, hashed_password, auth_provider, provider_id,
                   role, status, is_mfa_enabled, mfa_secret, failed_login_attempts, 
                   locked_until, last_login, last_password_change, email_verified_at,
                   password_reset_token, email_verification_token, avatar_url, 
                   timezone, language, created_at, updated_at
            FROM users WHERE email = $1
        """
        row = await self._pool.fetchrow(query, str(email))
        return self._map_row_to_user(row) if row else None

    async def get_by_username(self, username: Username) -> User | None:
        """Find user by username"""
        query = """
            SELECT id, email, username, full_name, hashed_password, auth_provider, provider_id,
                   role, status, is_mfa_enabled, mfa_secret, failed_login_attempts, 
                   locked_until, last_login, last_password_change, email_verified_at,
                   password_reset_token, email_verification_token, avatar_url, 
                   timezone, language, created_at, updated_at
            FROM users WHERE username = $1
        """
        row = await self._pool.fetchrow(query, str(username))
        return self._map_row_to_user(row) if row else None

    async def get_by_provider_id(self, provider: str, provider_id: str) -> User | None:
        """Find user by external provider ID"""
        query = """
            SELECT id, email, username, full_name, hashed_password, auth_provider, provider_id,
                   role, status, is_mfa_enabled, mfa_secret, failed_login_attempts, 
                   locked_until, last_login, last_password_change, email_verified_at,
                   password_reset_token, email_verification_token, avatar_url, 
                   timezone, language, created_at, updated_at
            FROM users WHERE auth_provider = $1 AND provider_id = $2
        """
        row = await self._pool.fetchrow(query, provider, provider_id)
        return self._map_row_to_user(row) if row else None

    async def email_exists(self, email: EmailAddress) -> bool:
        """Check if email is already registered"""
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)"
        return await self._pool.fetchval(query, str(email))

    async def username_exists(self, username: Username) -> bool:
        """Check if username is already taken"""
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE username = $1)"
        return await self._pool.fetchval(query, str(username))

    async def get_by_verification_token(self, token: str) -> User | None:
        """Find user by email verification token"""
        query = """
            SELECT id, email, username, full_name, hashed_password, auth_provider, provider_id,
                   role, status, is_mfa_enabled, mfa_secret, failed_login_attempts, 
                   locked_until, last_login, last_password_change, email_verified_at,
                   password_reset_token, email_verification_token, avatar_url, 
                   timezone, language, created_at, updated_at
            FROM users WHERE email_verification_token = $1
        """
        row = await self._pool.fetchrow(query, token)
        return self._map_row_to_user(row) if row else None

    async def get_by_reset_token(self, token: str) -> User | None:
        """Find user by password reset token"""
        query = """
            SELECT id, email, username, full_name, hashed_password, auth_provider, provider_id,
                   role, status, is_mfa_enabled, mfa_secret, failed_login_attempts, 
                   locked_until, last_login, last_password_change, email_verified_at,
                   password_reset_token, email_verification_token, avatar_url, 
                   timezone, language, created_at, updated_at
            FROM users WHERE password_reset_token = $1
        """
        row = await self._pool.fetchrow(query, token)
        return self._map_row_to_user(row) if row else None

    async def save(self, user: User) -> User:
        """Save user (create or update)"""
        # Check if user exists
        existing = await self.exists(user.id)

        if existing:
            return await self._update_user(user)
        else:
            return await self._create_user(user)

    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID"""
        query = "DELETE FROM users WHERE id = $1"
        result = await self._pool.execute(query, user_id.value)
        return result == "DELETE 1"

    async def exists(self, user_id: UserId) -> bool:
        """Check if user exists"""
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)"
        return await self._pool.fetchval(query, user_id.value)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """Get all users with pagination"""
        query = """
            SELECT id, email, username, full_name, hashed_password, auth_provider, provider_id,
                   role, status, is_mfa_enabled, mfa_secret, failed_login_attempts, 
                   locked_until, last_login, last_password_change, email_verified_at,
                   password_reset_token, email_verification_token, avatar_url, 
                   timezone, language, created_at, updated_at
            FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2
        """
        rows = await self._pool.fetch(query, limit, offset)
        return [self._map_row_to_user(row) for row in rows]

    async def get_active_users(self, limit: int = 100, offset: int = 0) -> list[User]:
        """Get active users with pagination"""
        query = """
            SELECT id, email, username, full_name, hashed_password, auth_provider, provider_id,
                   role, status, is_mfa_enabled, mfa_secret, failed_login_attempts, 
                   locked_until, last_login, last_password_change, email_verified_at,
                   password_reset_token, email_verification_token, avatar_url, 
                   timezone, language, created_at, updated_at
            FROM users WHERE status = $1 ORDER BY last_login DESC LIMIT $2 OFFSET $3
        """
        rows = await self._pool.fetch(query, UserStatus.ACTIVE.value, limit, offset)
        return [self._map_row_to_user(row) for row in rows]

    async def _create_user(self, user: User) -> User:
        """Create new user in database"""
        query = """
            INSERT INTO users (
                id, email, username, full_name, hashed_password, auth_provider, provider_id,
                role, status, is_mfa_enabled, mfa_secret, failed_login_attempts,
                locked_until, last_login, last_password_change, email_verified_at,
                password_reset_token, email_verification_token, avatar_url,
                timezone, language, created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, 
                $16, $17, $18, $19, $20, $21, $22, $23
            ) RETURNING id
        """

        await self._pool.fetchval(
            query,
            user.id.value,
            str(user.email),
            str(user.username),
            user.full_name,
            user.hashed_password,
            user.auth_provider.value,
            user.provider_id,
            user.role.value,
            user.status.value,
            user.is_mfa_enabled,
            user.mfa_secret,
            user.failed_login_attempts,
            user.locked_until,
            user.last_login,
            user.last_password_change,
            user.email_verified_at,
            user.password_reset_token,
            user.email_verification_token,
            user.avatar_url,
            user.timezone,
            user.language,
            user.created_at,
            user.updated_at,
        )

        return user

    async def _update_user(self, user: User) -> User:
        """Update existing user in database"""
        query = """
            UPDATE users SET
                email = $2, username = $3, full_name = $4, hashed_password = $5,
                auth_provider = $6, provider_id = $7, role = $8, status = $9,
                is_mfa_enabled = $10, mfa_secret = $11, failed_login_attempts = $12,
                locked_until = $13, last_login = $14, last_password_change = $15,
                email_verified_at = $16, password_reset_token = $17, 
                email_verification_token = $18, avatar_url = $19, timezone = $20,
                language = $21, updated_at = $22, version = version + 1
            WHERE id = $1
        """

        await self._pool.execute(
            query,
            user.id.value,
            str(user.email),
            str(user.username),
            user.full_name,
            user.hashed_password,
            user.auth_provider.value,
            user.provider_id,
            user.role.value,
            user.status.value,
            user.is_mfa_enabled,
            user.mfa_secret,
            user.failed_login_attempts,
            user.locked_until,
            user.last_login,
            user.last_password_change,
            user.email_verified_at,
            user.password_reset_token,
            user.email_verification_token,
            user.avatar_url,
            user.timezone,
            user.language,
            user.updated_at,
        )

        user.increment_version()
        return user

    def _map_row_to_user(self, row) -> User:
        """Map database row to User domain entity"""
        return User(
            id=UserId(row["id"]),
            email=EmailAddress(row["email"]),
            username=Username(row["username"]),
            full_name=row["full_name"],
            hashed_password=row["hashed_password"],
            auth_provider=AuthProvider(row["auth_provider"]),
            provider_id=row["provider_id"],
            role=UserRole(row["role"]),
            status=UserStatus(row["status"]),
            is_mfa_enabled=row["is_mfa_enabled"],
            mfa_secret=row["mfa_secret"],
            failed_login_attempts=row["failed_login_attempts"],
            locked_until=row["locked_until"],
            last_login=row["last_login"],
            last_password_change=row["last_password_change"],
            email_verified_at=row["email_verified_at"],
            password_reset_token=row["password_reset_token"],
            email_verification_token=row["email_verification_token"],
            avatar_url=row["avatar_url"],
            timezone=row["timezone"] or "UTC",
            language=row["language"] or "en",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
