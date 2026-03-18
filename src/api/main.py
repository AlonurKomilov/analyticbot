"""FastAPI application — web interface for channel analysis"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.analyze import router as analyze_router
from src.api.routes.reports import router as reports_router
from src.db.session import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Analyticbot API starting...")
    await init_db()
    yield
    logger.info("Analyticbot API shutting down.")


app = FastAPI(
    title="Analyticbot API",
    description="Telegram Channel & Group Analytics",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(reports_router, prefix="/api", tags=["Reports"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "analyticbot", "version": "2.0.0"}
