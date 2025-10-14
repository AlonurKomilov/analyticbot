"""
Core Dashboard Services - Business Logic Layer

Real-time analytics dashboards with:
- Interactive visualizations (Plotly)
- Live data streaming
- Multiple chart types (line, bar, scatter, heatmap, etc.)
- Web-based interfaces (Dash framework)
- Dashboard factory patterns
"""

from core.services.bot.dashboard.dashboard_service import (
    DashboardFactory,
    RealTimeDashboard,
    VisualizationEngine,
    create_dashboard,
    create_visualization_engine,
    health_check,
)

__all__ = [
    "VisualizationEngine",
    "RealTimeDashboard",
    "DashboardFactory",
    "create_visualization_engine",
    "create_dashboard",
    "health_check",
]
