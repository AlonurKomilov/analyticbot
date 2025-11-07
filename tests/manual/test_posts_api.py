"""Test the posts API directly"""

import asyncio

import asyncpg


async def test():
    conn = await asyncpg.connect(
        host="localhost", port=10100, user="analytic", password="change_me", database="analytic_bot"
    )

    try:
        # Use the actual user who owns the channel
        user_id = 844338517  # abclegacyllc@gmail.com - owns the ABC LEGACY NEWS channel
        print(f"Testing with user_id: {user_id}")

        # Test the exact query used in the API
        where_clause = "WHERE p.channel_id IN (SELECT id FROM channels WHERE user_id = $1)"
        params = [user_id]

        # Count query
        count_query = f"SELECT COUNT(*) FROM posts p {where_clause}"
        total = await conn.fetchval(count_query, *params)
        print(f"\nTotal posts: {total}")

        # Page 1 query (LIMIT 50 OFFSET 0)
        limit_param_idx = len(params) + 1
        offset_param_idx = len(params) + 2

        query = f"""
            SELECT p.channel_id, p.msg_id, p.date, p.text
            FROM posts p
            LEFT JOIN channels c ON p.channel_id = c.id
            {where_clause}
            ORDER BY p.date DESC
            LIMIT ${limit_param_idx} OFFSET ${offset_param_idx}
        """

        # Test page 1
        page_1_params = params + [50, 0]
        print("\n=== PAGE 1 ===")
        print(f"Params: {page_1_params}")
        print(f"Query: {query}")
        page_1_results = await conn.fetch(query, *page_1_params)
        print(f"Returned {len(page_1_results)} posts")
        if page_1_results:
            print(f"First: msg_id={page_1_results[0]['msg_id']}")
            print(f"Last: msg_id={page_1_results[-1]['msg_id']}")

        # Test page 2
        page_2_params = params + [50, 50]
        print("\n=== PAGE 2 ===")
        print(f"Params: {page_2_params}")
        page_2_results = await conn.fetch(query, *page_2_params)
        print(f"Returned {len(page_2_results)} posts")
        if page_2_results:
            print(f"First: msg_id={page_2_results[0]['msg_id']}")
            print(f"Last: msg_id={page_2_results[-1]['msg_id']}")

    finally:
        await conn.close()


asyncio.run(test())
