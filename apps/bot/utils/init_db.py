import asyncio
import logging

from infra.db.connection_manager import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
CREATE_TABLES_COMMANDS = [
    "\n    CREATE TABLE IF NOT EXISTS plans (\n        id SERIAL PRIMARY KEY,\n        name VARCHAR(50) UNIQUE NOT NULL,\n        max_channels INTEGER DEFAULT 1,\n        max_posts_per_month INTEGER DEFAULT 30\n    );\n    ",
    "\n    CREATE TABLE IF NOT EXISTS users (\n        id BIGINT PRIMARY KEY,\n        username VARCHAR(255),\n        plan_id INTEGER,\n        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()\n    );\n    ",
    "\n    CREATE TABLE IF NOT EXISTS channels (\n        id BIGINT PRIMARY KEY,\n        user_id BIGINT NOT NULL,\n        title VARCHAR(255),\n        username VARCHAR(255) UNIQUE,\n        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()\n    );\n    ",
    "\n    CREATE TABLE IF NOT EXISTS scheduled_posts (\n        id SERIAL PRIMARY KEY,\n        user_id BIGINT,\n        channel_id BIGINT,\n        post_text TEXT,\n        media_id VARCHAR(255),\n        media_type VARCHAR(50),\n        inline_buttons JSON,\n        status VARCHAR(50) DEFAULT 'pending',\n        schedule_time TIMESTAMP WITH TIME ZONE,\n        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),\n        views INTEGER DEFAULT 0\n    );\n    ",
    "\n    CREATE TABLE IF NOT EXISTS sent_posts (\n        id SERIAL PRIMARY KEY,\n        scheduled_post_id INTEGER NOT NULL,\n        channel_id BIGINT NOT NULL,\n        message_id BIGINT NOT NULL,\n        sent_at TIMESTAMP WITH TIME ZONE DEFAULT now()\n    );\n    ",
]
ADD_CONSTRAINTS_COMMANDS = [
    "ALTER TABLE users ADD CONSTRAINT fk_users_plan_id FOREIGN KEY (plan_id) REFERENCES plans(id);",
    "ALTER TABLE channels ADD CONSTRAINT fk_channels_user_id FOREIGN KEY (user_id) REFERENCES users(id);",
    "ALTER TABLE scheduled_posts ADD CONSTRAINT fk_scheduled_posts_user_id FOREIGN KEY (user_id) REFERENCES users(id);",
    "ALTER TABLE scheduled_posts ADD CONSTRAINT fk_scheduled_posts_channel_id FOREIGN KEY (channel_id) REFERENCES channels(id);",
    "ALTER TABLE sent_posts ADD CONSTRAINT fk_sent_posts_scheduled_post_id FOREIGN KEY (scheduled_post_id) REFERENCES scheduled_posts(id);",
    "ALTER TABLE sent_posts ADD CONSTRAINT fk_sent_posts_channel_id FOREIGN KEY (channel_id) REFERENCES channels(id);",
]


async def main():
    """Manually creates all tables first, then adds all foreign key constraints."""
    logger.info("Connecting to the database...")

    # Initialize database manager
    await db_manager.initialize()

    try:
        async with db_manager.connection() as connection:
            logger.info("--- Step 1: Creating tables without constraints ---")
            for statement in CREATE_TABLES_COMMANDS:
                await connection.execute(statement)
            logger.info("✅ All tables created successfully.")
            logger.info("--- Step 2: Adding foreign key constraints ---")
            for statement in ADD_CONSTRAINTS_COMMANDS:
                await connection.execute(statement)
            logger.info("✅ All foreign key constraints added successfully!")
    except Exception as e:
        logger.error(f"❌ An error occurred during database initialization: {e}", exc_info=True)
    finally:
        await db_manager.close()
        logger.info("Database connection closed.")


if __name__ == "__main__":
    asyncio.run(main())
