"""Chart generation for reports — Plotly-based, saved as PNG"""

from __future__ import annotations

import io
import os
from pathlib import Path

import plotly.graph_objects as go

from src.analyzer.metrics import AnalysisMetrics

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "data/reports"))
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def create_views_chart(metrics: AnalysisMetrics) -> bytes:
    """Bar chart of top posts by views."""
    top = metrics.top_posts_by_views[:10]
    if not top:
        return b""

    labels = [f"#{p.message_id}" for p in top]
    values = [p.views for p in top]

    fig = go.Figure(go.Bar(x=labels, y=values, marker_color="#229ED9"))
    fig.update_layout(
        title="Top Posts by Views",
        xaxis_title="Post",
        yaxis_title="Views",
        template="plotly_white",
        width=700,
        height=400,
        margin=dict(l=50, r=30, t=60, b=50),
    )
    return fig.to_image(format="png", engine="kaleido")


def create_hourly_chart(metrics: AnalysisMetrics) -> bytes:
    """Bar chart of posting activity by hour."""
    dist = metrics.posting_pattern.hour_distribution
    if not dist:
        return b""

    hours = list(range(24))
    counts = [dist.get(h, 0) for h in hours]

    fig = go.Figure(go.Bar(x=hours, y=counts, marker_color="#34A853"))
    fig.update_layout(
        title="Posting Activity by Hour (UTC)",
        xaxis_title="Hour",
        yaxis_title="Posts",
        template="plotly_white",
        width=700,
        height=350,
        margin=dict(l=50, r=30, t=60, b=50),
    )
    return fig.to_image(format="png", engine="kaleido")


def create_weekday_chart(metrics: AnalysisMetrics) -> bytes:
    """Bar chart of posting activity by weekday."""
    dist = metrics.posting_pattern.weekday_distribution
    if not dist:
        return b""

    labels = WEEKDAY_NAMES
    counts = [dist.get(i, 0) for i in range(7)]

    fig = go.Figure(go.Bar(x=labels, y=counts, marker_color="#FBBC04"))
    fig.update_layout(
        title="Posting Activity by Weekday",
        xaxis_title="Day",
        yaxis_title="Posts",
        template="plotly_white",
        width=700,
        height=350,
        margin=dict(l=50, r=30, t=60, b=50),
    )
    return fig.to_image(format="png", engine="kaleido")


def create_content_mix_chart(metrics: AnalysisMetrics) -> bytes:
    """Pie chart of content type distribution."""
    mix = metrics.content_mix
    labels = ["Text", "Photo", "Video", "Document", "Other"]
    values = [mix.pct_text_only, mix.pct_photo, mix.pct_video, mix.pct_document, mix.pct_other]

    # Filter out zero slices
    filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
    if not filtered:
        return b""

    fig = go.Figure(
        go.Pie(
            labels=[f[0] for f in filtered],
            values=[f[1] for f in filtered],
            hole=0.4,
            marker_colors=["#229ED9", "#34A853", "#EA4335", "#FBBC04", "#9E9E9E"],
        )
    )
    fig.update_layout(
        title="Content Mix",
        template="plotly_white",
        width=500,
        height=400,
        margin=dict(l=30, r=30, t=60, b=30),
    )
    return fig.to_image(format="png", engine="kaleido")


def generate_all_charts(metrics: AnalysisMetrics, analysis_id: int) -> dict[str, str]:
    """Generate all charts and save to disk. Returns {name: file_path}."""
    chart_dir = REPORTS_DIR / f"analysis_{analysis_id}" / "charts"
    _ensure_dir(chart_dir)

    charts: dict[str, str] = {}
    generators = {
        "views": create_views_chart,
        "hourly": create_hourly_chart,
        "weekday": create_weekday_chart,
        "content_mix": create_content_mix_chart,
    }

    for name, gen_fn in generators.items():
        png_data = gen_fn(metrics)
        if png_data:
            path = chart_dir / f"{name}.png"
            path.write_bytes(png_data)
            charts[name] = str(path)

    return charts
