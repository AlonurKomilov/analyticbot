# alembic/env.py
# pyright: reportMissingImports=false, reportAttributeAccessIssue=false

from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from bot.database.models import metadata

# Alembic Config obyekti
config = context.config

# Logging (alembic.ini)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata (agar ORM modeli bo‘lsa, shu yerda ularni import qilasiz)
# at top with other imports:
target_metadata = metadata


def _sync_db_url() -> str:
    """
    Migratsiya uchun sinxron URL (psycopg2) qaytaradi.
    DATABASE_URL bo‘lsa — undan olamiz; agar async bo‘lsa, sync’ga o‘girib yuboramiz.
    Bo‘lmasa POSTGRES_* bo‘laklaridan yasaymiz.
    """
    url = os.getenv("DATABASE_URL", "")
    if not url:
        user = os.getenv("POSTGRES_USER", "analytic")
        pwd = os.getenv("POSTGRES_PASSWORD", "change_me")
        host = os.getenv("POSTGRES_HOST", "postgres")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "analytic_bot")
        url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


def run_migrations_offline() -> None:
    url = _sync_db_url()
    config.set_main_option("sqlalchemy.url", url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        compare_type=True,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = _sync_db_url()
    config.set_main_option("sqlalchemy.url", url)
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
