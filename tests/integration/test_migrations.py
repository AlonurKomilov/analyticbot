import os, socket, urllib.parse as up, pytest
from alembic import command
from alembic.config import Config

@pytest.mark.integration
def test_alembic_upgrade_head():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL not set; skipping integration test locally.")

    # quick reachability check (no docker in sandbox -> skip)
    p = up.urlparse(db_url)
    host, port = p.hostname or "localhost", p.port or 5432
    sock = socket.socket()
    sock.settimeout(0.5)
    if sock.connect_ex((host, port)) != 0:
        pytest.skip("DB not reachable in local sandbox; will run in CI.")

    cfg = Config("alembic.ini")
    # env.py already reads from env, but set explicitly for safety:
    cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(cfg, "head")
