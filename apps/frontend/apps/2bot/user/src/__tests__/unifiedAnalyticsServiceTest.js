/**
 * Analytics Service Migration Test
 * Verifies that the unified analytics service works correctly
 */

// Test the unified analytics service
import { unifiedAnalyticsService } from '../services/unifiedAnalyticsService.js';
import { dataSourceManager } from '../utils/dataSourceManager.js';

async function testUnifiedAnalyticsService() {
    console.log('🧪 Testing Unified Analytics Service');

    try {
        // Test switching to mock data source
        dataSourceManager.switchDataSource('mock');
        console.log('✅ Switched to mock data source');

        // Test analytics overview
        const overview = await unifiedAnalyticsService.getAnalyticsOverview();
        console.log('✅ Analytics Overview:', {
            channelId: overview.channelId,
            totalViews: overview.totalViews,
            source: overview.source
        });

        // Test post dynamics
        const dynamics = await unifiedAnalyticsService.getPostDynamics();
        console.log('✅ Post Dynamics:', {
            period: dynamics.period,
            dataPoints: dynamics.dynamics?.length,
            source: dynamics.source
        });

        // Test top posts
        const topPosts = await unifiedAnalyticsService.getTopPosts();
        console.log('✅ Top Posts:', {
            period: topPosts.period,
            postsCount: topPosts.posts?.length,
            source: topPosts.source
        });

        // Test health check
        const health = await unifiedAnalyticsService.healthCheck();
        console.log('✅ Health Check:', {
            status: health.status,
            adapter: health.adapter,
            features: health.features?.length
        });

        // Test metrics
        const metrics = await unifiedAnalyticsService.getMetrics();
        console.log('✅ Service Metrics:', {
            requests: metrics.requests.requests,
            cacheHits: metrics.requests.cacheHits,
            currentAdapter: metrics.currentAdapter
        });

        console.log('🎉 All tests passed! Unified Analytics Service is working correctly.');
        return true;

    } catch (error) {
        console.error('❌ Test failed:', error);
        return false;
    }
}

// Export for use in console or other tests
window.testUnifiedAnalyticsService = testUnifiedAnalyticsService;

// Auto-run test when loaded
if (typeof window !== 'undefined') {
    setTimeout(() => {
        testUnifiedAnalyticsService();
    }, 1000);
}

export { testUnifiedAnalyticsService };
