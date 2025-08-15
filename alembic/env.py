import os
from typing import Any

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

from bot.config import settings  # <— bizning pydantic settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _secret_to_str(v: Any) -> str | None:
    # SecretStr bo‘lsa ham odiy strga aylantiramiz
    if v is None:
        return None
    try:
        return v.get_secret_value()  # pydantic SecretStr
    except Exception:
        return str(v)


def get_db_url() -> str:
    """
    DSN ni settings yoki ENVdan oladi.
    App asyncpg ishlatishi mumkin, Alembic esa sync driver bilan yuradi —
    shuning uchun +asyncpg bo‘lsa, olib tashlaymiz.
    """
    candidates = [
        getattr(settings, "DATABASE_URL", None),
        getattr(settings, "DB_URL", None),
        getattr(settings, "DB_DSN", None),
        os.getenv("DATABASE_URL"),
        os.getenv("DB_URL"),
        os.getenv("POSTGRES_DSN"),
    ]
    for c in candidates:
        dsn = _secret_to_str(c)
        if dsn:
            break
    else:
        # oxirgi chora — ENV komponentlaridan yig'amiz
        user = os.getenv("POSTGRES_USER", "postgres")
        pwd  = os.getenv("POSTGRES_PASSWORD", "postgres")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db   = os.getenv("POSTGRES_DB", "postgres")
        dsn  = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

    # Alembic sync driverga muhtoj: +asyncpg bo'lsa olib tashlaymiz
    if "+asyncpg" in dsn:
        dsn = dsn.replace("+asyncpg", "")
    return dsn


# Alembic configga DSN ni beramiz
config.set_main_option("sqlalchemy.url", get_db_url())