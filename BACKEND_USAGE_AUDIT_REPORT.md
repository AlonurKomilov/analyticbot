# Backend Service and API Endpoint Usage Audit Report
============================================================

## Summary
- **Total API Endpoints Found:** 0
- **Frontend API Calls Found:** 35
- **Unused API Endpoints:** 0
- **Total Service Classes:** 42
- **Unused Service Classes:** 19

## Part 1: All Discovered API Endpoints


## Part 2: Frontend API Calls

- `${this.baseURL}/api/v1/media/upload-direct`
- `/api/mobile/v1/analytics/quick`
- `/api/v1/content-protection/detection/scan`
- `/api/v1/media/storage-files?limit=${limit}&offset=${offset}`
- `/api/v1/media/upload-direct`
- `/api/v1/superadmin/audit-logs?limit=50`
- `/api/v1/superadmin/stats`
- `/api/v1/superadmin/users/${suspendDialog.user.id}/suspend`
- `/api/v1/superadmin/users/${userId}/reactivate`
- `/api/v1/superadmin/users?limit=100`
- `/api/v2/analytics/advanced/alerts/check/${channelId}`
- `/api/v2/analytics/advanced/dashboard/${channelId}?${params}`
- `/api/v2/analytics/advanced/metrics/real-time/${channelId}`
- `/api/v2/analytics/advanced/performance/score/${channelId}?period=${period}`
- `/api/v2/analytics/advanced/recommendations/${channelId}`
- `/api/v2/analytics/channel-data`
- `/api/v2/analytics/channels/${channelId}/growth?period=${period}`
- `/api/v2/analytics/channels/${channelId}/growth?period=30`
- `/api/v2/analytics/channels/${channelId}/overview`
- `/api/v2/analytics/channels/${channelId}/overview?period=${period}`
- `/api/v2/analytics/channels/${channelId}/overview?period=30`
- `/api/v2/analytics/channels/${channelId}/reach?period=${period}`
- `/api/v2/analytics/channels/${channelId}/reach?period=30`
- `/api/v2/analytics/channels/${channelId}/top-posts?period=${period}`
- `/api/v2/analytics/channels/${channelId}/trending?period=${period}`
- `/api/v2/analytics/channels/${channelId}/trending?period=7`
- `/api/v2/analytics/metrics/performance`
- `/api/v2/analytics/trends/top-posts`
- `/api/v2/exports/csv/${type}/${channelId}?period=${period}`
- `/api/v2/exports/png/${type}/${channelId}?period=${period}`
- `/api/v2/exports/status`
- `/api/v2/share/create/${type}/${channelId}`
- `/api/v2/share/info/${token}`
- `/api/v2/share/report/${token}`
- `/api/v2/share/revoke/${token}`

## Part 3: Unused API Endpoints

🎉 **No unused API endpoints found!** All endpoints are being used by the frontend.

## Part 4: Backend Service Analysis

### All Service Classes
- `EnhancedDeliveryService` - core/services/enhanced_delivery_service.py - ✅ USED
  - Used in: apps/bot/services/scheduler_service.py
- `SuperAdminService` - core/services/superadmin_service.py - ✅ USED
  - Used in: apps/api/superadmin_routes.py
- `AnalyticsFusionService` - core/services/analytics_fusion_service.py - ✅ USED
  - Used in: apps/api/di_analytics_v2.py
  - Used in: apps/api/routers/analytics_v2.py
- `SubscriptionService` - apps/bot/services/subscription_service.py - ✅ USED
  - Used in: apps/bot/container.py
  - Used in: apps/bot/handlers/user_handlers.py
  - Used in: apps/bot/services/__init__.py
- `AnalyticsService` - apps/bot/services/analytics_service.py - ✅ USED
  - Used in: apps/bot/container.py
  - Used in: apps/api/routers/analytics_router.py
  - Used in: apps/bot/handlers/admin_handlers.py
  - ... and 2 more files
- `PaymentGatewayAdapter` - apps/bot/services/payment_service.py - ❌ UNUSED
- `StripeAdapter` - apps/bot/services/payment_service.py - ❌ UNUSED
- `PaymeAdapter` - apps/bot/services/payment_service.py - ❌ UNUSED
- `ClickAdapter` - apps/bot/services/payment_service.py - ❌ UNUSED
- `PaymentService` - apps/bot/services/payment_service.py - ✅ USED
  - Used in: apps/bot/api/payment_routes.py
- `WatermarkConfig` - apps/bot/services/content_protection.py - ✅ USED
  - Used in: apps/bot/handlers/content_protection.py
  - Used in: apps/bot/api/content_protection_routes.py
- `ContentProtectionService` - apps/bot/services/content_protection.py - ✅ USED
  - Used in: apps/bot/handlers/content_protection.py
  - Used in: apps/bot/api/content_protection_routes.py
- `PremiumEmojiService` - apps/bot/services/content_protection.py - ✅ USED
  - Used in: apps/bot/handlers/content_protection.py
- `ReportTemplate` - apps/bot/services/reporting_service.py - ❌ UNUSED
- `AutomatedReportingSystem` - apps/bot/services/reporting_service.py - ❌ UNUSED
- `PrometheusService` - apps/bot/services/prometheus_service.py - ❌ UNUSED
- `PrometheusMiddleware` - apps/bot/services/prometheus_service.py - ❌ UNUSED
- `VisualizationEngine` - apps/bot/services/dashboard_service.py - ❌ UNUSED
- `RealTimeDashboard` - apps/bot/services/dashboard_service.py - ❌ UNUSED
- `DashboardFactory` - apps/bot/services/dashboard_service.py - ✅ USED
  - Used in: apps/api/routers/analytics_router.py
- `dbc` - apps/bot/services/dashboard_service.py - ❌ UNUSED
- `html` - apps/bot/services/dashboard_service.py - ✅ USED
  - Used in: apps/bot/services/reporting_service.py
- `dcc` - apps/bot/services/dashboard_service.py - ❌ UNUSED
- `dash` - apps/bot/services/dashboard_service.py - ✅ USED
  - Used in: apps/bot/analytics.py
  - Used in: apps/api/routers/analytics_router.py
  - Used in: apps/bot/handlers/user_handlers.py
- `GuardService` - apps/bot/services/guard_service.py - ✅ USED
  - Used in: apps/bot/container.py
  - Used in: apps/bot/handlers/admin_handlers.py
  - Used in: apps/bot/services/__init__.py
- `SchedulerService` - apps/bot/services/scheduler_service.py - ✅ USED
  - Used in: apps/bot/container.py
  - Used in: apps/bot/handlers/admin_handlers.py
  - Used in: apps/bot/services/__init__.py
- `StandaloneContentAnalysis` - apps/bot/services/ml/standalone_content_optimizer.py - ❌ UNUSED
- `StandaloneContentOptimizer` - apps/bot/services/ml/standalone_content_optimizer.py - ❌ UNUSED
- `PredictiveAnalyticsEngine` - apps/bot/services/ml/predictive_engine.py - ✅ USED
  - Used in: apps/api/routers/analytics_router.py
- `ContentAnalysis` - apps/bot/services/ml/content_optimizer.py - ✅ USED
  - Used in: apps/bot/services/ml/standalone_content_optimizer.py
  - Used in: apps/bot/services/ml/engagement_analyzer.py
- `HashtagSuggestion` - apps/bot/services/ml/content_optimizer.py - ❌ UNUSED
- `ContentOptimizer` - apps/bot/services/ml/content_optimizer.py - ✅ USED
  - Used in: apps/bot/container.py
  - Used in: apps/bot/services/ml/__init__.py
  - Used in: apps/bot/services/ml/engagement_analyzer.py
- `UserBehaviorData` - apps/bot/services/ml/churn_predictor.py - ❌ UNUSED
- `ChurnRiskAssessment` - apps/bot/services/ml/churn_predictor.py - ❌ UNUSED
- `ChurnPredictor` - apps/bot/services/ml/churn_predictor.py - ✅ USED
  - Used in: apps/bot/container.py
  - Used in: apps/bot/services/ml/__init__.py
  - Used in: apps/bot/services/ml/engagement_analyzer.py
- `AIInsightsGenerator` - apps/bot/services/ml/ai_insights.py - ✅ USED
  - Used in: apps/api/routers/analytics_router.py
- `EngagementInsight` - apps/bot/services/ml/engagement_analyzer.py - ❌ UNUSED
- `PerformanceReport` - apps/bot/services/ml/engagement_analyzer.py - ❌ UNUSED
- `EngagementAnalyzer` - apps/bot/services/ml/engagement_analyzer.py - ✅ USED
  - Used in: apps/bot/container.py
  - Used in: apps/bot/services/ml/__init__.py
- `PredictionResult` - apps/bot/services/ml/prediction_service.py - ✅ USED
  - Used in: apps/bot/services/ml/engagement_analyzer.py
- `ContentMetrics` - apps/bot/services/ml/prediction_service.py - ✅ USED
  - Used in: apps/bot/services/ml/engagement_analyzer.py
- `PredictionService` - apps/bot/services/ml/prediction_service.py - ✅ USED
  - Used in: apps/bot/container.py
  - Used in: apps/bot/services/ml/__init__.py
  - Used in: apps/bot/services/ml/engagement_analyzer.py

### Potentially Unused Service Classes
- `PaymentGatewayAdapter` - apps/bot/services/payment_service.py
  - Methods: provider_name, verify_webhook_signature
- `StripeAdapter` - apps/bot/services/payment_service.py
  - Methods: __init__, provider_name, verify_webhook_signature
- `PaymeAdapter` - apps/bot/services/payment_service.py
  - Methods: __init__, provider_name, verify_webhook_signature
- `ClickAdapter` - apps/bot/services/payment_service.py
  - Methods: __init__, provider_name, verify_webhook_signature
- `ReportTemplate` - apps/bot/services/reporting_service.py
  - Methods: __init__, add_section, set_styling
- `AutomatedReportingSystem` - apps/bot/services/reporting_service.py
  - Methods: __init__, _generate_data_summary, _start_scheduler, configure_email, get_report_history, get_scheduled_reports
- `PrometheusService` - apps/bot/services/prometheus_service.py
  - Methods: __init__, _setup_metrics, record_http_request, record_telegram_api_request, record_telegram_update, record_database_query, update_database_connections, record_celery_task, update_celery_workers, update_business_metrics, record_post_sent, record_post_views_update, update_system_metrics, update_health_check, set_app_info, get_metrics, get_content_type
- `PrometheusMiddleware` - apps/bot/services/prometheus_service.py
  - Methods: 
- `VisualizationEngine` - apps/bot/services/dashboard_service.py
  - Methods: __init__
- `RealTimeDashboard` - apps/bot/services/dashboard_service.py
  - Methods: __init__, _setup_layout, _setup_callbacks
- `dbc` - apps/bot/services/dashboard_service.py
  - Methods: themes
- `dcc` - apps/bot/services/dashboard_service.py
  - Methods: Upload, Dropdown, Graph, Store
- `StandaloneContentAnalysis` - apps/bot/services/ml/standalone_content_optimizer.py
  - Methods: 
- `StandaloneContentOptimizer` - apps/bot/services/ml/standalone_content_optimizer.py
  - Methods: __init__, _analyze_sentiment, _calculate_readability, _calculate_overall_score, _score_content_length, _generate_optimization_tips, _suggest_hashtags
- `HashtagSuggestion` - apps/bot/services/ml/content_optimizer.py
  - Methods: 
- `UserBehaviorData` - apps/bot/services/ml/churn_predictor.py
  - Methods: 
- `ChurnRiskAssessment` - apps/bot/services/ml/churn_predictor.py
  - Methods: 
- `EngagementInsight` - apps/bot/services/ml/engagement_analyzer.py
  - Methods: 
- `PerformanceReport` - apps/bot/services/ml/engagement_analyzer.py
  - Methods: 

## Recommendations

### Unused Service Classes
Consider removing the following unused service classes:
- PaymentGatewayAdapter
- StripeAdapter
- PaymeAdapter
- ClickAdapter
- ReportTemplate
- AutomatedReportingSystem
- PrometheusService
- PrometheusMiddleware
- VisualizationEngine
- RealTimeDashboard
- dbc
- dcc
- StandaloneContentAnalysis
- StandaloneContentOptimizer
- HashtagSuggestion
- UserBehaviorData
- ChurnRiskAssessment
- EngagementInsight
- PerformanceReport
