# health_app.py
import os

import asyncpg
from fastapi import FastAPI

try:
    import redis.asyncio as redis
except Exception:  # pragma: no cover
    redis = None  # type: ignore

app = FastAPI()


@app.get("/health")
async def health(full: bool = False) -> dict[str, str]:
    # Default legacy contract
    if not full:
        return {"status": "ok"}

    resp: dict[str, str] = {"status": "ok"}
    dsn = os.getenv("DATABASE_URL")
    if dsn:
        try:
            conn = await asyncpg.connect(dsn)
            await conn.close()
            resp["db"] = "ok"
        except Exception:
            resp["db"] = "fail"
            resp["status"] = "degraded"
    r_url = os.getenv("REDIS_URL")
    if redis and r_url:
        try:
            r = redis.from_url(r_url)
            await r.ping()
            resp["redis"] = "ok"
        except Exception:
            resp["redis"] = "fail"
            resp["status"] = "degraded"
    return resp
