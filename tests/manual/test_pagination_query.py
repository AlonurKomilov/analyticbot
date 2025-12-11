"""Test pagination query directly"""

import asyncio

import asyncpg


async def test_pagination():
    # Connect to database
    conn = await asyncpg.connect(
        host="localhost",
        port=10100,
        user="analytic",
        password="change_me",
        database="analytic_bot",
    )

    try:
        # First check total posts
        total_posts = await conn.fetchval("SELECT COUNT(*) FROM posts")
        print(f"Total posts in database: {total_posts}")

        # Check channels
        channels = await conn.fetch("SELECT id, title, user_id FROM channels")
        print(f"\nChannels ({len(channels)}):")
        for ch in channels:
            print(f"  - ID: {ch['id']}, Title: {ch['title']}, User ID: {ch['user_id']}")

        # Check posts
        posts_sample = await conn.fetch(
            "SELECT channel_id, msg_id, date FROM posts ORDER BY date DESC LIMIT 5"
        )
        print("\nRecent posts:")
        for p in posts_sample:
            print(f"  - Channel: {p['channel_id']}, Msg ID: {p['msg_id']}, Date: {p['date']}")

        # Test count for user_id=1
        count_query = "SELECT COUNT(*) FROM posts p WHERE p.channel_id IN (SELECT id FROM channels WHERE user_id = $1)"
        total = await conn.fetchval(count_query, 1)
        print(f"\nTotal posts for user_id=1: {total}")

        # Test page 1
        print("\n=== PAGE 1 ===")
        page_1_query = """
            SELECT p.msg_id, p.date, p.text
            FROM posts p
            WHERE p.channel_id IN (SELECT id FROM channels WHERE user_id = $1)
            ORDER BY p.date DESC
            LIMIT $2 OFFSET $3
        """
        page_1_results = await conn.fetch(page_1_query, 1, 50, 0)
        print(f"Page 1 returned {len(page_1_results)} posts")
        if page_1_results:
            print(
                f"First post: msg_id={page_1_results[0]['msg_id']}, date={page_1_results[0]['date']}"
            )
            print(
                f"Last post: msg_id={page_1_results[-1]['msg_id']}, date={page_1_results[-1]['date']}"
            )

        # Test page 2
        print("\n=== PAGE 2 ===")
        page_2_query = """
            SELECT p.msg_id, p.date, p.text
            FROM posts p
            WHERE p.channel_id IN (SELECT id FROM channels WHERE user_id = $1)
            ORDER BY p.date DESC
            LIMIT $2 OFFSET $3
        """
        page_2_results = await conn.fetch(page_2_query, 1, 50, 50)
        print(f"Page 2 returned {len(page_2_results)} posts")
        if page_2_results:
            print(
                f"First post: msg_id={page_2_results[0]['msg_id']}, date={page_2_results[0]['date']}"
            )
            print(
                f"Last post: msg_id={page_2_results[-1]['msg_id']}, date={page_2_results[-1]['date']}"
            )

        # Show all msg_ids
        print("\n=== ALL POST IDs (ordered by date DESC) ===")
        all_query = """
            SELECT p.msg_id, p.date
            FROM posts p
            WHERE p.channel_id IN (SELECT id FROM channels WHERE user_id = $1)
            ORDER BY p.date DESC
        """
        all_results = await conn.fetch(all_query, 1)
        for i, row in enumerate(all_results, 1):
            marker = ""
            if i <= 50:
                marker = " <- PAGE 1"
            elif i <= 52:
                marker = " <- PAGE 2"
            print(f"{i}. msg_id={row['msg_id']}, date={row['date']}{marker}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(test_pagination())
