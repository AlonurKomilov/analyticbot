import asyncio
import os

import asyncpg


async def main():
    conn = await asyncpg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "10100")),
        database=os.getenv("POSTGRES_DB", "analytic_bot"),
        user=os.getenv("POSTGRES_USER", "analytic"),
        password=os.getenv("POSTGRES_PASSWORD", "rsDTxy3p&Y+F8LG2Z=KnAIed1a4etjrt4cX+sb@yo6-_7H-bjizWfrwSQ4iJXKg%"),
    )

    print("\n📺 All channels in database:")
    print("=" * 80)
    channels = await conn.fetch("SELECT id, user_id, title, username FROM channels ORDER BY id")

    if not channels:
        print("❌ No channels found!")
    else:
        for ch in channels:
            print(
                f"ID: {ch['id']:15} | User: {ch['user_id']} | Title: {ch['title'][:40]:<40} | @{ch['username'] or 'N/A'}"
            )

    print(f"\nTotal: {len(channels)} channels")

    # Check for any channel with similar name
    print("\n🔍 Searching for 'ABC LEGACY NEWS' or ID 100267887654...")
    abc_channels = await conn.fetch("""
        SELECT id, user_id, title, username
        FROM channels
        WHERE title ILIKE '%ABC%LEGACY%' OR title ILIKE '%ABC%NEWS%' OR id = 100267887654
    """)

    if abc_channels:
        print("Found matches:")
        for ch in abc_channels:
            print(
                f"  ID: {ch['id']} | Title: {ch['title']} | @{ch['username'] or 'N/A'} | User: {ch['user_id']}"
            )
    else:
        print("  ❌ No matches found - Channel not in database!")
        print("\n💡 Solution: You need to add the channel via MTProto Setup page")

    # Check if there are ANY posts
    posts_count = await conn.fetchval("SELECT COUNT(*) FROM posts")
    print(f"\n📊 Total posts in database: {posts_count}")

    if posts_count > 0:
        sample = await conn.fetch("""
            SELECT channel_id, COUNT(*) as count
            FROM posts
            GROUP BY channel_id
            ORDER BY count DESC
            LIMIT 5
        """)
        print("\nTop channels by posts:")
        for s in sample:
            print(f"  Channel {s['channel_id']}: {s['count']} posts")

    await conn.close()


asyncio.run(main())
