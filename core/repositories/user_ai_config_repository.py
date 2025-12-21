"""
User AI Config Repository
==========================

Repository for managing user AI configuration and tier.
"""

import json
import logging
from datetime import datetime
from typing import Any

import asyncpg

from infra.db.models.ai.user_ai_orm import UserAIConfigORM

logger = logging.getLogger(__name__)


class UserAIConfigRepository:
    """Repository for user AI configuration CRUD operations."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_by_user_id(self, user_id: int) -> dict[str, Any] | None:
        """Get AI config for a user."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    user_id, tier, enabled, settings, preferred_model,
                    temperature, enabled_features, language, response_style,
                    auto_insights_enabled, auto_insights_frequency,
                    data_retention_days, anonymize_data,
                    created_at, updated_at
                FROM user_ai_config
                WHERE user_id = $1
                """,
                user_id,
            )
            return dict(row) if row else None

    async def create(
        self,
        user_id: int,
        tier: str = "free",
        settings: dict | None = None,
        enabled_features: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create new AI config for a user."""
        if enabled_features is None:
            enabled_features = ["analytics_insights", "content_suggestions"]

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO user_ai_config (
                    user_id, tier, enabled, settings, enabled_features,
                    created_at, updated_at
                )
                VALUES ($1, $2, true, $3::jsonb, $4::jsonb, NOW(), NOW())
                RETURNING 
                    user_id, tier, enabled, settings, preferred_model,
                    temperature, enabled_features, language, response_style,
                    auto_insights_enabled, auto_insights_frequency,
                    data_retention_days, anonymize_data,
                    created_at, updated_at
                """,
                user_id,
                tier,
                json.dumps(settings or {}),
                json.dumps(enabled_features),
            )
            logger.info(f"✅ Created AI config for user {user_id} with tier {tier}")
            return dict(row)

    async def update_settings(
        self,
        user_id: int,
        settings: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Update user AI settings."""
        update_fields = []
        params = []
        param_count = 1

        # Build dynamic UPDATE query based on provided settings
        if "preferred_model" in settings:
            update_fields.append(f"preferred_model = ${param_count}")
            params.append(settings["preferred_model"])
            param_count += 1

        if "temperature" in settings:
            update_fields.append(f"temperature = ${param_count}")
            params.append(settings["temperature"])
            param_count += 1

        if "enabled_features" in settings:
            update_fields.append(f"enabled_features = ${param_count}::jsonb")
            params.append(json.dumps(settings["enabled_features"]))
            param_count += 1

        if "language" in settings:
            update_fields.append(f"language = ${param_count}")
            params.append(settings["language"])
            param_count += 1

        if "response_style" in settings:
            update_fields.append(f"response_style = ${param_count}")
            params.append(settings["response_style"])
            param_count += 1

        if "auto_insights_enabled" in settings:
            update_fields.append(f"auto_insights_enabled = ${param_count}")
            params.append(settings["auto_insights_enabled"])
            param_count += 1

        if "auto_insights_frequency" in settings:
            update_fields.append(f"auto_insights_frequency = ${param_count}")
            params.append(settings["auto_insights_frequency"])
            param_count += 1

        if "settings" in settings:
            update_fields.append(f"settings = ${param_count}::jsonb")
            params.append(json.dumps(settings["settings"]))
            param_count += 1

        if not update_fields:
            logger.warning(f"No fields to update for user {user_id}")
            return await self.get_by_user_id(user_id)

        # Add updated_at
        update_fields.append(f"updated_at = ${param_count}")
        params.append(datetime.utcnow())
        param_count += 1

        # Add user_id as last parameter
        params.append(user_id)

        query = f"""
            UPDATE user_ai_config
            SET {', '.join(update_fields)}
            WHERE user_id = ${param_count}
            RETURNING 
                user_id, tier, enabled, settings, preferred_model,
                temperature, enabled_features, language, response_style,
                auto_insights_enabled, auto_insights_frequency,
                data_retention_days, anonymize_data,
                created_at, updated_at
        """

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            if row:
                logger.info(f"✅ Updated AI settings for user {user_id}")
                return dict(row)
            return None

    async def update_tier(self, user_id: int, tier: str) -> dict[str, Any] | None:
        """Update user's AI tier."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE user_ai_config
                SET tier = $1, updated_at = NOW()
                WHERE user_id = $2
                RETURNING 
                    user_id, tier, enabled, settings, preferred_model,
                    temperature, enabled_features, language, response_style,
                    auto_insights_enabled, auto_insights_frequency,
                    data_retention_days, anonymize_data,
                    created_at, updated_at
                """,
                tier,
                user_id,
            )
            if row:
                logger.info(f"✅ Updated AI tier for user {user_id} to {tier}")
                return dict(row)
            return None

    async def get_or_create_default(self, user_id: int) -> dict[str, Any]:
        """Get existing config or create default one with race condition protection."""
        # Try to get existing first
        config = await self.get_by_user_id(user_id)
        if config:
            return config

        logger.info(f"📝 Creating default AI config for new user {user_id}")
        
        # Use INSERT ... ON CONFLICT to handle race conditions
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO user_ai_config (
                    user_id, tier, enabled, settings, enabled_features
                )
                VALUES ($1, $2, true, $3::jsonb, $4::jsonb)
                ON CONFLICT (user_id) DO UPDATE 
                SET user_id = EXCLUDED.user_id
                RETURNING 
                    user_id, tier, enabled, settings, preferred_model,
                    temperature, enabled_features, language, response_style,
                    auto_insights_enabled, auto_insights_frequency,
                    data_retention_days, anonymize_data,
                    created_at, updated_at
                """,
                user_id,
                "free",
                json.dumps({}),
                json.dumps(["analytics_insights", "content_suggestions"]),
            )
            if row:
                logger.info(f"✅ Created AI config for user {user_id} with tier free")
                return dict(row)
            
            # Fallback - fetch if concurrent insert happened
            config = await self.get_by_user_id(user_id)
            if config:
                return config
                
            raise Exception(f"Failed to create or fetch AI config for user {user_id}")

    async def set_enabled(self, user_id: int, enabled: bool) -> dict[str, Any] | None:
        """Enable or disable AI for a user."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE user_ai_config
                SET enabled = $1, updated_at = NOW()
                WHERE user_id = $2
                RETURNING 
                    user_id, tier, enabled, settings, preferred_model,
                    temperature, enabled_features, language, response_style,
                    auto_insights_enabled, auto_insights_frequency,
                    data_retention_days, anonymize_data,
                    created_at, updated_at
                """,
                enabled,
                user_id,
            )
            if row:
                status = "enabled" if enabled else "disabled"
                logger.info(f"✅ AI {status} for user {user_id}")
                return dict(row)
            return None
