"""Chart generation for reports — matplotlib-based, saved as PNG"""

from __future__ import annotations

import io
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime

from src.analyzer.metrics import AnalysisMetrics
from src.bot.i18n import format_date_short, t

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "data/reports"))

# Consistent color palette
BLUE = "#229ED9"
GREEN = "#34A853"
YELLOW = "#FBBC04"
RED = "#EA4335"
GREY = "#9E9E9E"
DARK_TEXT = "#333333"
LIGHT_BG = "#F8F9FA"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _apply_style(ax, title: str, xlabel: str = "", ylabel: str = "") -> None:
    """Apply consistent styling to chart axes."""
    ax.set_title(title, fontsize=13, fontweight="bold", color=DARK_TEXT, pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=DARK_TEXT)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color=DARK_TEXT)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#DDDDDD")
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.tick_params(colors=DARK_TEXT, labelsize=9)
    ax.set_facecolor("white")


def _fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def create_views_trend_chart(metrics: AnalysisMetrics, lang: str = "en") -> bytes:
    """Line chart showing daily views over time."""
    trend = metrics.views_trend
    if not trend.dates or len(trend.dates) < 2:
        return b""

    dates = [datetime.strptime(d, "%Y-%m-%d") for d in trend.dates]

    fig, ax1 = plt.subplots(figsize=(7, 3.5))
    _apply_style(ax1, t("chart_views_trend", lang), ylabel=t("chart_views", lang))

    ax1.fill_between(dates, trend.daily_views, alpha=0.15, color=BLUE)
    ax1.plot(dates, trend.daily_views, color=BLUE, linewidth=2, label=t("chart_views", lang))

    # Secondary axis for post count
    ax2 = ax1.twinx()
    ax2.bar(dates, trend.daily_posts, alpha=0.3, color=GREEN, width=0.8, label=t("chart_posts", lang))
    ax2.set_ylabel(t("chart_posts", lang), fontsize=10, color=GREEN)
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["right"].set_color(GREEN)
    ax2.tick_params(axis="y", colors=GREEN, labelsize=9)

    ax1.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
    ax1.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: format_date_short(mdates.num2date(x), lang))
    )
    fig.autofmt_xdate(rotation=30)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)

    fig.tight_layout()
    return _fig_to_bytes(fig)


def create_views_chart(metrics: AnalysisMetrics, lang: str = "en") -> bytes:
    """Horizontal bar chart of top posts by views (better for readability)."""
    top = metrics.top_posts_by_views[:10]
    if not top:
        return b""

    labels = [f"#{p.message_id}" for p in reversed(top)]
    values = [p.views for p in reversed(top)]

    fig, ax = plt.subplots(figsize=(7, 4))
    _apply_style(ax, t("chart_top_posts", lang), xlabel=t("chart_views", lang))

    bars = ax.barh(labels, values, color=BLUE, height=0.6)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        if val > 0:
            ax.text(
                bar.get_width() + max(values) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,}",
                va="center",
                fontsize=8,
                color=DARK_TEXT,
            )

    fig.tight_layout()
    return _fig_to_bytes(fig)


def create_hourly_chart(metrics: AnalysisMetrics, lang: str = "en") -> bytes:
    """Bar chart of posting activity by hour."""
    dist = metrics.posting_pattern.hour_distribution
    if not dist:
        return b""

    hours = list(range(24))
    counts = [dist.get(h, 0) for h in hours]
    peak_hour = max(range(24), key=lambda h: dist.get(h, 0))

    bar_colors = [RED if h == peak_hour else GREEN for h in hours]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    _apply_style(ax, t("chart_hourly", lang), xlabel=t("chart_hour", lang), ylabel=t("chart_posts", lang))
    ax.bar(hours, counts, color=bar_colors, width=0.7)
    ax.set_xticks(range(0, 24, 2))
    fig.tight_layout()
    return _fig_to_bytes(fig)


def create_weekday_chart(metrics: AnalysisMetrics, lang: str = "en") -> bytes:
    """Bar chart of posting activity by weekday."""
    dist = metrics.posting_pattern.weekday_distribution
    if not dist:
        return b""

    counts = [dist.get(i, 0) for i in range(7)]
    peak_day = max(range(7), key=lambda i: dist.get(i, 0))
    bar_colors = [RED if i == peak_day else YELLOW for i in range(7)]
    weekday_names = [t(f"weekday_short_{i}", lang) for i in range(7)]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    _apply_style(ax, t("chart_weekday", lang), xlabel=t("chart_day", lang), ylabel=t("chart_posts", lang))
    ax.bar(weekday_names, counts, color=bar_colors, width=0.6)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def create_content_mix_chart(metrics: AnalysisMetrics, lang: str = "en") -> bytes:
    """Donut chart of content type distribution."""
    mix = metrics.content_mix
    label_keys = ["chart_text", "chart_photo", "chart_video", "chart_document", "chart_other"]
    labels = [t(k, lang) for k in label_keys]
    values = [mix.pct_text_only, mix.pct_photo, mix.pct_video, mix.pct_document, mix.pct_other]

    filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
    if not filtered:
        return b""

    chart_colors = [BLUE, GREEN, RED, YELLOW, GREY]
    color_map = dict(zip(labels, chart_colors))

    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(
        [f[1] for f in filtered],
        labels=[f[0] for f in filtered],
        colors=[color_map[f[0]] for f in filtered],
        autopct="%1.0f%%",
        pctdistance=0.75,
        wedgeprops={"width": 0.4, "edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 10, "color": DARK_TEXT},
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight("bold")
    ax.set_title(t("chart_content_mix", lang), fontsize=13, fontweight="bold", color=DARK_TEXT, pad=12)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def create_engagement_chart(metrics: AnalysisMetrics, lang: str = "en") -> bytes:
    """Bar chart comparing key engagement metrics."""
    eng = metrics.engagement
    if not metrics.total_posts:
        return b""

    labels = [t("chart_reach_label", lang), t("chart_virality_label", lang), t("chart_interaction_label", lang)]
    values = [
        eng.views_per_member * 100,  # convert to percentage for visual scale
        eng.virality_rate,
        eng.interaction_rate,
    ]

    fig, ax = plt.subplots(figsize=(6, 3.5))
    _apply_style(ax, t("chart_engagement", lang), ylabel="%")

    bar_colors = [BLUE, GREEN, YELLOW]
    bars = ax.bar(labels, values, color=bar_colors, width=0.5)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.02,
            f"{val:.2f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=DARK_TEXT,
        )

    fig.tight_layout()
    return _fig_to_bytes(fig)


def generate_all_charts(metrics: AnalysisMetrics, analysis_id: int, lang: str = "en") -> dict[str, str]:
    """Generate all charts and save to disk. Returns {name: file_path}."""
    chart_dir = REPORTS_DIR / f"analysis_{analysis_id}" / "charts"
    _ensure_dir(chart_dir)

    charts: dict[str, str] = {}
    generators = {
        "views_trend": create_views_trend_chart,
        "views": create_views_chart,
        "hourly": create_hourly_chart,
        "weekday": create_weekday_chart,
        "content_mix": create_content_mix_chart,
        "engagement": create_engagement_chart,
    }

    for name, gen_fn in generators.items():
        png_data = gen_fn(metrics, lang=lang)
        if png_data:
            path = chart_dir / f"{name}.png"
            path.write_bytes(png_data)
            charts[name] = str(path)

    return charts
