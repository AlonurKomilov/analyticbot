"""Database repository — simple CRUD for analysis data"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import AnalysisRequest, AnalysisResult, ChannelSnapshot, PostRecord


class AnalysisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Analysis Requests ──────────────────────────────────────────────

    async def create_request(
        self,
        channel_identifier: str,
        requested_by: int | None = None,
        source: str = "bot",
    ) -> AnalysisRequest:
        req = AnalysisRequest(
            channel_identifier=channel_identifier,
            requested_by=requested_by,
            source=source,
            status="pending",
        )
        self.session.add(req)
        await self.session.flush()
        return req

    async def set_request_running(self, request_id: int, channel_id: int, title: str) -> None:
        await self.session.execute(
            update(AnalysisRequest)
            .where(AnalysisRequest.id == request_id)
            .values(status="running", channel_id=channel_id, channel_title=title)
        )

    async def set_request_done(self, request_id: int) -> None:
        await self.session.execute(
            update(AnalysisRequest)
            .where(AnalysisRequest.id == request_id)
            .values(status="done", completed_at=datetime.utcnow())
        )

    async def set_request_failed(self, request_id: int, error: str) -> None:
        await self.session.execute(
            update(AnalysisRequest)
            .where(AnalysisRequest.id == request_id)
            .values(status="failed", error_message=error, completed_at=datetime.utcnow())
        )

    async def get_request(self, request_id: int) -> AnalysisRequest | None:
        result = await self.session.execute(
            select(AnalysisRequest).where(AnalysisRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    # ── Channel Snapshots ──────────────────────────────────────────────

    async def save_snapshot(self, snapshot: ChannelSnapshot) -> ChannelSnapshot:
        self.session.add(snapshot)
        await self.session.flush()
        return snapshot

    # ── Posts ───────────────────────────────────────────────────────────

    async def save_posts(self, posts: list[PostRecord]) -> int:
        self.session.add_all(posts)
        await self.session.flush()
        return len(posts)

    async def get_posts(self, analysis_id: int) -> list[PostRecord]:
        result = await self.session.execute(
            select(PostRecord)
            .where(PostRecord.analysis_id == analysis_id)
            .order_by(PostRecord.date.desc())
        )
        return list(result.scalars().all())

    # ── Analysis Results ───────────────────────────────────────────────

    async def save_result(self, result: AnalysisResult) -> AnalysisResult:
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_result(self, analysis_id: int) -> AnalysisResult | None:
        result = await self.session.execute(
            select(AnalysisResult).where(AnalysisResult.analysis_id == analysis_id)
        )
        return result.scalar_one_or_none()
