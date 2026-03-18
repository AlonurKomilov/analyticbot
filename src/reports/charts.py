"""Chart generation for reports — matplotlib-based, saved as PNG"""

from __future__ import annotations

import io
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.analyzer.metrics import AnalysisMetrics

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "data/reports"))
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def create_views_chart(metrics: AnalysisMetrics) -> bytes:
    """Bar chart of top posts by views."""
    top = metrics.top_posts_by_views[:10]
    if not top:
        return b""

    labels = [f"#{p.message_id}" for p in top]
    values = [p.views for p in top]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(labels, values, color="#229ED9")
    ax.set_title("Top Posts by Views", fontsize=14)
    ax.set_xlabel("Post")
    ax.set_ylabel("Views")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def create_hourly_chart(metrics: AnalysisMetrics) -> bytes:
    """Bar chart of posting activity by hour."""
    dist = metrics.posting_pattern.hour_distribution
    if not dist:
        return b""

    hours = list(range(24))
    counts = [dist.get(h, 0) for h in hours]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(hours, counts, color="#34A853")
    ax.set_title("Posting Activity by Hour (UTC)", fontsize=14)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Posts")
    ax.set_xticks(range(0, 24, 2))
    fig.tight_layout()
    return _fig_to_bytes(fig)


def create_weekday_chart(metrics: AnalysisMetrics) -> bytes:
    """Bar chart of posting activity by weekday."""
    dist = metrics.posting_pattern.weekday_distribution
    if not dist:
        return b""

    counts = [dist.get(i, 0) for i in range(7)]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(WEEKDAY_NAMES, counts, color="#FBBC04")
    ax.set_title("Posting Activity by Weekday", fontsize=14)
    ax.set_xlabel("Day")
    ax.set_ylabel("Posts")
    fig.tight_layout()
    return _fig_to_bytes(fig)


def create_content_mix_chart(metrics: AnalysisMetrics) -> bytes:
    """Pie chart of content type distribution."""
    mix = metrics.content_mix
    labels = ["Text", "Photo", "Video", "Document", "Other"]
    values = [mix.pct_text_only, mix.pct_photo, mix.pct_video, mix.pct_document, mix.pct_other]

    filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
    if not filtered:
        return b""

    colors = ["#229ED9", "#34A853", "#EA4335", "#FBBC04", "#9E9E9E"]
    color_map = dict(zip(labels, colors))

    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(
        [f[1] for f in filtered],
        labels=[f[0] for f in filtered],
        colors=[color_map[f[0]] for f in filtered],
        autopct="%1.0f%%",
        pctdistance=0.75,
        wedgeprops={"width": 0.4},
    )
    ax.set_title("Content Mix", fontsize=14)
    fig.tight_layout()
    return _fig_to_bytes(fig)


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
