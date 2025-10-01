"""
Chart Service - Clean Architecture Implementation
Provides chart rendering services for the apps layer, abstracting away infrastructure details
"""

import logging
from typing import Any, Dict, Optional

from apps.shared.protocols import ChartServiceProtocol

logger = logging.getLogger(__name__)


class ChartRenderingError(Exception):
    """Raised when chart rendering fails"""
    pass


class ChartService(ChartServiceProtocol):
    """
    Chart service implementation that abstracts chart rendering infrastructure
    
    This service provides a clean interface for chart generation while isolating
    the apps layer from infrastructure dependencies like matplotlib.
    """
    
    def __init__(self, chart_renderer=None):
        self._renderer: Optional[Any] = chart_renderer
        self._initialized = chart_renderer is not None
    
    def _initialize_renderer(self) -> Any:
        """Lazy initialization of chart renderer"""
        if self._renderer is None:
            try:
                # Chart renderer should be injected via DI, but provide fallback
                # This fallback will be removed once DI is properly configured
                logger.warning("Chart renderer not injected, using fallback import")
                from infra.rendering.charts import ChartRenderer, MATPLOTLIB_AVAILABLE
                
                if not MATPLOTLIB_AVAILABLE:
                    raise ChartRenderingError("Matplotlib not available for chart rendering")
                
                self._renderer = ChartRenderer()
                self._initialized = True
                logger.info("Chart renderer initialized via fallback")
                
            except ImportError as e:
                logger.error(f"Failed to import chart renderer: {e}")
                raise ChartRenderingError("Chart rendering infrastructure not available")
            except Exception as e:
                logger.error(f"Failed to initialize chart renderer: {e}")
                raise ChartRenderingError(f"Chart renderer initialization failed: {e}")
        
        return self._renderer
    
    def is_available(self) -> bool:
        """Check if chart rendering is available"""
        try:
            self._initialize_renderer()
            return True
        except ChartRenderingError:
            return False
    
    def render_growth_chart(self, data: Dict[str, Any]) -> bytes:
        """
        Render growth data as PNG chart
        
        Args:
            data: Growth analytics data
            
        Returns:
            PNG chart as bytes
            
        Raises:
            ChartRenderingError: If rendering fails
        """
        try:
            renderer = self._initialize_renderer()
            return renderer.render_growth_chart(data)
        except Exception as e:
            logger.error(f"Growth chart rendering failed: {e}")
            raise ChartRenderingError(f"Failed to render growth chart: {e}")
    
    def render_reach_chart(self, data: Dict[str, Any]) -> bytes:
        """
        Render reach data as PNG chart
        
        Args:
            data: Reach analytics data
            
        Returns:
            PNG chart as bytes
            
        Raises:
            ChartRenderingError: If rendering fails
        """
        try:
            renderer = self._initialize_renderer()
            return renderer.render_reach_chart(data)
        except Exception as e:
            logger.error(f"Reach chart rendering failed: {e}")
            raise ChartRenderingError(f"Failed to render reach chart: {e}")
    
    def render_sources_chart(self, data: Dict[str, Any]) -> bytes:
        """
        Render sources data as PNG chart
        
        Args:
            data: Sources analytics data
            
        Returns:
            PNG chart as bytes
            
        Raises:
            ChartRenderingError: If rendering fails
        """
        try:
            renderer = self._initialize_renderer()
            return renderer.render_sources_chart(data)
        except Exception as e:
            logger.error(f"Sources chart rendering failed: {e}")
            raise ChartRenderingError(f"Failed to render sources chart: {e}")
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported chart formats"""
        if self.is_available():
            return ["png"]
        return []
    
    def get_supported_chart_types(self) -> list[str]:
        """Get list of supported chart types"""
        if self.is_available():
            return ["growth", "reach", "sources"]
        return []


# Factory function for dependency injection
def create_chart_service() -> ChartService:
    """Create and return a chart service instance"""
    return ChartService()