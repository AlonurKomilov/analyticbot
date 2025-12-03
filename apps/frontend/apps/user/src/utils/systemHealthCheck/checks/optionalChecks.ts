/**
 * Optional Health Checks
 * Nice to have, doesn't block startup
 */

import { HealthCheck, CheckCategory } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://api.analyticbot.org';

/**
 * Check 7: Environment Configuration
 */
export async function checkEnvironmentConfig(_signal: AbortSignal): Promise<HealthCheck> {
    const check = new HealthCheck(
        'Environment Configuration',
        CheckCategory.OPTIONAL,
        'Verify environment variables and configuration'
    );

    try {
        const config = {
            apiUrl: API_BASE_URL,
            mode: import.meta.env.MODE,
            dev: import.meta.env.DEV,
            prod: import.meta.env.PROD,
            sentryConfigured: !!import.meta.env.VITE_SENTRY_DSN
        };

        const issues: string[] = [];

        if (!config.apiUrl) {
            issues.push('API URL not configured');
        }

        if (config.prod && !config.sentryConfigured) {
            issues.push('Sentry not configured in production');
        }

        if (issues.length > 0) {
            check.degraded(issues.join(', '), config);
        } else {
            check.passed(config);
        }
    } catch (error: any) {
        check.failed(error.message);
    }

    return check;
}

/**
 * Check 8: LocalStorage Availability
 */
export async function checkLocalStorage(_signal: AbortSignal): Promise<HealthCheck> {
    const check = new HealthCheck(
        'LocalStorage',
        CheckCategory.OPTIONAL,
        'Verify browser storage is available and functional'
    );

    try {
        const testKey = '__storage_test__';
        const testValue = 'test';

        localStorage.setItem(testKey, testValue);
        const retrieved = localStorage.getItem(testKey);
        localStorage.removeItem(testKey);

        if (retrieved === testValue) {
            check.passed({
                available: true,
                quota: navigator.storage ? 'supported' : 'not supported'
            });
        } else {
            check.failed('LocalStorage read/write failed');
        }
    } catch (error: any) {
        check.failed(error.message);
    }

    return check;
}
