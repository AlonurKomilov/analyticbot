/**
 * Important Health Checks
 * Should pass, but degraded mode possible if they fail
 */

import { HealthCheck, CheckCategory, CheckStatus } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://api.analyticbot.org';

/**
 * Check 4: Dashboard Data Endpoint
 */
export async function checkDashboardEndpoint(signal: AbortSignal): Promise<HealthCheck> {
    const check = new HealthCheck(
        'Dashboard Data Endpoint',
        CheckCategory.IMPORTANT,
        'Verify main dashboard data endpoint exists'
    );

    try {
        // Using correct /analytics/historical/overview/{channel_id} path
        const response = await fetch(`${API_BASE_URL}/analytics/historical/overview/demo_channel`, {
            method: 'GET',
            signal
        });

        if (response.status === 401 || response.status === 403) {
            // Expected - endpoint exists but requires auth
            check.passed({
                endpoint: 'analytics/historical/overview',
                accessible: true,
                requiresAuth: true
            });
        } else if (response.ok) {
            check.passed({
                endpoint: 'analytics/historical/overview',
                accessible: true,
                requiresAuth: false
            });
        } else if (response.status === 404) {
            check.failed('Dashboard endpoint not found', { status: 404 });
        } else {
            check.degraded(`Unexpected status: ${response.status}`, { status: response.status });
        }
    } catch (error: any) {
        check.failed(error.message);
    }

    return check;
}

/**
 * Check 5: Analytics Endpoints
 */
export async function checkAnalyticsEndpoints(signal: AbortSignal): Promise<HealthCheck> {
    const check = new HealthCheck(
        'Analytics Endpoints',
        CheckCategory.IMPORTANT,
        'Verify analytics endpoints are accessible'
    );

    const endpoints = [
        '/analytics/content/',
        '/analytics/audience/',
        '/analytics/predictive/best-times/demo_channel'
    ];

    try {
        const results = await Promise.all(
            endpoints.map(async endpoint => {
                try {
                    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                        method: 'GET',
                        signal
                    });
                    return {
                        endpoint,
                        status: response.status,
                        accessible: response.status !== 404
                    };
                } catch (error: any) {
                    return {
                        endpoint,
                        status: 'error',
                        accessible: false,
                        error: error.message
                    };
                }
            })
        );

        const accessible = results.filter(r => r.accessible);
        const notFound = results.filter(r => r.status === 404);

        if (notFound.length === endpoints.length) {
            check.failed('No analytics endpoints found', { results });
        } else if (notFound.length > 0) {
            check.degraded(`${notFound.length}/${endpoints.length} endpoints missing`, { results });
        } else {
            check.passed({
                totalEndpoints: endpoints.length,
                accessible: accessible.length,
                results
            });
        }
    } catch (error: any) {
        check.failed(error.message);
    }

    return check;
}

/**
 * Check 6: API Response Time
 */
export async function checkAPIPerformance(signal: AbortSignal): Promise<HealthCheck> {
    const check = new HealthCheck(
        'API Performance',
        CheckCategory.IMPORTANT,
        'Measure API response time for performance baseline'
    );

    try {
        const startTime = performance.now();
        const response = await fetch(`${API_BASE_URL}/health/`, {
            method: 'GET',
            signal
        });
        const responseTime = performance.now() - startTime;

        if (response.ok) {
            const status = responseTime < 1000 ? CheckStatus.PASSED :
                          responseTime < 3000 ? CheckStatus.DEGRADED :
                          CheckStatus.FAILED;

            const details = {
                responseTimeMs: Math.round(responseTime),
                threshold: {
                    excellent: '< 1000ms',
                    acceptable: '< 3000ms',
                    slow: '> 3000ms'
                }
            };

            if (status === CheckStatus.PASSED) {
                check.passed(details);
            } else if (status === CheckStatus.DEGRADED) {
                check.degraded(`Slow response: ${Math.round(responseTime)}ms`, details);
            } else {
                check.failed(`Very slow response: ${Math.round(responseTime)}ms`, details);
            }
        } else {
            check.failed(`HTTP ${response.status}`);
        }
    } catch (error: any) {
        check.failed(error.message);
    }

    return check;
}
