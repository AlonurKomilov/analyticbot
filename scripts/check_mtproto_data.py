import asyncio
import os

import asyncpg
from dotenv import load_dotenv

load_dotenv()


async def check_data():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return

    # Convert to asyncpg format
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    conn = await asyncpg.connect(database_url)

    try:
        print("=" * 60)
        print("🔍 CHECKING MTPROTO DATA COLLECTION STATUS")
        print("=" * 60)

        # Check channels
        channels = await conn.fetch("SELECT id, title, username, user_id FROM channels LIMIT 5")
        print(f"\n📺 Channels in database: {len(channels)}")
        for ch in channels:
            print(
                f"  - ID: {ch['id']}, Title: {ch['title']}, @{ch['username']}, User: {ch['user_id']}"
            )

        # Check MTProto settings
        print("\n⚙️  MTProto Settings:")
        mtproto_settings = await conn.fetch(
            """
            SELECT channel_id, is_enabled, collection_mode, user_id
            FROM channel_mtproto_settings
            WHERE is_enabled = true
        """
        )
        print(f"  Enabled MTProto channels: {len(mtproto_settings)}")
        for setting in mtproto_settings:
            print(
                f"  - Channel {setting['channel_id']}: mode={setting['collection_mode']}, user={setting['user_id']}"
            )

        # Check posts
        print("\n📝 Posts data:")
        posts_count = await conn.fetchval("SELECT COUNT(*) FROM posts")
        print(f"  Total posts: {posts_count}")

        if posts_count > 0:
            recent_posts = await conn.fetch(
                """
                SELECT channel_id, msg_id, date, LEFT(text, 50) as text_preview
                FROM posts
                ORDER BY date DESC
                LIMIT 5
            """
            )
            print("  Recent posts:")
            for post in recent_posts:
                print(
                    f"    - Channel {post['channel_id']}, msg_id={post['msg_id']}, {post['date']}"
                )
                print(f"      Text: {post['text_preview']}...")

        # Check post_metrics (THE KEY TABLE FOR POST DYNAMICS)
        print("\n�� Post Metrics (for Post Dynamics):")
        metrics_count = await conn.fetchval("SELECT COUNT(*) FROM post_metrics")
        print(f"  Total metrics snapshots: {metrics_count}")

        if metrics_count > 0:
            # Check recent metrics
            recent_metrics = await conn.fetch(
                """
                SELECT channel_id, msg_id, views, forwards, reactions, snapshot_time
                FROM post_metrics
                ORDER BY snapshot_time DESC
                LIMIT 10
            """
            )
            print("  Recent metrics snapshots:")
            for m in recent_metrics:
                print(f"    - Channel {m['channel_id']}, msg_id={m['msg_id']}")
                print(
                    f"      Views: {m['views']}, Forwards: {m['forwards']}, Reactions: {m['reactions']}"
                )
                print(f"      Time: {m['snapshot_time']}")

            # Check metrics by channel
            metrics_by_channel = await conn.fetch(
                """
                SELECT channel_id, COUNT(*) as metric_count,
                       MAX(snapshot_time) as last_snapshot,
                       MIN(snapshot_time) as first_snapshot
                FROM post_metrics
                GROUP BY channel_id
                ORDER BY metric_count DESC
            """
            )
            print("\n  Metrics by channel:")
            for mc in metrics_by_channel:
                print(f"    - Channel {mc['channel_id']}: {mc['metric_count']} snapshots")
                print(f"      First: {mc['first_snapshot']}, Last: {mc['last_snapshot']}")
        else:
            print("  ⚠️  NO METRICS DATA FOUND!")
            print("  This is why Post Dynamics shows no data!")

        # Check if MTProto collectors are running
        print("\n🤖 MTProto Collection Status:")
        print("  Check if these processes are running:")
        print("  - updates_collector (real-time updates)")
        print("  - history_collector (historical data)")

        # Check ABC LEGACY NEWS specifically (from the screenshot)
        abc_channel = await conn.fetchrow(
            """
            SELECT c.id, c.title, c.username,
                   m.is_enabled, m.collection_mode,
                   (SELECT COUNT(*) FROM posts WHERE channel_id = c.id) as post_count,
                   (SELECT COUNT(*) FROM post_metrics WHERE channel_id = c.id) as metrics_count
            FROM channels c
            LEFT JOIN channel_mtproto_settings m ON c.id = m.channel_id
            WHERE c.id = 1002678877654 OR c.username LIKE '%LEGACY%NEWS%'
            LIMIT 1
        """
        )

        if abc_channel:
            print("\n📺 ABC LEGACY NEWS Channel (from screenshot):")
            print(f"  ID: {abc_channel['id']}")
            print(f"  Title: {abc_channel['title']}")
            print(f"  MTProto Enabled: {abc_channel['is_enabled']}")
            print(f"  Collection Mode: {abc_channel['collection_mode']}")
            print(f"  Posts: {abc_channel['post_count']}")
            print(f"  Metrics snapshots: {abc_channel['metrics_count']}")

            if abc_channel["metrics_count"] == 0:
                print("\n  ⚠️  PROBLEM FOUND:")
                print("     MTProto might be enabled but NOT COLLECTING METRICS!")
                print("     Post dynamics needs post_metrics table data!")

        print("\n" + "=" * 60)
        print("✅ Data check complete")
        print("=" * 60)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_data())
