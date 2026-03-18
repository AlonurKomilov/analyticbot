"""API route: download generated reports"""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from src.db.repository import AnalysisRepository
from src.db.session import async_session

router = APIRouter()


@router.get("/reports/{analysis_id}/pdf")
async def download_report(analysis_id: int):
    """Download the PDF report for a completed analysis."""
    async with async_session() as session:
        repo = AnalysisRepository(session)
        result = await repo.get_result(analysis_id)

    if not result or not result.report_pdf_path:
        raise HTTPException(status_code=404, detail="Report not found or analysis not complete")

    if not os.path.exists(result.report_pdf_path):
        raise HTTPException(status_code=404, detail="Report file not found on disk")

    return FileResponse(
        result.report_pdf_path,
        media_type="application/pdf",
        filename=f"analytics_report_{analysis_id}.pdf",
    )
