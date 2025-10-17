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
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://b2qz1m0n-11400.euw.devtunnels.ms';

/**
 * Health check categories with severity levels
 */
const CheckCategory = {
    CRITICAL: 'critical',      // Must pass for production
    IMPORTANT: 'important',    // Should pass, but degraded mode possible
    OPTIONAL: 'optional'       // Nice to have, doesn't block startup
};

/**
 * Health check result status
 */
const CheckStatus = {
    PASSED: 'passed',
    FAILED: 'failed',
    DEGRADED: 'degraded',
    SKIPPED: 'skipped',
    TIMEOUT: 'timeout'
};

/**
 * Production readiness report
 */
class ReadinessReport {
    constructor() {
        this.checks = [];
        this.startTime = Date.now();
        this.endTime = null;
        this.overallStatus = CheckStatus.PASSED;
        this.criticalFailures = [];
        this.warnings = [];
        this.recommendations = [];
    }

    addCheck(check) {
        this.checks.push(check);

        // Track failures
        if (check.status === CheckStatus.FAILED) {
            if (check.category === CheckCategory.CRITICAL) {
                this.criticalFailures.push(check);
                this.overallStatus = CheckStatus.FAILED;
            } else if (check.category === CheckCategory.IMPORTANT) {
                this.warnings.push(check);
                if (this.overallStatus === CheckStatus.PASSED) {
                    this.overallStatus = CheckStatus.DEGRADED;
                }
            }
        }
    }

    complete() {
        this.endTime = Date.now();
    }

    getDuration() {
        return this.endTime ? this.endTime - this.startTime : Date.now() - this.startTime;
    }

    isProductionReady() {
        return this.criticalFailures.length === 0;
    }

    getStatusEmoji() {
        switch (this.overallStatus) {
            case CheckStatus.PASSED: return '✅';
            case CheckStatus.DEGRADED: return '⚠️';
            case CheckStatus.FAILED: return '❌';
            default: return '❓';
        }
    }
}

/**
 * Individual health check result
 */
class HealthCheck {
    constructor(name, category, description) {
        this.name = name;
        this.category = category;
        this.description = description;
        this.status = CheckStatus.SKIPPED;
        this.error = null;
        this.details = {};
        this.duration = 0;
    }

    passed(details = {}) {
        this.status = CheckStatus.PASSED;
        this.details = details;
    }

    failed(error, details = {}) {
        this.status = CheckStatus.FAILED;
        this.error = error;
        this.details = details;
    }

    degraded(reason, details = {}) {
        this.status = CheckStatus.DEGRADED;
        this.error = reason;
        this.details = details;
    }

    timeout() {
        this.status = CheckStatus.TIMEOUT;
        this.error = 'Check timed out';
    }
}

/**
 * Execute a health check with timeout
 */
async function executeCheck(checkFn, timeoutMs = 10000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
        const startTime = Date.now();
        const result = await checkFn(controller.signal);
        result.duration = Date.now() - startTime;
        clearTimeout(timeoutId);
        return result;
    } catch (error) {
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
 * ============================================================================
 * CRITICAL CHECKS - Must pass for production readiness
 * ============================================================================
 */

/**
 * Check 1: API Basic Health
 */
async function checkAPIBasicHealth(signal) {
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
    } catch (error) {
        check.failed(error.message);
    }

    return check;
}

/**
 * Check 2: API Detailed Health (Components)
 */
async function checkAPIDetailedHealth(signal) {
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
            const componentStatus = {};
            const failedComponents = [];

            for (const [name, component] of Object.entries(data.components || {})) {
                componentStatus[name] = component.status;
                if (component.status === 'unhealthy') {
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
    } catch (error) {
        check.failed(error.message);
    }

    return check;
}

/**
 * Check 3: Authentication Endpoint
 */
async function checkAuthEndpoint(signal) {
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
    } catch (error) {
        check.failed(error.message);
    }

    return check;
}

/**
 * Check 4: Dashboard Data Endpoint
 */
async function checkDashboardEndpoint(signal) {
    const check = new HealthCheck(
        'Dashboard Data Endpoint',
        CheckCategory.IMPORTANT,
        'Verify main dashboard data endpoint exists'
    );

    try {
        // Try to access without auth - should get 401 but proves endpoint exists
        const response = await fetch(`${API_BASE_URL}/insights/dashboard/overview/demo_channel`, {
            method: 'GET',
            signal
        });

        if (response.status === 401 || response.status === 403) {
            // Expected - endpoint exists but requires auth
            check.passed({
                endpoint: 'insights/dashboard/overview',
                accessible: true,
                requiresAuth: true
            });
        } else if (response.ok) {
            check.passed({
                endpoint: 'insights/dashboard/overview',
                accessible: true,
                requiresAuth: false
            });
        } else if (response.status === 404) {
            check.failed('Dashboard endpoint not found', { status: 404 });
        } else {
            check.degraded(`Unexpected status: ${response.status}`, { status: response.status });
        }
    } catch (error) {
        check.failed(error.message);
    }

    return check;
}

/**
 * ============================================================================
 * IMPORTANT CHECKS - Should pass, degraded mode possible if fail
 * ============================================================================
 */

/**
 * Check 5: Analytics Endpoints
 */
async function checkAnalyticsEndpoints(signal) {
    const check = new HealthCheck(
        'Analytics Endpoints',
        CheckCategory.IMPORTANT,
        'Verify analytics endpoints are accessible'
    );

    const endpoints = [
        '/insights/content/',
        '/insights/audience/',
        '/insights/predictive/best-times/demo_channel'
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
                } catch (error) {
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
    } catch (error) {
        check.failed(error.message);
    }

    return check;
}

/**
 * Check 6: API Response Time
 */
async function checkAPIPerformance(signal) {
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
    } catch (error) {
        check.failed(error.message);
    }

    return check;
}

/**
 * ============================================================================
 * OPTIONAL CHECKS - Nice to have, doesn't block startup
 * ============================================================================
 */

/**
 * Check 7: Environment Configuration
 */
async function checkEnvironmentConfig(signal) {
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

        const issues = [];

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
    } catch (error) {
        check.failed(error.message);
    }

    return check;
}

/**
 * Check 8: LocalStorage Availability
 */
async function checkLocalStorage(signal) {
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
    } catch (error) {
        check.failed(error.message);
    }

    return check;
}

/**
 * ============================================================================
 * MAIN SYSTEM HEALTH CHECK
 * ============================================================================
 */

/**
 * Run comprehensive production readiness check
 *
 * @param {Object} options - Check options
 * @param {boolean} options.skipOptional - Skip optional checks
 * @param {number} options.timeout - Timeout per check in ms
 * @param {Function} options.onProgress - Progress callback
 * @returns {Promise<ReadinessReport>}
 */
export async function runProductionReadinessCheck(options = {}) {
    const {
        skipOptional = false,
        timeout = 10000,
        onProgress = null
    } = options;

    const report = new ReadinessReport();

    // Define all checks
    const allChecks = [
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
        } catch (error) {
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
export async function quickHealthCheck() {
    try {
        const check = await executeCheck(checkAPIBasicHealth, 5000);
        return {
            healthy: check.status === CheckStatus.PASSED,
            details: check.details,
            error: check.error
        };
    } catch (error) {
        return {
            healthy: false,
            error: error.message
        };
    }
}

/**
 * Generate human-readable report
 */
export function formatReadinessReport(report) {
    const lines = [];

    lines.push('');
    lines.push('═══════════════════════════════════════════════════════════');
    lines.push('          🏥 PRODUCTION READINESS REPORT');
    lines.push('═══════════════════════════════════════════════════════════');
    lines.push('');
    lines.push(`Status: ${report.getStatusEmoji()} ${report.overallStatus.toUpperCase()}`);
    lines.push(`Duration: ${report.getDuration()}ms`);
    lines.push(`Production Ready: ${report.isProductionReady() ? 'YES ✅' : 'NO ❌'}`);
    lines.push('');

    // Group checks by category
    const categories = {
        [CheckCategory.CRITICAL]: [],
        [CheckCategory.IMPORTANT]: [],
        [CheckCategory.OPTIONAL]: []
    };

    report.checks.forEach(check => {
        categories[check.category].push(check);
    });

    // Display checks
    Object.entries(categories).forEach(([category, checks]) => {
        if (checks.length === 0) return;

        lines.push(`─── ${category.toUpperCase()} CHECKS ─────────────────────────────────`);
        checks.forEach(check => {
            const emoji = check.status === CheckStatus.PASSED ? '✅' :
                         check.status === CheckStatus.DEGRADED ? '⚠️' :
                         check.status === CheckStatus.TIMEOUT ? '⏱️' : '❌';
            lines.push(`${emoji} ${check.name} (${check.duration}ms)`);
            if (check.error) {
                lines.push(`   └─ Error: ${check.error}`);
            }
        });
        lines.push('');
    });

    // Critical failures
    if (report.criticalFailures.length > 0) {
        lines.push('─── ❌ CRITICAL FAILURES ──────────────────────────────────');
        report.criticalFailures.forEach(check => {
            lines.push(`• ${check.name}: ${check.error}`);
        });
        lines.push('');
    }

    // Warnings
    if (report.warnings.length > 0) {
        lines.push('─── ⚠️  WARNINGS ──────────────────────────────────────────');
        report.warnings.forEach(check => {
            lines.push(`• ${check.name}: ${check.error}`);
        });
        lines.push('');
    }

    // Recommendations
    if (report.recommendations.length > 0) {
        lines.push('─── 💡 RECOMMENDATIONS ────────────────────────────────────');
        report.recommendations.forEach(rec => {
            lines.push(`• ${rec}`);
        });
        lines.push('');
    }

    lines.push('═══════════════════════════════════════════════════════════');

    return lines.join('\n');
}

export default {
    runProductionReadinessCheck,
    quickHealthCheck,
    formatReadinessReport,
    CheckStatus,
    CheckCategory
};
