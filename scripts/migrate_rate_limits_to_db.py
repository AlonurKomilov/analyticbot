#!/usr/bin/env python3
"""
Migrate Rate Limit Configs from Redis to PostgreSQL (Phase 3)

This script migrates existing rate limit configurations from Redis
to the new PostgreSQL-backed system with full audit trail.

Usage:
    python scripts/migrate_rate_limits_to_db.py [--dry-run]

Options:
    --dry-run    Show what would be migrated without making changes
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis

from config.settings import settings
from infra.db.repositories.rate_limit_repository import RateLimitRepository
from infra.db.models.rate_limit_orm import RateLimitConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Service name mapping
SERVICE_NAMES = {
    "bot_creation": "Bot Creation",
    "bot_operations": "Bot Operations",
    "admin_operations": "Admin Operations",
    "auth_login": "Authentication Login",
    "auth_register": "Authentication Register",
    "public_read": "Public Read Operations",
    "webhook": "Webhook Endpoints",
    "analytics": "Analytics Operations",
}


async def get_redis_configs():
    """Get all rate limit configs from Redis"""
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        # Get all keys matching ratelimit:config:*
        keys = await redis_client.keys("ratelimit:config:*")
        
        configs = {}
        for key in keys:
            service_key = key.replace("ratelimit:config:", "")
            config_data = await redis_client.hgetall(key)
            
            if config_data:
                configs[service_key] = {
                    "service": service_key,
                    "limit": int(config_data.get("limit", 100)),
                    "period": config_data.get("period", "minute"),
                    "enabled": config_data.get("enabled", "true").lower() == "true",
                }
        
        await redis_client.close()
        return configs
        
    except Exception as e:
        logger.error(f"Error getting configs from Redis: {e}")
        return {}


async def migrate_configs(dry_run: bool = False):
    """
    Migrate rate limit configurations from Redis to PostgreSQL

    Args:
        dry_run: If True, show what would be migrated without making changes
    """
    logger.info("=" * 60)
    logger.info("Rate Limit Configuration Migration: Redis → PostgreSQL")
    logger.info("=" * 60)
    
    # Get Redis configs
    logger.info("📥 Fetching configurations from Redis...")
    redis_configs = await get_redis_configs()
    
    if not redis_configs:
        logger.warning("⚠️  No configurations found in Redis")
        logger.info("Using default configurations instead")
        return
    
    logger.info(f"✅ Found {len(redis_configs)} configurations in Redis")
    
    # Create database session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        repo = RateLimitRepository(session)
        
        # Get existing configs from database
        existing_configs = await repo.get_all_configs()
        existing_keys = {config.service_key for config in existing_configs}
        
        logger.info(f"📊 Found {len(existing_configs)} existing configurations in database")
        logger.info("")
        
        # Migrate each config
        migrated_count = 0
        updated_count = 0
        skipped_count = 0
        
        for service_key, config_data in redis_configs.items():
            service_name = SERVICE_NAMES.get(service_key, service_key.replace("_", " ").title())
            
            if dry_run:
                if service_key in existing_keys:
                    logger.info(f"[DRY RUN] Would update: {service_key}")
                    logger.info(f"  Service: {service_name}")
                    logger.info(f"  Limit: {config_data['limit']}/{config_data['period']}")
                    logger.info(f"  Enabled: {config_data['enabled']}")
                else:
                    logger.info(f"[DRY RUN] Would create: {service_key}")
                    logger.info(f"  Service: {service_name}")
                    logger.info(f"  Limit: {config_data['limit']}/{config_data['period']}")
                    logger.info(f"  Enabled: {config_data['enabled']}")
                logger.info("")
                continue
            
            try:
                if service_key in existing_keys:
                    # Update existing config
                    updated = await repo.update_config(
                        service_key=service_key,
                        limit_value=config_data["limit"],
                        period=config_data["period"],
                        enabled=config_data["enabled"],
                        updated_by="migration_script",
                    )
                    
                    if updated:
                        logger.info(f"✅ Updated: {service_key} = {config_data['limit']}/{config_data['period']}")
                        updated_count += 1
                        
                        # Log to audit trail
                        old_config = next((c for c in existing_configs if c.service_key == service_key), None)
                        await repo.log_change(
                            service_key=service_key,
                            action="update",
                            old_config=old_config,
                            new_config=updated,
                            changed_by="system",
                            changed_by_username="migration_script",
                            change_reason="Migrated from Redis to PostgreSQL",
                            metadata={"source": "redis", "migration_date": datetime.utcnow().isoformat()},
                        )
                    else:
                        logger.warning(f"⚠️  Failed to update: {service_key}")
                        skipped_count += 1
                else:
                    # Create new config
                    created = await repo.create_config(
                        service_key=service_key,
                        service_name=service_name,
                        limit_value=config_data["limit"],
                        period=config_data["period"],
                        enabled=config_data["enabled"],
                        description=f"Migrated from Redis on {datetime.utcnow().strftime('%Y-%m-%d')}",
                        created_by="migration_script",
                    )
                    
                    if created:
                        logger.info(f"✅ Created: {service_key} = {config_data['limit']}/{config_data['period']}")
                        migrated_count += 1
                        
                        # Log to audit trail
                        await repo.log_change(
                            service_key=service_key,
                            action="create",
                            old_config=None,
                            new_config=created,
                            changed_by="system",
                            changed_by_username="migration_script",
                            change_reason="Migrated from Redis to PostgreSQL",
                            metadata={"source": "redis", "migration_date": datetime.utcnow().isoformat()},
                        )
                    else:
                        logger.warning(f"⚠️  Failed to create: {service_key}")
                        skipped_count += 1
                        
            except Exception as e:
                logger.error(f"❌ Error migrating {service_key}: {e}")
                skipped_count += 1
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("Migration Summary")
        logger.info("=" * 60)
        
        if dry_run:
            logger.info("[DRY RUN] No changes were made")
            logger.info(f"Would create: {len([k for k in redis_configs.keys() if k not in existing_keys])}")
            logger.info(f"Would update: {len([k for k in redis_configs.keys() if k in existing_keys])}")
        else:
            logger.info(f"✅ Created: {migrated_count}")
            logger.info(f"✅ Updated: {updated_count}")
            logger.info(f"⚠️  Skipped: {skipped_count}")
            logger.info(f"📊 Total: {migrated_count + updated_count + skipped_count}")
        
        logger.info("=" * 60)
    
    await engine.dispose()


async def verify_migration():
    """Verify that all configs are in the database"""
    logger.info("")
    logger.info("🔍 Verifying migration...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        repo = RateLimitRepository(session)
        
        # Get all configs
        all_configs = await repo.get_all_configs()
        
        logger.info(f"✅ Found {len(all_configs)} configurations in database:")
        logger.info("")
        
        for config in all_configs:
            status = "✅ Enabled" if config.enabled else "❌ Disabled"
            logger.info(
                f"  {config.service_key:<20} | {config.limit_value:>4}/{config.period:<6} | {status}"
            )
        
        # Get recent audit logs
        audit_trail = await repo.get_recent_changes(hours=24, limit=10)
        
        if audit_trail:
            logger.info("")
            logger.info(f"📝 Recent audit log entries ({len(audit_trail)}):")
            for entry in audit_trail[:5]:
                logger.info(
                    f"  {entry.action:<8} | {entry.service_key:<20} | "
                    f"{entry.changed_by_username or entry.changed_by}"
                )
    
    await engine.dispose()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Migrate rate limit configurations from Redis to PostgreSQL"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing database configs without migration",
    )
    
    args = parser.parse_args()
    
    try:
        if args.verify_only:
            await verify_migration()
        else:
            await migrate_configs(dry_run=args.dry_run)
            
            if not args.dry_run:
                await verify_migration()
        
        logger.info("")
        logger.info("✅ Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
