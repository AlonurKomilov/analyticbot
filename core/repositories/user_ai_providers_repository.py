"""
User AI Providers Repository
==============================

Manages user's AI provider API keys (encrypted storage).
"""

import logging
from datetime import datetime
from decimal import Decimal

import asyncpg

from core.security.encryption import get_encryption

logger = logging.getLogger(__name__)


class UserAIProvidersRepository:
    """Repository for user AI provider management."""

    def __init__(self, pool: asyncpg.Pool):
        """
        Initialize repository.

        Args:
            pool: AsyncPG connection pool
        """
        self.pool = pool
        self.encryption = get_encryption()

    async def add_provider(
        self,
        user_id: int,
        provider_name: str,
        api_key: str,
        model_preference: str,
        is_default: bool = False,
        monthly_budget_usd: Decimal | None = None,
        config: dict | None = None,
    ) -> dict:
        """
        Add or update user's AI provider.

        Args:
            user_id: User ID
            provider_name: Provider name (openai, claude, etc.)
            api_key: Plain text API key (will be encrypted)
            model_preference: Preferred model
            is_default: Set as default provider
            monthly_budget_usd: Optional monthly budget
            config: Provider-specific config

        Returns:
            Created/updated provider record
        """
        # Encrypt API key
        api_key_encrypted = self.encryption.encrypt(api_key)

        async with self.pool.acquire() as conn:
            # If setting as default, unset other defaults
            if is_default:
                await conn.execute(
                    """
                    UPDATE user_ai_providers
                    SET is_default = FALSE
                    WHERE user_id = $1 AND provider_name != $2
                    """,
                    user_id,
                    provider_name,
                )

            # Insert or update
            row = await conn.fetchrow(
                """
                INSERT INTO user_ai_providers (
                    user_id, provider_name, api_key_encrypted,
                    model_preference, is_default, monthly_budget_usd, config
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (user_id, provider_name)
                DO UPDATE SET
                    api_key_encrypted = EXCLUDED.api_key_encrypted,
                    model_preference = EXCLUDED.model_preference,
                    is_default = EXCLUDED.is_default,
                    monthly_budget_usd = EXCLUDED.monthly_budget_usd,
                    config = EXCLUDED.config,
                    is_active = TRUE,
                    updated_at = NOW()
                RETURNING 
                    id, user_id, provider_name, model_preference,
                    is_active, is_default, monthly_budget_usd,
                    current_month_spent_usd, config, created_at, updated_at
                """,
                user_id,
                provider_name,
                api_key_encrypted,
                model_preference,
                is_default,
                monthly_budget_usd,
                config or {},
            )

            logger.info(
                f"Added AI provider {provider_name} for user {user_id} (default={is_default})"
            )

            return dict(row)

    async def get_provider(
        self,
        user_id: int,
        provider_name: str,
        decrypt_key: bool = False,
    ) -> dict | None:
        """
        Get user's AI provider configuration.

        Args:
            user_id: User ID
            provider_name: Provider name
            decrypt_key: If True, decrypt the API key

        Returns:
            Provider record or None
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    id, user_id, provider_name, api_key_encrypted,
                    model_preference, is_active, is_default,
                    monthly_budget_usd, current_month_spent_usd,
                    config, created_at, updated_at
                FROM user_ai_providers
                WHERE user_id = $1 AND provider_name = $2
                """,
                user_id,
                provider_name,
            )

            if not row:
                return None

            result = dict(row)

            # Decrypt API key if requested
            if decrypt_key:
                result["api_key"] = self.encryption.decrypt(result["api_key_encrypted"])

            # Remove encrypted key from response
            if not decrypt_key:
                result.pop("api_key_encrypted", None)

            return result

    async def get_default_provider(
        self,
        user_id: int,
        decrypt_key: bool = False,
    ) -> dict | None:
        """
        Get user's default AI provider.

        Args:
            user_id: User ID
            decrypt_key: If True, decrypt the API key

        Returns:
            Default provider record or None
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    id, user_id, provider_name, api_key_encrypted,
                    model_preference, is_active, is_default,
                    monthly_budget_usd, current_month_spent_usd,
                    config, created_at, updated_at
                FROM user_ai_providers
                WHERE user_id = $1 
                  AND is_active = TRUE
                  AND is_default = TRUE
                LIMIT 1
                """,
                user_id,
            )

            if not row:
                return None

            result = dict(row)

            if decrypt_key:
                result["api_key"] = self.encryption.decrypt(result["api_key_encrypted"])

            if not decrypt_key:
                result.pop("api_key_encrypted", None)

            return result

    async def list_user_providers(
        self,
        user_id: int,
        active_only: bool = True,
    ) -> list[dict]:
        """
        List all providers for a user.

        Args:
            user_id: User ID
            active_only: Only return active providers

        Returns:
            List of provider records (without decrypted keys)
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT 
                    id, user_id, provider_name, model_preference,
                    is_active, is_default, monthly_budget_usd,
                    current_month_spent_usd, config, created_at, updated_at
                FROM user_ai_providers
                WHERE user_id = $1
            """

            if active_only:
                query += " AND is_active = TRUE"

            query += " ORDER BY is_default DESC, created_at DESC"

            rows = await conn.fetch(query, user_id)
            return [dict(row) for row in rows]

    async def remove_provider(self, user_id: int, provider_name: str) -> bool:
        """
        Remove (deactivate) a provider.

        Args:
            user_id: User ID
            provider_name: Provider name

        Returns:
            True if provider was removed
        """
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM user_ai_providers
                WHERE user_id = $1 AND provider_name = $2
                """,
                user_id,
                provider_name,
            )

            removed = result.split()[-1] == "1"

            if removed:
                logger.info(f"Removed AI provider {provider_name} for user {user_id}")

            return removed

    async def update_spending(
        self,
        user_id: int,
        provider_name: str,
        cost_usd: Decimal,
        tokens_used: int,
    ) -> None:
        """
        Update spending for current month.

        Args:
            user_id: User ID
            provider_name: Provider name
            cost_usd: Cost in USD
            tokens_used: Number of tokens used
        """
        async with self.pool.acquire() as conn:
            # Update current month spending in provider record
            await conn.execute(
                """
                UPDATE user_ai_providers
                SET 
                    current_month_spent_usd = current_month_spent_usd + $3,
                    updated_at = NOW()
                WHERE user_id = $1 AND provider_name = $2
                """,
                user_id,
                provider_name,
                cost_usd,
            )

            # Update monthly spending tracking
            month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            await conn.execute(
                """
                INSERT INTO user_ai_spending (
                    user_id, provider_name, month,
                    total_cost_usd, request_count, tokens_used
                )
                VALUES ($1, $2, $3, $4, 1, $5)
                ON CONFLICT (user_id, provider_name, month)
                DO UPDATE SET
                    total_cost_usd = user_ai_spending.total_cost_usd + $4,
                    request_count = user_ai_spending.request_count + 1,
                    tokens_used = user_ai_spending.tokens_used + $5,
                    updated_at = NOW()
                """,
                user_id,
                provider_name,
                month_start.date(),
                cost_usd,
                tokens_used,
            )

    async def check_budget(
        self,
        user_id: int,
        provider_name: str,
    ) -> tuple[bool, Decimal | None, Decimal | None]:
        """
        Check if user is within budget.

        Args:
            user_id: User ID
            provider_name: Provider name

        Returns:
            Tuple of (within_budget, budget_limit, current_spent)
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT monthly_budget_usd, current_month_spent_usd
                FROM user_ai_providers
                WHERE user_id = $1 AND provider_name = $2
                """,
                user_id,
                provider_name,
            )

            if not row:
                return True, None, None

            budget = row["monthly_budget_usd"]
            spent = row["current_month_spent_usd"]

            # No budget limit set
            if budget is None:
                return True, None, spent

            # Check if within budget
            within_budget = spent < budget

            return within_budget, budget, spent
