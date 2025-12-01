/**
 * Critical Health Checks
 * Must pass for production readiness
 */

import { HealthCheck, CheckCategory, ComponentStatus } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://api.analyticbot.org';

/**
 * Check 1: API Basic Health
 */
export async function checkAPIBasicHealth(signal: AbortSignal): Promise<HealthCheck> {
    const check = new HealthCheck(
        'API Basic Health',
        CheckCategory.CRITICAL,
        'Verify API is responding to basic health check'
    );

    try {
        const response = await fetch(`${API_BASE_URL}/health/`, {
            method: 'GET',
            signal
        });

        if (response.ok) {
            const data = await response.json();
            check.passed({
                status: data.status,
                service: data.service,
                version: data.version,
                timestamp: data.timestamp
            });
        } else {
            check.failed(`HTTP ${response.status}: ${response.statusText}`, {
                status: response.status
            });
        }
    } catch (error: any) {
        check.failed(error.message);
    }

    return check;
}

/**
 * Check 2: API Detailed Health (Components)
 */
export async function checkAPIDetailedHealth(signal: AbortSignal): Promise<HealthCheck> {
    const check = new HealthCheck(
        'API Components Health',
        CheckCategory.CRITICAL,
        'Verify all critical API components (database, cache, services)'
    );

    try {
        const response = await fetch(`${API_BASE_URL}/health/detailed`, {
            method: 'GET',
            signal
        });

        if (response.ok) {
            const data = await response.json();

            // Check each component
            const componentStatus: ComponentStatus = {};
            const failedComponents: string[] = [];

            for (const [name, component] of Object.entries(data.components || {})) {
                const comp = component as { status: string };
                componentStatus[name] = comp;
                if (comp.status === 'unhealthy') {
                    failedComponents.push(name);
                }
            }

            if (failedComponents.length > 0) {
                check.degraded(`Unhealthy components: ${failedComponents.join(', ')}`, {
                    status: data.status,
                    components: componentStatus,
                    failedComponents
                });
            } else {
                check.passed({
                    status: data.status,
                    components: componentStatus,
                    uptime: data.uptime_seconds
                });
            }
        } else {
            check.failed(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error: any) {
        check.failed(error.message);
    }

    return check;
}

/**
 * Check 3: Authentication Endpoint
 */
export async function checkAuthEndpoint(signal: AbortSignal): Promise<HealthCheck> {
    const check = new HealthCheck(
        'Authentication Service',
        CheckCategory.CRITICAL,
        'Verify authentication endpoint is accessible'
    );

    try {
        // Test with OPTIONS request (no auth required)
        const response = await fetch(`${API_BASE_URL}/auth/telegram/`, {
            method: 'OPTIONS',
            signal
        });

        if (response.ok || response.status === 405) {
            // 405 Method Not Allowed means endpoint exists but OPTIONS not supported
            check.passed({
                endpoint: 'auth/telegram/',
                accessible: true
            });
        } else if (response.status === 404) {
            check.failed('Authentication endpoint not found', { status: 404 });
        } else {
            check.degraded(`Unexpected status: ${response.status}`, { status: response.status });
        }
    } catch (error: any) {
        check.failed(error.message);
    }

    return check;
}
