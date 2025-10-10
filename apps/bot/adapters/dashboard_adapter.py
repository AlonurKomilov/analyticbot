"""
Bot Dashboard Adapter - Thin layer adapting core dashboard to bot interface
Follows Clean Architecture: Apps layer adapter wrapping Core business logic
"""

import logging
from typing import Any

import pandas as pd

from core.services.dashboard import RealTimeDashboard, VisualizationEngine

logger = logging.getLogger(__name__)


class BotDashboardAdapter:
    """
    Thin adapter for bot layer - translates bot requests to core dashboard service
    This is how apps layer should work: thin translation, no business logic
    """

    def __init__(
        self,
        visualization_engine: VisualizationEngine | None = None,
        dashboard: RealTimeDashboard | None = None,
    ):
        """
        Initialize bot dashboard adapter

        Args:
            visualization_engine: Core visualization engine
            dashboard: Optional real-time dashboard instance
        """
        self.visualization_engine = visualization_engine
        self.dashboard = dashboard

    async def create_line_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str | None = None,
        theme: str = "default",
    ) -> dict[str, Any]:
        """
        Create a line chart visualization

        Args:
            df: Pandas DataFrame with data
            x_column: X-axis column name
            y_column: Y-axis column name
            title: Optional chart title
            theme: Chart theme (default, dark, light)

        Returns:
            Chart specification dictionary
        """
        try:
            if not self.visualization_engine:
                return {"success": False, "error": "Visualization engine not initialized"}

            return await self.visualization_engine.create_line_chart(
                df, x_column, y_column, title, theme
            )
        except Exception as e:
            logger.error(f"Failed to create line chart: {e}")
            return {"success": False, "error": str(e)}

    async def create_bar_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str | None = None,
        orientation: str = "vertical",
    ) -> dict[str, Any]:
        """
        Create a bar chart visualization

        Args:
            df: Pandas DataFrame with data
            x_column: X-axis column name
            y_column: Y-axis column name
            title: Optional chart title
            orientation: Chart orientation (vertical or horizontal)

        Returns:
            Chart specification dictionary
        """
        try:
            if not self.visualization_engine:
                return {"success": False, "error": "Visualization engine not initialized"}

            return await self.visualization_engine.create_bar_chart(
                df, x_column, y_column, title, orientation
            )
        except Exception as e:
            logger.error(f"Failed to create bar chart: {e}")
            return {"success": False, "error": str(e)}

    async def create_scatter_plot(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str | None = None,
        color_column: str | None = None,
        size_column: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a scatter plot visualization

        Args:
            df: Pandas DataFrame with data
            x_column: X-axis column name
            y_column: Y-axis column name
            title: Optional chart title
            color_column: Optional color grouping column
            size_column: Optional size column

        Returns:
            Chart specification dictionary
        """
        try:
            if not self.visualization_engine:
                return {"success": False, "error": "Visualization engine not initialized"}

            return await self.visualization_engine.create_scatter_plot(
                df, x_column, y_column, title, color_column, size_column
            )
        except Exception as e:
            logger.error(f"Failed to create scatter plot: {e}")
            return {"success": False, "error": str(e)}

    async def create_heatmap(
        self, df: pd.DataFrame, title: str | None = None
    ) -> dict[str, Any]:
        """
        Create a heatmap visualization

        Args:
            df: Pandas DataFrame with data
            title: Optional chart title

        Returns:
            Chart specification dictionary
        """
        try:
            if not self.visualization_engine:
                return {"success": False, "error": "Visualization engine not initialized"}

            return await self.visualization_engine.create_heatmap(df, title)
        except Exception as e:
            logger.error(f"Failed to create heatmap: {e}")
            return {"success": False, "error": str(e)}

    async def start_dashboard(self, port: int = 8050) -> dict[str, Any]:
        """
        Start the real-time dashboard server

        Args:
            port: Port number for dashboard server

        Returns:
            Result dictionary
        """
        try:
            if not self.dashboard:
                return {"success": False, "error": "Dashboard not initialized"}

            await self.dashboard.start_dashboard()
            return {
                "success": True,
                "port": port,
                "url": f"http://localhost:{port}",
                "status": "running",
            }
        except Exception as e:
            logger.error(f"Failed to start dashboard: {e}")
            return {"success": False, "error": str(e)}

    async def stop_dashboard(self) -> dict[str, Any]:
        """
        Stop the real-time dashboard server

        Returns:
            Result dictionary
        """
        try:
            if not self.dashboard:
                return {"success": False, "error": "Dashboard not initialized"}

            await self.dashboard.stop_dashboard()
            return {"success": True, "status": "stopped"}
        except Exception as e:
            logger.error(f"Failed to stop dashboard: {e}")
            return {"success": False, "error": str(e)}

    def get_visualization_engine(self) -> VisualizationEngine | None:
        """
        Get the underlying visualization engine for advanced operations

        Returns:
            Core visualization engine
        """
        return self.visualization_engine

    def get_dashboard(self) -> RealTimeDashboard | None:
        """
        Get the underlying dashboard for advanced operations

        Returns:
            Core real-time dashboard
        """
        return self.dashboard
