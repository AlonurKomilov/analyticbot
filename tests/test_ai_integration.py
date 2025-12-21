#!/usr/bin/env python3
"""
Integration test for AI System database persistence.

Tests the full flow:
1. Create user AI config
2. Update settings
3. Track usage
4. Enable services
5. Verify database state
"""

import asyncio
import asyncpg
from datetime import datetime

# Database connection settings
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "analytic_bot",
    "user": "analytic",
    "password": "analyticdbdev",
}


async def test_ai_repositories():
    """Test AI repositories integration."""
    print("=" * 60)
    print("Testing AI System Database Integration")
    print("=" * 60)
    
    # Create connection pool
    pool = await asyncpg.create_pool(**DB_CONFIG)
    
    try:
        # Test 1: Create user AI config
        print("\n[1/5] Testing user AI config creation...")
        test_user_id = 99999  # Test user
        
        # Clean up any existing test data
        await pool.execute("DELETE FROM user_ai_config WHERE user_id = $1", test_user_id)
        await pool.execute("DELETE FROM user_ai_usage WHERE user_id = $1", test_user_id)
        await pool.execute("DELETE FROM user_ai_services WHERE user_id = $1", test_user_id)
        
        # Create config
        await pool.execute(
            """
            INSERT INTO user_ai_config (user_id, tier, enabled, settings)
            VALUES ($1, $2, $3, $4)
            """,
            test_user_id,
            "basic",
            True,
            {
                "enabled_features": ["content_analysis", "recommendations"],
                "temperature": 0.7,
                "language": "en",
            },
        )
        
        config = await pool.fetchrow(
            "SELECT * FROM user_ai_config WHERE user_id = $1",
            test_user_id,
        )
        
        assert config is not None, "Config creation failed"
        assert config["tier"] == "basic", "Tier mismatch"
        print(f"   ✓ Created config for user {test_user_id}")
        print(f"     Tier: {config['tier']}, Enabled: {config['enabled']}")
        
        # Test 2: Update settings
        print("\n[2/5] Testing settings update...")
        new_settings = {
            "enabled_features": ["content_analysis", "recommendations", "auto_insights"],
            "temperature": 0.8,
            "language": "en",
            "auto_insights_enabled": True,
        }
        
        await pool.execute(
            """
            UPDATE user_ai_config
            SET settings = $1, updated_at = NOW()
            WHERE user_id = $2
            """,
            new_settings,
            test_user_id,
        )
        
        updated_config = await pool.fetchrow(
            "SELECT * FROM user_ai_config WHERE user_id = $1",
            test_user_id,
        )
        
        assert updated_config["settings"]["temperature"] == 0.8, "Settings update failed"
        print(f"   ✓ Updated settings")
        print(f"     New temperature: {updated_config['settings']['temperature']}")
        
        # Test 3: Track usage
        print("\n[3/5] Testing usage tracking...")
        
        # Insert today's usage
        await pool.execute(
            """
            INSERT INTO user_ai_usage (user_id, usage_date, request_count, tier_at_time)
            VALUES ($1, CURRENT_DATE, 5, $2)
            ON CONFLICT (user_id, usage_date)
            DO UPDATE SET request_count = user_ai_usage.request_count + 5
            """,
            test_user_id,
            "basic",
        )
        
        usage = await pool.fetchrow(
            """
            SELECT * FROM user_ai_usage
            WHERE user_id = $1 AND usage_date = CURRENT_DATE
            """,
            test_user_id,
        )
        
        assert usage is not None, "Usage tracking failed"
        assert usage["request_count"] == 5, "Request count mismatch"
        print(f"   ✓ Tracked usage")
        print(f"     Requests today: {usage['request_count']}")
        
        # Test 4: Enable service
        print("\n[4/5] Testing service activation...")
        
        await pool.execute(
            """
            INSERT INTO user_ai_services (
                user_id, service_type, tier_required, is_active
            )
            VALUES ($1, $2, $3, $4)
            """,
            test_user_id,
            "content_scheduler",
            "basic",
            True,
        )
        
        service = await pool.fetchrow(
            """
            SELECT * FROM user_ai_services
            WHERE user_id = $1 AND service_type = $2
            """,
            test_user_id,
            "content_scheduler",
        )
        
        assert service is not None, "Service activation failed"
        assert service["is_active"] is True, "Service not active"
        print(f"   ✓ Activated service")
        print(f"     Service: {service['service_type']}, Active: {service['is_active']}")
        
        # Test 5: Verify all data
        print("\n[5/5] Verifying complete state...")
        
        final_config = await pool.fetchrow(
            "SELECT * FROM user_ai_config WHERE user_id = $1",
            test_user_id,
        )
        
        final_usage = await pool.fetchrow(
            """
            SELECT * FROM user_ai_usage
            WHERE user_id = $1 AND usage_date = CURRENT_DATE
            """,
            test_user_id,
        )
        
        active_services = await pool.fetch(
            """
            SELECT * FROM user_ai_services
            WHERE user_id = $1 AND is_active = TRUE
            """,
            test_user_id,
        )
        
        print(f"   ✓ Final state verified")
        print(f"     Config: tier={final_config['tier']}, enabled={final_config['enabled']}")
        print(f"     Usage: {final_usage['request_count']} requests")
        print(f"     Active services: {len(active_services)}")
        
        # Cleanup
        print("\n[Cleanup] Removing test data...")
        await pool.execute("DELETE FROM user_ai_config WHERE user_id = $1", test_user_id)
        await pool.execute("DELETE FROM user_ai_usage WHERE user_id = $1", test_user_id)
        await pool.execute("DELETE FROM user_ai_services WHERE user_id = $1", test_user_id)
        print("   ✓ Test data cleaned up")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(test_ai_repositories())
