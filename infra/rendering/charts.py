"""
Chart Rendering Service for PNG Exports
Provides server-side chart generation using matplotlib
"""

import io
import logging
from datetime import datetime

from apps.bot.clients.analytics_v2_client import (
    GrowthResponse,
    ReachResponse,
    SourcesResponse,
)

logger = logging.getLogger(__name__)

# Optional matplotlib import for chart rendering
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-interactive backend
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib not available - PNG chart rendering disabled")


class ChartRenderingError(Exception):
    """Chart rendering error"""


class ChartRenderer:
    """Service for rendering analytics charts as PNG"""

    def __init__(self, max_points: int = 2000):
        self.max_points = max_points

        if not MATPLOTLIB_AVAILABLE:
            raise ChartRenderingError(
                "Matplotlib not available. Install with: pip install matplotlib"
            )

    def _setup_figure(self, title: str, figsize: tuple[int, int] = (12, 8)) -> Figure:
        """Set up matplotlib figure with consistent styling"""
        fig = Figure(figsize=figsize, facecolor="white")
        ax = fig.add_subplot(111)

        # Styling
        ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
        ax.grid(True, alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        return fig

    def render_line_chart(
        self,
        points: list[tuple[datetime, float]],
        title: str = "Time Series Chart",
        xlabel: str = "Date",
        ylabel: str = "Value",
    ) -> bytes:
        """Render line chart from time series data"""
        if not MATPLOTLIB_AVAILABLE:
            raise ChartRenderingError("Matplotlib not available")

        if len(points) > self.max_points:
            # Sample points to prevent memory issues
            step = len(points) // self.max_points
            points = points[::step]
            logger.warning(f"Downsampled chart data from {len(points)} to {len(points)} points")

        try:
            fig = self._setup_figure(title)
            ax = fig.gca()

            # Extract dates and values
            dates = [point[0] for point in points]
            values = [point[1] for point in points]

            # Plot line
            ax.plot(dates, values, linewidth=2, color="#2E86AB", marker="o", markersize=4)

            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 10)))
            fig.autofmt_xdate()

            # Labels
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)

            # Tight layout
            fig.tight_layout()

            # Render to bytes
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)

            plt.close(fig)  # Clean up memory
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to render line chart: {e}")
            raise ChartRenderingError(f"Line chart rendering failed: {e}")

    def render_bar_chart(
        self,
        labels: list[str],
        values: list[float],
        title: str = "Bar Chart",
        xlabel: str = "Category",
        ylabel: str = "Value",
    ) -> bytes:
        """Render bar chart from categorical data"""
        if not MATPLOTLIB_AVAILABLE:
            raise ChartRenderingError("Matplotlib not available")

        if len(labels) > self.max_points:
            # Limit number of bars
            labels = labels[: self.max_points]
            values = values[: self.max_points]
            logger.warning(f"Limited bar chart to {self.max_points} bars")

        try:
            fig = self._setup_figure(title)
            ax = fig.gca()

            # Create bars
            bars = ax.bar(labels, values, color="#A23B72", alpha=0.8)

            # Add value labels on bars
            for bar, value in zip(bars, values, strict=False):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{value:.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                )

            # Rotate labels if many categories
            if len(labels) > 10:
                ax.tick_params(axis="x", rotation=45)

            # Labels
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)

            # Tight layout
            fig.tight_layout()

            # Render to bytes
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)

            plt.close(fig)  # Clean up memory
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to render bar chart: {e}")
            raise ChartRenderingError(f"Bar chart rendering failed: {e}")

    def render_pie_chart(
        self, labels: list[str], values: list[float], title: str = "Distribution Chart"
    ) -> bytes:
        """Render pie chart from categorical data"""
        if not MATPLOTLIB_AVAILABLE:
            raise ChartRenderingError("Matplotlib not available")

        try:
            fig = self._setup_figure(title, figsize=(10, 10))
            ax = fig.gca()

            # Create pie chart
            colors = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#8A2387"]
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90,
                colors=colors[: len(labels)],
            )

            # Styling
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")

            ax.axis("equal")  # Equal aspect ratio ensures circular pie

            # Tight layout
            fig.tight_layout()

            # Render to bytes
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)

            plt.close(fig)  # Clean up memory
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to render pie chart: {e}")
            raise ChartRenderingError(f"Pie chart rendering failed: {e}")

    def render_growth_chart(self, data: GrowthResponse) -> bytes:
        """Render specialized growth chart"""
        daily_growth = data.growth.daily_growth

        if not daily_growth:
            raise ChartRenderingError("No growth data available")

        # Convert to time series points
        points = []
        for day_data in daily_growth:
            try:
                date = datetime.fromisoformat(day_data["date"])
                subscribers = day_data.get("subscribers", 0)
                points.append((date, float(subscribers)))
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping invalid growth data point: {e}")

        if not points:
            raise ChartRenderingError("No valid growth data points")

        return self.render_line_chart(
            points,
            title=f"Subscriber Growth - {data.channel_id} ({data.period} days)",
            xlabel="Date",
            ylabel="Subscribers",
        )

    def render_reach_chart(self, data: ReachResponse) -> bytes:
        """Render specialized reach chart"""
        hourly_dist = data.reach.hourly_distribution

        if not hourly_dist:
            raise ChartRenderingError("No reach data available")

        # Convert to bar chart data
        hours = sorted(hourly_dist.keys(), key=int)
        views = [hourly_dist[hour] for hour in hours]
        labels = [f"{hour}:00" for hour in hours]

        return self.render_bar_chart(
            labels,
            views,
            title=f"Hourly View Distribution - {data.channel_id} ({data.period} days)",
            xlabel="Hour of Day",
            ylabel="Views",
        )

    def render_sources_chart(self, data: SourcesResponse) -> bytes:
        """Render specialized sources pie chart"""
        sources = data.sources

        # Extract source data
        source_data = [
            ("Direct", sources.direct.get("views", 0)),
            ("Forwards", sources.forwards.get("views", 0)),
            ("Links", sources.links.get("views", 0)),
            ("Search", sources.search.get("views", 0)),
        ]

        # Filter out zero values
        source_data = [(label, value) for label, value in source_data if value > 0]

        if not source_data:
            raise ChartRenderingError("No traffic sources data available")

        labels = [item[0] for item in source_data]
        values = [item[1] for item in source_data]

        return self.render_pie_chart(
            labels,
            values,
            title=f"Traffic Sources Distribution - {data.channel_id} ({data.period} days)",
        )

    @staticmethod
    def is_available() -> bool:
        """Check if chart rendering is available"""
        return MATPLOTLIB_AVAILABLE
