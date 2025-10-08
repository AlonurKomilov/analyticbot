/**
 * Quick test to verify all mock data imports work correctly
 * This file can be used to validate the mock data structure
 */

// Test all mock data imports
try {
    // Content Optimizer Mock Data
    const contentOptimizer = require('../contentOptimizer.js');
    console.log('✅ Content Optimizer mock data loaded successfully');
    console.log('   - Stats:', Object.keys(contentOptimizer.contentOptimizerStats));
    console.log('   - Recent optimizations:', contentOptimizer.recentOptimizations.length, 'items');

    // Churn Predictor Mock Data
    const churnPredictor = require('../churnPredictor.js');
    console.log('✅ Churn Predictor mock data loaded successfully');
    console.log('   - Stats:', Object.keys(churnPredictor.churnPredictorStats));
    console.log('   - Predictions:', churnPredictor.mockChurnPredictions.length, 'users');

    // Predictive Analytics Mock Data
    const predictiveAnalytics = require('../predictiveAnalytics.js');
    console.log('✅ Predictive Analytics mock data loaded successfully');
    console.log('   - Stats:', Object.keys(predictiveAnalytics.predictiveStats));
    console.log('   - Forecasts:', predictiveAnalytics.mockForecasts.length, 'predictions');

    // Security Monitor Mock Data
    const securityMonitor = require('../securityMonitor.js');
    console.log('✅ Security Monitor mock data loaded successfully');
    console.log('   - Stats:', Object.keys(securityMonitor.securityStats));
    console.log('   - Alerts:', securityMonitor.mockSecurityAlerts.length, 'alerts');

    console.log('\n🎉 All mock data files are properly structured and loadable!');

} catch (error) {
    console.error('❌ Error loading mock data:', error.message);
}

module.exports = {
    testMessage: 'Mock data validation complete'
};
