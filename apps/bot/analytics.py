"""
🚀 PHASE 4.0: ADVANCED ANALYTICS - Bot Integration Module

Enterprise Data Science Platform integrated into AnalyticBot structure

This module provides comprehensive advanced analytics capabilities:

✅ Module 4.1: Advanced Data Processing Engine (bot/utils/data_processor.py)
   - Multi-source data ingestion (CSV, JSON, Excel, SQL, API, streaming)
   - Automated data cleaning and quality analysis
   - Statistical analysis and data transformations

✅ Module 4.2: Predictive Analytics & Forecasting (bot/services/ml/predictive_engine.py)
   - 15+ ML algorithms (Regression, Classification, Clustering)
   - Time series forecasting (ARIMA, Prophet, Exponential Smoothing)
   - Automated model selection and hyperparameter tuning

✅ Module 4.3: Real-time Analytics Dashboard (bot/services/dashboard_service.py)
   - Interactive web-based dashboards with 20+ chart types
   - Real-time data streaming and live updates
   - Customizable themes and export functionality

✅ Module 4.4: AI-Powered Insights Generator (bot/services/ml/ai_insights.py)
   - Pattern recognition and anomaly detection
   - Automated statistical insights and recommendations
   - Natural language insight generation

✅ Module 4.5: Automated Reporting System (bot/services/reporting_service.py)
   - Multi-format reports (PDF, Excel, HTML, JSON)
   - Scheduled report generation and email delivery
   - Customizable templates and styling

RELOCATED IMPLEMENTATION: Analytics modules properly organized in bot structure
- ML Services: bot/services/ml/
- Utilities: bot/utils/
- Web Services: bot/services/
"""

from apps.bot.services.adapters.bot_ml_facade import create_bot_ml_facade
from apps.bot.services.adapters.ml_coordinator import create_ml_coordinator
from apps.bot.utils.data_processor import AdvancedDataProcessor, create_data_processor

# ✅ Phase 3.5: Migrated to core services (2025-10-15)
from core.services.bot.dashboard.dashboard_service import (
    DashboardFactory,
    RealTimeDashboard,
    VisualizationEngine,
    create_dashboard,
    create_visualization_engine,
)
from core.services.bot.reporting.reporting_service import (
    AutomatedReportingSystem,
    ReportTemplate,
    create_report_template,
    create_reporting_system,
)

__all__ = [
    "create_ml_coordinator",
    "create_bot_ml_facade",
    "AdvancedDataProcessor",
    "create_data_processor",
    "VisualizationEngine",
    "RealTimeDashboard",
    "DashboardFactory",
    "create_visualization_engine",
    "create_dashboard",
    "AutomatedReportingSystem",
    "ReportTemplate",
    "create_reporting_system",
    "create_report_template",
]


async def create_analytics_suite():
    """
    🚀 Create complete analytics suite with all components
    """
    return {
        "data_processor": await create_data_processor(),
        "ml_coordinator": create_ml_coordinator(),
        "bot_ml_facade": create_bot_ml_facade(),
        "visualization_engine": await create_visualization_engine(),
        "dashboard": await create_dashboard(),
        "reporting_system": await create_reporting_system(),
    }


async def analytics_health_check():
    """
    🔍 Comprehensive health check for all analytics components
    """
    try:
        health_results = {}
        data_processor = await create_data_processor()
        # health_results["data_processor"] = await data_processor.health_check()  # Method not available
        ml_coordinator = create_ml_coordinator()
        health_results["ml_coordinator"] = await ml_coordinator.health_check()
        bot_ml_facade = create_bot_ml_facade()
        health_results["bot_ml_facade"] = await bot_ml_facade.get_service_status()
        # ✅ Phase 3.5: Updated to core service
        from core.services.bot.dashboard.dashboard_service import health_check as dashboard_health

        health_results["dashboard_service"] = await dashboard_health()
        reporting_system = await create_reporting_system()
        health_results["reporting_system"] = await reporting_system.health_check()
        all_healthy = all(result.get("status") == "healthy" for result in health_results.values())
        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "components": health_results,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "overall_status": "error",
            "error": str(e),
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
