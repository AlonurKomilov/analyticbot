import asyncio
import os

import asyncpg
from dotenv import load_dotenv

load_dotenv()


async def check_data():
    # Connect to database
    conn = await asyncpg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "analyticbot"),
        user=os.getenv("DB_USER", "analyticbot"),
        password=os.getenv("DB_PASSWORD", ""),
    )

    channel_id = 100267887654  # From screenshot

    print(f"\n🔍 Checking channel {channel_id}...")

    # Check if channel exists
    channel = await conn.fetchrow("SELECT * FROM channels WHERE id = $1", channel_id)
    if channel:
        print(f"✅ Channel found: {dict(channel)}")
    else:
        print("❌ Channel NOT found in database")

    # Check posts count
    posts_count = await conn.fetchval(
        "SELECT COUNT(*) FROM posts WHERE channel_id = $1", channel_id
    )
    print(f"\n📊 Posts count: {posts_count}")

    if posts_count > 0:
        # Show sample posts
        posts = await conn.fetch(
            "SELECT msg_id, date, LEFT(text, 50) as text FROM posts WHERE channel_id = $1 ORDER BY date DESC LIMIT 5",
            channel_id,
        )
        print("\n📝 Sample posts:")
        for post in posts:
            print(f"  - Message {post['msg_id']}: {post['text']}... ({post['date']})")

    # Check metrics
    metrics_count = await conn.fetchval(
        "SELECT COUNT(*) FROM post_metrics WHERE channel_id = $1", channel_id
    )
    print(f"\n📈 Metrics snapshots: {metrics_count}")

    if metrics_count > 0:
        # Show sample metrics
        metrics = await conn.fetch(
            """
            SELECT msg_id, views, forwards, reactions_count, snapshot_time
            FROM post_metrics
            WHERE channel_id = $1
            ORDER BY snapshot_time DESC
            LIMIT 5
        """,
            channel_id,
        )
        print("\n📊 Sample metrics:")
        for m in metrics:
            print(
                f"  - Message {m['msg_id']}: {m['views']} views, {m['forwards']} forwards ({m['snapshot_time']})"
            )

    # Check MTProto settings
    settings = await conn.fetchrow(
        "SELECT * FROM channel_mtproto_settings WHERE channel_id = $1", channel_id
    )
    if settings:
        print(f"\n⚙️ MTProto settings: {dict(settings)}")
    else:
        print("\n⚠️ No MTProto settings found (using global default)")

    await conn.close()


asyncio.run(check_data())
