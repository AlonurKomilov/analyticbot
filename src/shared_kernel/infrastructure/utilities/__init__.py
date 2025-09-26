"""
Rendering Infrastructure Module
Provides chart and image generation services
"""

from .charts import MATPLOTLIB_AVAILABLE, ChartRenderer, ChartRenderingError

__all__ = ["ChartRenderer", "ChartRenderingError", "MATPLOTLIB_AVAILABLE"]
