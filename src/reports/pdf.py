"""PDF report generation — produces a professional analytics report"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.analyzer.metrics import AnalysisMetrics
from src.reports.charts import generate_all_charts

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "data/reports"))
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _fmt(n: int | float) -> str:
    """Format number with thousand separators."""
    if isinstance(n, float):
        return f"{n:,.1f}"
    return f"{n:,}"


def generate_pdf_report(metrics: AnalysisMetrics, analysis_id: int) -> str:
    """
    Generate a PDF analytics report.

    Returns:
        Path to the generated PDF file.
    """
    report_dir = REPORTS_DIR / f"analysis_{analysis_id}"
    report_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = report_dir / "report.pdf"

    # Generate charts first
    charts = generate_all_charts(metrics, analysis_id)

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        spaceAfter=6 * mm,
        textColor=colors.HexColor("#229ED9"),
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=8 * mm,
        spaceAfter=4 * mm,
        textColor=colors.HexColor("#333333"),
    )
    body_style = styles["BodyText"]
    small_style = ParagraphStyle("Small", parent=body_style, fontSize=8, textColor=colors.gray)

    elements: list = []

    # ── Title ──────────────────────────────────────────────────────────
    channel_display = f"@{metrics.channel_username}" if metrics.channel_username else metrics.channel_title
    elements.append(Paragraph(f"Channel Analytics Report", title_style))
    elements.append(Paragraph(f"<b>{channel_display}</b> — {metrics.channel_title}", body_style))
    elements.append(
        Paragraph(
            f"Generated {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}",
            small_style,
        )
    )
    elements.append(Spacer(1, 8 * mm))

    # ── Overview ───────────────────────────────────────────────────────
    elements.append(Paragraph("Overview", heading_style))

    period = ""
    if metrics.date_from and metrics.date_to:
        period = f"{metrics.date_from.strftime('%Y-%m-%d')} — {metrics.date_to.strftime('%Y-%m-%d')} ({metrics.analysis_period_days} days)"

    overview_data = [
        ["Metric", "Value"],
        ["Type", metrics.channel_type.capitalize()],
        ["Members", _fmt(metrics.member_count)],
        ["Posts analyzed", _fmt(metrics.total_posts)],
        ["Period", period or "—"],
        ["Total views", _fmt(metrics.total_views)],
        ["Avg views/post", _fmt(metrics.avg_views)],
        ["Avg engagement rate", f"{metrics.avg_engagement_rate:.1f}%"],
        ["Total forwards", _fmt(metrics.total_forwards)],
        ["Total reactions", _fmt(metrics.total_reactions)],
        ["Avg posts/day", _fmt(metrics.posting_pattern.avg_posts_per_day)],
    ]

    table = Table(overview_data, colWidths=[7 * cm, 9 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#229ED9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 6 * mm))

    # ── Posting Patterns ───────────────────────────────────────────────
    elements.append(Paragraph("Posting Patterns", heading_style))

    best_hour = (
        f"{metrics.posting_pattern.most_active_hour}:00 UTC"
        if metrics.posting_pattern.most_active_hour is not None
        else "—"
    )
    best_day = (
        WEEKDAY_NAMES[metrics.posting_pattern.most_active_weekday]
        if metrics.posting_pattern.most_active_weekday is not None
        else "—"
    )
    elements.append(Paragraph(f"Most active hour: <b>{best_hour}</b>", body_style))
    elements.append(Paragraph(f"Most active day: <b>{best_day}</b>", body_style))

    if "hourly" in charts:
        elements.append(Spacer(1, 4 * mm))
        elements.append(Image(charts["hourly"], width=15 * cm, height=7.5 * cm))

    if "weekday" in charts:
        elements.append(Spacer(1, 4 * mm))
        elements.append(Image(charts["weekday"], width=15 * cm, height=7.5 * cm))

    # ── Content Mix ────────────────────────────────────────────────────
    elements.append(Paragraph("Content Mix", heading_style))
    if "content_mix" in charts:
        elements.append(Image(charts["content_mix"], width=11 * cm, height=8.5 * cm))

    # ── Top Posts by Views ─────────────────────────────────────────────
    elements.append(Paragraph("Top Posts by Views", heading_style))

    if metrics.top_posts_by_views:
        top_data = [["#", "Post ID", "Views", "Fwd", "React", "Preview"]]
        for i, p in enumerate(metrics.top_posts_by_views[:10], 1):
            top_data.append([
                str(i),
                str(p.message_id),
                _fmt(p.views),
                _fmt(p.forwards),
                _fmt(p.reactions),
                p.text_preview[:50],
            ])

        top_table = Table(top_data, colWidths=[1 * cm, 2 * cm, 2 * cm, 1.5 * cm, 1.5 * cm, 8 * cm])
        top_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34A853")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(top_table)

    if "views" in charts:
        elements.append(Spacer(1, 4 * mm))
        elements.append(Image(charts["views"], width=15 * cm, height=8.5 * cm))

    # ── Footer ─────────────────────────────────────────────────────────
    elements.append(Spacer(1, 10 * mm))
    elements.append(
        Paragraph(
            "Generated by Analyticbot • t.me/analyticbot",
            small_style,
        )
    )

    doc.build(elements)
    return str(pdf_path)
