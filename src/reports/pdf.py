"""PDF report generation — produces a professional analytics report"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.analyzer.metrics import AnalysisMetrics
from src.bot.i18n import format_date, t
from src.reports.charts import generate_all_charts

from src.config import settings

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "data/reports"))

# ── Register Cyrillic-capable fonts ────────────────────────────────────────
_FONT = "DejaVuSans"
_FONT_BOLD = "DejaVuSans-Bold"
pdfmetrics.registerFont(TTFont(_FONT, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont(_FONT_BOLD, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily(_FONT, normal=_FONT, bold=_FONT_BOLD)

# ── Colors ─────────────────────────────────────────────────────────────────
BRAND_BLUE = colors.HexColor("#229ED9")
DARK = colors.HexColor("#333333")
LIGHT_ROW = colors.HexColor("#F8F9FA")
BORDER = colors.HexColor("#E0E0E0")
GREEN = colors.HexColor("#34A853")
RED = colors.HexColor("#EA4335")


def _fmt(n: int | float) -> str:
    """Format number with thousand separators."""
    if isinstance(n, float):
        return f"{n:,.1f}"
    return f"{n:,}"


def _pct(n: float) -> str:
    return f"{n:.2f}%"


def _cell(text: str, style: ParagraphStyle) -> Paragraph:
    """Wrap text in a Paragraph so it can line-break inside table cells."""
    return Paragraph(str(text), style)


def _styled_table(data, col_widths, header_color=BRAND_BLUE, font_size: int = 9):
    """Create a consistently styled table."""
    table = Table(data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), header_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), _FONT_BOLD),
                ("FONTNAME", (0, 1), (-1, -1), _FONT),
                ("FONTSIZE", (0, 0), (-1, 0), font_size),
                ("FONTSIZE", (0, 1), (-1, -1), font_size),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_ROW]),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def generate_pdf_report(metrics: AnalysisMetrics, analysis_id: int, lang: str = "en") -> str:
    """Generate a PDF analytics report. Returns path to the generated PDF file."""
    report_dir = REPORTS_DIR / f"analysis_{analysis_id}"
    report_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = report_dir / "report.pdf"

    # Generate charts first
    charts = generate_all_charts(metrics, analysis_id, lang=lang)

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
        fontName=_FONT_BOLD,
        fontSize=22,
        spaceAfter=4 * mm,
        textColor=BRAND_BLUE,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName=_FONT_BOLD,
        fontSize=14,
        spaceBefore=8 * mm,
        spaceAfter=4 * mm,
        textColor=DARK,
        borderWidth=0,
        borderPadding=0,
    )
    body_style = ParagraphStyle("BodyCyrillic", parent=styles["BodyText"], fontName=_FONT)
    small_style = ParagraphStyle("Small", parent=body_style, fontName=_FONT, fontSize=8, textColor=colors.gray)
    note_style = ParagraphStyle(
        "Note",
        parent=body_style,
        fontName=_FONT,
        fontSize=8,
        textColor=colors.HexColor("#666666"),
        backColor=colors.HexColor("#F5F5F5"),
        borderPadding=6,
        spaceBefore=4 * mm,
        spaceAfter=4 * mm,
    )
    insight_style = ParagraphStyle(
        "Insight",
        parent=body_style,
        fontName=_FONT,
        fontSize=9,
        textColor=DARK,
        leftIndent=8,
    )

    elements: list = []

    # ━━ PAGE 1: Title + Overview + Engagement ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # ── Title ──────────────────────────────────────────────────────────
    channel_display = (
        f"@{metrics.channel_username}" if metrics.channel_username else metrics.channel_title
    )
    elements.append(Paragraph(t("pdf_title", lang), title_style))
    elements.append(Paragraph(f"<b>{channel_display}</b> — {metrics.channel_title}", body_style))
    if metrics.description:
        desc_preview = metrics.description[:200] + ("…" if len(metrics.description) > 200 else "")
        elements.append(
            Paragraph(f"<i>{desc_preview}</i>", ParagraphStyle("Desc", parent=small_style, fontSize=8))
        )
    elements.append(
        Paragraph(
            t("pdf_generated", lang, date=datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')),
            small_style,
        )
    )
    elements.append(Spacer(1, 6 * mm))

    # ── Overview table ─────────────────────────────────────────────────
    elements.append(Paragraph(t("pdf_overview", lang), heading_style))

    period = ""
    if metrics.date_from and metrics.date_to:
        period = (
            f"{format_date(metrics.date_from, lang)} — "
            f"{format_date(metrics.date_to, lang)} ({metrics.analysis_period_days} {t('pdf_days', lang)})"
        )

    overview_data = [
        [t("pdf_metric", lang), t("pdf_value", lang)],
        [t("pdf_type", lang), t(f"type_{metrics.channel_type}", lang)],
        [t("pdf_members", lang), _fmt(metrics.member_count)],
        [t("pdf_status", lang), t(f"pdf_activity_{metrics.activity_status}", lang)],
        [t("pdf_last_post", lang),
         t("pdf_today", lang) if metrics.days_since_last_post == 0
         else t("pdf_days_ago", lang, days=metrics.days_since_last_post)],
        [t("pdf_posts_analyzed", lang), _fmt(metrics.total_posts)],
        [t("pdf_period", lang), period or "—"],
        [t("pdf_total_views", lang), _fmt(metrics.total_views)],
        [t("pdf_avg_views", lang), _fmt(metrics.avg_views)],
        [t("pdf_median_views", lang), _fmt(metrics.engagement.median_views)],
        [t("pdf_avg_engagement", lang), f"{metrics.avg_engagement_rate:.1f}%"],
        [t("pdf_avg_posts_day", lang), _fmt(metrics.posting_pattern.avg_posts_per_day)],
    ]
    elements.append(_styled_table(overview_data, [7 * cm, 9 * cm]))
    elements.append(Spacer(1, 4 * mm))

    # ── Data coverage note ─────────────────────────────────────────────
    if metrics.date_from and metrics.date_to:
        note_text = t(
            "pdf_data_note", lang,
            n=metrics.total_posts,
            date_from=format_date(metrics.date_from, lang),
            date_to=format_date(metrics.date_to, lang),
            days=metrics.analysis_period_days,
        )
        if metrics.total_posts >= 500:
            note_text += t("pdf_data_note_partial", lang)
        else:
            note_text += t("pdf_data_note_full", lang)
    else:
        note_text = t("pdf_data_note_cached", lang)
    elements.append(Paragraph(f"ℹ️ {note_text}", note_style))

    # ── Activity warnings ──────────────────────────────────────────────
    warn_style = ParagraphStyle(
        "Warning",
        parent=body_style,
        fontName=_FONT,
        fontSize=8,
        textColor=colors.HexColor("#B45309"),
        backColor=colors.HexColor("#FEF3C7"),
        borderPadding=6,
        spaceBefore=2 * mm,
        spaceAfter=4 * mm,
    )
    if metrics.days_since_last_post > 14:
        elements.append(Paragraph(t("pdf_warn_stale", lang, days=metrics.days_since_last_post), warn_style))
    elif metrics.total_posts < 50 and metrics.analysis_period_days > 90:
        elements.append(Paragraph(
            t("pdf_warn_low_posts", lang, n=metrics.total_posts, days=metrics.analysis_period_days),
            warn_style,
        ))

    # ── Engagement Breakdown ───────────────────────────────────────────
    elements.append(Paragraph(t("pdf_engagement_breakdown", lang), heading_style))

    eng = metrics.engagement
    desc_cell_s = ParagraphStyle("DescCell", fontName=_FONT, fontSize=8, leading=10, textColor=DARK)
    engagement_data = [
        [t("pdf_metric", lang), t("pdf_value", lang), _cell(t("pdf_what_it_means", lang), desc_cell_s)],
        [
            t("pdf_reach", lang),
            f"{eng.views_per_member * 100:.1f}%",
            _cell(t("pdf_reach_desc", lang), desc_cell_s),
        ],
        [
            t("pdf_virality", lang),
            _pct(eng.virality_rate),
            _cell(t("pdf_virality_desc", lang), desc_cell_s),
        ],
        [
            t("pdf_interaction", lang),
            _pct(eng.interaction_rate),
            _cell(t("pdf_interaction_desc", lang), desc_cell_s),
        ],
        [
            t("pdf_avg_replies", lang),
            _fmt(eng.avg_replies_per_post),
            _cell(t("pdf_avg_replies_desc", lang), desc_cell_s),
        ],
        [
            t("pdf_posts_with_links", lang),
            f"{eng.pct_posts_with_links:.0f}%",
            _cell(t("pdf_posts_with_links_desc", lang), desc_cell_s),
        ],
    ]
    elements.append(_styled_table(engagement_data, [3.5 * cm, 2.5 * cm, 10 * cm], font_size=8))

    if "engagement" in charts:
        elements.append(Spacer(1, 4 * mm))
        elements.append(Image(charts["engagement"], width=13 * cm, height=7.5 * cm))

    # ── Interaction stats ──────────────────────────────────────────────
    interaction_data = [
        [t("pdf_metric", lang), t("pdf_total", lang), t("pdf_avg_per_post", lang)],
        [t("pdf_views", lang), _fmt(metrics.total_views), _fmt(metrics.avg_views)],
        [t("pdf_forwards", lang), _fmt(metrics.total_forwards), _fmt(metrics.avg_forwards_per_post)],
        [t("pdf_reactions", lang), _fmt(metrics.total_reactions), _fmt(metrics.avg_reactions_per_post)],
        [
            t("pdf_replies", lang),
            _fmt(metrics.total_replies),
            _fmt(eng.avg_replies_per_post),
        ],
    ]
    elements.append(Spacer(1, 4 * mm))
    elements.append(_styled_table(interaction_data, [5 * cm, 5.5 * cm, 5.5 * cm]))

    # ━━ PAGE 2: Views Trend + Posting Patterns ━━━━━━━━━━━━━━━━━━━━━━━━━
    elements.append(PageBreak())

    # ── Views Trend ────────────────────────────────────────────────────
    if "views_trend" in charts:
        elements.append(Paragraph(t("pdf_views_trend", lang), heading_style))
        elements.append(Image(charts["views_trend"], width=16 * cm, height=8 * cm))
        elements.append(Spacer(1, 2 * mm))

    # ── Posting Patterns ───────────────────────────────────────────────
    elements.append(Paragraph(t("pdf_posting_patterns", lang), heading_style))

    best_hour = (
        f"{metrics.posting_pattern.most_active_hour}:00 UTC"
        if metrics.posting_pattern.most_active_hour is not None
        else "—"
    )
    best_day = (
        t(f"weekday_{metrics.posting_pattern.most_active_weekday}", lang)
        if metrics.posting_pattern.most_active_weekday is not None
        else "—"
    )
    elements.append(
        Paragraph(
            f"{t('pdf_peak_hour', lang)}: <b>{best_hour}</b> &nbsp;|&nbsp; {t('pdf_peak_day', lang)}: <b>{best_day}</b>",
            insight_style,
        )
    )

    if "hourly" in charts:
        elements.append(Spacer(1, 3 * mm))
        elements.append(Image(charts["hourly"], width=15 * cm, height=7 * cm))

    if "weekday" in charts:
        elements.append(Spacer(1, 3 * mm))
        elements.append(Image(charts["weekday"], width=15 * cm, height=7 * cm))

    # ━━ PAGE 3: Content Mix + Top Posts ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elements.append(PageBreak())

    # ── Content Mix ────────────────────────────────────────────────────
    elements.append(Paragraph(t("pdf_content_mix", lang), heading_style))
    if "content_mix" in charts:
        elements.append(Image(charts["content_mix"], width=10 * cm, height=8 * cm))

    # ── Top Posts by Views ─────────────────────────────────────────────
    elements.append(Paragraph(t("pdf_top_posts", lang), heading_style))

    if metrics.top_posts_by_views:
        cell_s = ParagraphStyle("CellSmall", fontName=_FONT, fontSize=7, leading=9)
        cell_s_b = ParagraphStyle("CellSmallBold", fontName=_FONT_BOLD, fontSize=7, leading=9, textColor=colors.white)
        top_data = [[
            _cell("#", cell_s_b),
            _cell(t("pdf_post_id", lang), cell_s_b),
            _cell(t("pdf_views", lang), cell_s_b),
            _cell(t("pdf_fwd", lang), cell_s_b),
            _cell(t("pdf_react", lang), cell_s_b),
            _cell(t("pdf_er_pct", lang), cell_s_b),
            _cell(t("pdf_preview", lang), cell_s_b),
        ]]
        for i, p in enumerate(metrics.top_posts_by_views[:10], 1):
            top_data.append([
                str(i),
                str(p.message_id),
                _fmt(p.views),
                _fmt(p.forwards),
                _fmt(p.reactions),
                f"{p.engagement_rate:.1f}",
                _cell(p.text_preview[:45], cell_s),
            ])

        top_table = _styled_table(
            top_data,
            [0.6 * cm, 1.0 * cm, 2.2 * cm, 1.3 * cm, 1.5 * cm, 1.0 * cm, 8.4 * cm],
            header_color=GREEN,
            font_size=7,
        )
        elements.append(top_table)

    if "views" in charts:
        elements.append(Spacer(1, 4 * mm))
        elements.append(Image(charts["views"], width=15 * cm, height=8 * cm))

    # ── Top Posts by Engagement ────────────────────────────────────────
    if metrics.top_posts_by_engagement and metrics.member_count > 0:
        elements.append(Paragraph(t("pdf_top_posts_er", lang), heading_style))

        cell_s = ParagraphStyle("CellSmall2", fontName=_FONT, fontSize=7, leading=9)
        cell_s_b2 = ParagraphStyle("CellSmallBold2", fontName=_FONT_BOLD, fontSize=7, leading=9, textColor=colors.white)
        eng_data = [[
            _cell("#", cell_s_b2),
            _cell(t("pdf_post_id", lang), cell_s_b2),
            _cell(t("pdf_er_pct", lang), cell_s_b2),
            _cell(t("pdf_views", lang), cell_s_b2),
            _cell(t("pdf_fwd", lang), cell_s_b2),
            _cell(t("pdf_react", lang), cell_s_b2),
            _cell(t("pdf_preview", lang), cell_s_b2),
        ]]
        for i, p in enumerate(metrics.top_posts_by_engagement[:5], 1):
            eng_data.append([
                str(i),
                str(p.message_id),
                f"{p.engagement_rate:.1f}%",
                _fmt(p.views),
                _fmt(p.forwards),
                _fmt(p.reactions),
                _cell(p.text_preview[:45], cell_s),
            ])

        elements.append(
            _styled_table(
                eng_data,
                [0.6 * cm, 1.0 * cm, 1.2 * cm, 2.2 * cm, 1.3 * cm, 1.5 * cm, 8.2 * cm],
                header_color=colors.HexColor("#FBBC04"),
                font_size=7,
            )
        )

    # ── Footer ─────────────────────────────────────────────────────────
    elements.append(Spacer(1, 10 * mm))
    bot_name = settings.BOT_USERNAME or "analyticbot"
    elements.append(
        Paragraph(
            t("pdf_footer", lang, bot_name=bot_name),
            small_style,
        )
    )

    doc.build(elements)
    return str(pdf_path)
