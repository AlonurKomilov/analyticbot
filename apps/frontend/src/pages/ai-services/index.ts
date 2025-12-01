/**
 * AI Services Pages - Barrel Export
 * 
 * These are PAGE components for the /services/* routes.
 * The actual service LOGIC is in features/ai-services/services/
 */

// Layout
export { default as ServicesLayout } from './ServicesLayout';

// AI Service Pages
export { default as ChurnPredictorPage } from './ChurnPredictorPage';
export { default as ContentOptimizerPage } from './ContentOptimizerPage';
export { default as PredictiveAnalyticsPage } from './PredictiveAnalyticsPage';
export { SecurityMonitoringPage } from '../../features/ai-services/SecurityMonitoring';

// Backward compatibility aliases (deprecated)
export { default as ChurnPredictorService } from './ChurnPredictorPage';
export { default as ContentOptimizerService } from './ContentOptimizerPage';
export { default as PredictiveAnalyticsService } from './PredictiveAnalyticsPage';
export { SecurityMonitoringPage as SecurityMonitoringService } from '../../features/ai-services/SecurityMonitoring';
