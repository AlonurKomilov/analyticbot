#!/usr/bin/env python3
"""
Test script to verify MTProto disabled status fix

This script:
1. Disables MTProto for a test channel
2. Makes API call to check admin status
3. Verifies the response includes mtproto_disabled=true
4. Re-enables MTProto to restore normal operation
"""

import asyncio
import sys

import asyncpg


async def main():
    print("🧪 Testing MTProto Disabled Status Fix")
    print("=" * 50)

    # Database connection
    db_url = "postgresql://analytic:change_me@localhost:10100/analytic_bot"

    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

    # Get a test channel
    try:
        channel = await conn.fetchrow(
            """
            SELECT c.id, c.name, cms.mtproto_enabled
            FROM channels c
            LEFT JOIN channel_mtproto_settings cms
                ON c.id = cms.channel_id
            WHERE c.user_id = 844338517
            LIMIT 1
        """
        )

        if not channel:
            print("❌ No channels found for user 844338517")
            await conn.close()
            sys.exit(1)

        channel_id = channel["id"]
        channel_name = channel["name"]
        original_status = (
            channel["mtproto_enabled"] if channel["mtproto_enabled"] is not None else True
        )

        print("\n📺 Test Channel:")
        print(f"   ID: {channel_id}")
        print(f"   Name: {channel_name}")
        print(f"   Current MTProto Status: {'Enabled' if original_status else 'Disabled'}")

    except Exception as e:
        print(f"❌ Failed to fetch channel: {e}")
        await conn.close()
        sys.exit(1)

    # Step 1: Disable MTProto for the channel
    print("\n🔧 Step 1: Disabling MTProto for channel...")
    try:
        # Check if setting exists
        setting = await conn.fetchrow(
            """
            SELECT id FROM channel_mtproto_settings
            WHERE channel_id = $1 AND user_id = 844338517
        """,
            channel_id,
        )

        if setting:
            # Update existing setting
            await conn.execute(
                """
                UPDATE channel_mtproto_settings
                SET mtproto_enabled = false
                WHERE channel_id = $1 AND user_id = 844338517
            """,
                channel_id,
            )
        else:
            # Insert new setting
            await conn.execute(
                """
                INSERT INTO channel_mtproto_settings
                (channel_id, user_id, mtproto_enabled)
                VALUES ($1, 844338517, false)
            """,
                channel_id,
            )

        # Verify
        result = await conn.fetchrow(
            """
            SELECT mtproto_enabled
            FROM channel_mtproto_settings
            WHERE channel_id = $1 AND user_id = 844338517
        """,
            channel_id,
        )

        if result and result["mtproto_enabled"] == False:
            print("   ✅ MTProto disabled successfully")
        else:
            print("   ❌ Failed to disable MTProto")
            await conn.close()
            sys.exit(1)

    except Exception as e:
        print(f"   ❌ Error: {e}")
        await conn.close()
        sys.exit(1)

    # Step 2: Test admin status API
    print("\n🌐 Step 2: Testing Admin Status API...")
    print("   ⚠️  Manual test required:")
    print("   1. Open browser DevTools (F12)")
    print("   2. Go to Application > Local Storage")
    print("   3. Copy the 'token' value")
    print("   4. Run this command:")
    print(
        f"""
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
     http://localhost:11400/channels/admin-status/check-all \\
     | jq '.results | to_entries[] | select(.value.channel_id == {channel_id})'
   """
    )
    print('   5. Verify the response includes: "mtproto_disabled": true')

    # Step 3: Re-enable MTProto
    print("\n🔄 Step 3: Re-enabling MTProto...")
    try:
        if original_status:
            # Restore original enabled state
            await conn.execute(
                """
                UPDATE channel_mtproto_settings
                SET mtproto_enabled = true
                WHERE channel_id = $1 AND user_id = 844338517
            """,
                channel_id,
            )
            print("   ✅ MTProto re-enabled successfully")
        else:
            print("   ℹ️  Channel was originally disabled, leaving as-is")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    await conn.close()

    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("\nNext Steps:")
    print("1. Test the frontend:")
    print("   - Go to http://localhost:11300/channels")
    print("   - Disable MTProto for a channel using the toggle")
    print("   - Check that the status dot turns dark grey")
    print("   - Hover over it to see '🚫 Disabled for this channel'")
    print("2. Check worker logs:")
    print("   - tail -f logs/dev_mtproto_worker.log")
    print("   - Wait for next cycle (~10 minutes)")
    print("   - Verify it skips the disabled channel")


if __name__ == "__main__":
    asyncio.run(main())
