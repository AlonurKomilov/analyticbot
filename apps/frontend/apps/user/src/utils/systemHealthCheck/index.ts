/**
 * Production Readiness Check System
 * ==================================
 *
 * Comprehensive startup health checks that validate:
 * - API endpoint availability
 * - Critical services (database, cache, auth)
 * - System resources
 * - Security configuration
 * - Performance benchmarks
 *
 * Provides real-time feedback on system readiness before app initialization.
 *
 * Refactored: Nov 2025 - Split into modular check files
 */

import {
    CheckCategory,
    CheckStatus,
    CheckDetails,
    CheckDefinition,
    RunCheckOptions,
    HealthCheck,
    HealthReport
} from './types';

import {
    checkAPIBasicHealth,
    checkAPIDetailedHealth,
    checkAuthEndpoint,
    checkDashboardEndpoint,
    checkAnalyticsEndpoints,
    checkAPIPerformance,
    checkEnvironmentConfig,
    checkLocalStorage
} from './checks';

import { formatReadinessReport } from './formatters';

// Re-export types for backward compatibility
export {
    CheckCategory,
    CheckStatus,
    HealthCheck,
    HealthReport
} from './types';

export type { CheckDetails, RunCheckOptions, ProgressInfo } from './types';

export { formatReadinessReport } from './formatters';

/**
 * Execute a health check with timeout
 */
async function executeCheck(
    checkFn: (signal: AbortSignal) => Promise<HealthCheck>,
    timeoutMs: number = 10000
): Promise<HealthCheck> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
        const startTime = Date.now();
        const result = await checkFn(controller.signal);
        result.duration = Date.now() - startTime;
        clearTimeout(timeoutId);
        return result;
    } catch (error: any) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            const timeoutCheck = new HealthCheck('timeout', CheckCategory.CRITICAL, 'Check timed out');
            timeoutCheck.timeout();
            return timeoutCheck;
        }
        throw error;
    }
}

/**
 * Run comprehensive production readiness check
 */
export async function runProductionReadinessCheck(options: RunCheckOptions = {}): Promise<HealthReport> {
    const {
        skipOptional = false,
        timeout = 10000,
        onProgress = undefined
    } = options;

    const report = new HealthReport();

    // Define all checks
    const allChecks: CheckDefinition[] = [
        // CRITICAL - Must pass
        { fn: checkAPIBasicHealth, category: CheckCategory.CRITICAL },
        { fn: checkAPIDetailedHealth, category: CheckCategory.CRITICAL },
        { fn: checkAuthEndpoint, category: CheckCategory.CRITICAL },

        // IMPORTANT - Should pass
        { fn: checkDashboardEndpoint, category: CheckCategory.IMPORTANT },
        { fn: checkAnalyticsEndpoints, category: CheckCategory.IMPORTANT },
        { fn: checkAPIPerformance, category: CheckCategory.IMPORTANT },

        // OPTIONAL - Nice to have
        { fn: checkEnvironmentConfig, category: CheckCategory.OPTIONAL },
        { fn: checkLocalStorage, category: CheckCategory.OPTIONAL },
    ];

    // Filter checks based on options
    const checksToRun = skipOptional
        ? allChecks.filter(c => c.category !== CheckCategory.OPTIONAL)
        : allChecks;

    console.log(`🔍 Running ${checksToRun.length} production readiness checks...`);

    // Run checks sequentially with progress updates
    for (let i = 0; i < checksToRun.length; i++) {
        const { fn, category } = checksToRun[i];

        try {
            const check = await executeCheck(fn, timeout);
            report.addCheck(check);

            // Progress callback
            if (onProgress) {
                onProgress({
                    current: i + 1,
                    total: checksToRun.length,
                    check,
                    report
                });
            }

            // Log result
            const emoji = check.status === CheckStatus.PASSED ? '✅' :
                         check.status === CheckStatus.DEGRADED ? '⚠️' : '❌';
            console.log(`${emoji} ${check.name}: ${check.status} (${check.duration}ms)`);

            // Stop on critical failure unless we're gathering all results
            if (check.status === CheckStatus.FAILED && category === CheckCategory.CRITICAL) {
                console.error(`❌ Critical check failed: ${check.name}`);
                // Continue to run remaining checks to give full picture
            }
        } catch (error: any) {
            console.error(`Error running check:`, error);
        }
    }

    report.complete();

    // Add recommendations based on results
    if (report.criticalFailures.length > 0) {
        report.recommendations.push('Fix critical failures before deploying to production');
    }
    if (report.warnings.length > 0) {
        report.recommendations.push('Address warnings to ensure full functionality');
    }
    if (report.isProductionReady()) {
        report.recommendations.push('System is production ready! 🚀');
    }

    return report;
}

/**
 * Quick health check (basic only)
 */
export async function quickHealthCheck(): Promise<{ healthy: boolean; details?: CheckDetails; error?: string }> {
    try {
        const check = await executeCheck(checkAPIBasicHealth, 5000);
        return {
            healthy: check.status === CheckStatus.PASSED,
            details: check.details,
            error: check.error || undefined
        };
    } catch (error: any) {
        return {
            healthy: false,
            error: error.message
        };
    }
}

export default {
    runProductionReadinessCheck,
    quickHealthCheck,
    formatReadinessReport,
    CheckStatus,
    CheckCategory
};
