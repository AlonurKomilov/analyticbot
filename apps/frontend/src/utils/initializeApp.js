/**
 * Application initialization utilities with comprehensive health checks
 */

import {
    runProductionReadinessCheck,
    quickHealthCheck,
    formatReadinessReport
} from './systemHealthCheck.js';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://b2qz1m0n-11400.euw.devtunnels.ms';

/**
 * Perform health check with single attempt (no retry to avoid long initialization)
 * Uses 30s timeout which is sufficient for most scenarios
 *
 * @deprecated Use quickHealthCheck() from systemHealthCheck.js instead
 */
const checkAPIHealth = async (timeoutMs = 30000) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort('Health check timeout'), timeoutMs);

    try {
        const response = await fetch(`${API_BASE_URL}/health/`, {
            method: 'GET',
            signal: controller.signal,
            redirect: 'follow'
        });
        clearTimeout(timeoutId);
        return { ok: response.ok, status: response.status, response };
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
};

/**
 * Check if API is available and auto-configure data source
 */
export const initializeDataSource = async () => {
    try {
        // Skip health check for localhost (faster initialization)
        const isLocalhost = API_BASE_URL.includes('localhost') || API_BASE_URL.includes('127.0.0.1');

        if (isLocalhost) {
            if (import.meta.env.DEV) {
                console.log('✅ Localhost detected - skipping health check');
            }
            const savedPreference = localStorage.getItem('useRealAPI');
            return savedPreference === 'true' || savedPreference === null ? 'api' : 'mock';
        }

        // API health check with 30s timeout for devtunnel connections
        if (import.meta.env.DEV) {
            console.log('🔍 Checking API health...');
        }

        const { ok, status, response } = await checkAPIHealth(30000);

        if (ok) {
            // Check if API is healthy or degraded
            try {
                const healthData = await response.json();
                if (import.meta.env.DEV) {
                    if (healthData.status === 'healthy') {
                        console.log('✅ API is healthy and ready');
                    } else if (healthData.status === 'degraded') {
                        console.warn('⚠️ API is running in degraded mode (some services unavailable)');
                    }
                }
            } catch (e) {
                // Ignore JSON parse errors, health check passed
                if (import.meta.env.DEV) {
                    console.log('✅ API is available');
                }
            }

            // API is available, keep current preference or default to API
            const savedPreference = localStorage.getItem('useRealAPI');
            if (savedPreference === null) {
                // First time user, default to API mode - user can sign in to demo if needed
                localStorage.setItem('useRealAPI', 'true');
                return 'api';
            }
            return savedPreference === 'true' ? 'api' : 'mock';
        } else {
            // API returned error, don't auto-switch - user should sign in to demo account
            if (import.meta.env.DEV) {
                console.warn(`⚠️ API health check returned ${status} - continuing with API mode`);
            }
            return 'api'; // Keep API mode, let backend handle demo authentication
        }
    } catch (error) {
                // API is not available (connection refused, timeout, etc.)
        if (import.meta.env.DEV) {
            const errorMsg = error.name === 'AbortError'
                ? 'Timeout after 30s (dev tunnel may be cold-starting)'
                : (error.message || error.toString() || 'Unknown error');
            console.info('⏱️ API health check slow - continuing anyway:', errorMsg);
            console.info('💡 This is normal for dev tunnels. Authentication will use optimized timeout.');
        }
        // Don't auto-switch to mock - user should sign in to demo account instead
        return 'api'; // Keep API mode, API requests will use their own optimized timeouts
    }
};

/**
 * Initialize application with comprehensive production readiness checks
 *
 * @param {Object} options - Initialization options
 * @param {boolean} options.fullHealthCheck - Run full production readiness check (default: false)
 * @param {boolean} options.skipOptional - Skip optional checks (default: true for faster startup)
 * @param {Function} options.onProgress - Progress callback for health checks
 */
export const initializeApp = async (options = {}) => {
    const {
        fullHealthCheck = false,
        skipOptional = true,
        onProgress = null
    } = options;

    try {
        console.log('🚀 Initializing application...');

        // Initialize data source (quick check)
        const dataSource = await initializeDataSource();

        // Run production readiness checks if requested
        let healthReport = null;
        if (fullHealthCheck) {
            console.log('🏥 Running comprehensive production readiness checks...');

            healthReport = await runProductionReadinessCheck({
                skipOptional,
                timeout: 10000,
                onProgress
            });

            // Display report in console
            console.log(formatReadinessReport(healthReport));

            // Dispatch health check event
            window.dispatchEvent(new CustomEvent('healthCheckCompleted', {
                detail: {
                    report: healthReport,
                    isProductionReady: healthReport.isProductionReady(),
                    timestamp: Date.now()
                }
            }));

            // Log warnings for critical failures
            if (!healthReport.isProductionReady()) {
                console.error('❌ SYSTEM NOT PRODUCTION READY - Critical failures detected');
                healthReport.criticalFailures.forEach(failure => {
                    console.error(`  - ${failure.name}: ${failure.error}`);
                });
            } else if (healthReport.overallStatus === 'degraded') {
                console.warn('⚠️ System running in degraded mode');
                healthReport.warnings.forEach(warning => {
                    console.warn(`  - ${warning.name}: ${warning.error}`);
                });
            } else {
                console.log('✅ All systems operational - Production ready!');
            }
        }

        // Dispatch initialization event
        window.dispatchEvent(new CustomEvent('appInitialized', {
            detail: {
                dataSource,
                healthReport,
                timestamp: Date.now()
            }
        }));

        return {
            success: true,
            dataSource,
            healthReport,
            isProductionReady: healthReport ? healthReport.isProductionReady() : null
        };
    } catch (error) {
        console.error('App initialization error:', error);

        // Don't fallback to demo mode - user should sign in to demo account instead
        console.info('App initialization encountered an error - continuing with API mode for demo authentication');
        window.dispatchEvent(new CustomEvent('appInitialized', {
            detail: { dataSource: 'api', error: error.message, timestamp: Date.now() }
        }));

        return { success: false, dataSource: 'api', error: error.message };
    }
};

/**
 * Show user-friendly notification about data source
 */
export const showDataSourceNotification = (dataSource, reason = null) => {
    const messages = {
        'api': '🔗 Connected to live API data',
        'mock': '🎭 Using professional demo data',
        'api_unavailable': '⚠️ API unavailable - switched to demo mode automatically',
        'api_error': '❌ API error - using demo data as fallback'
    };

    const message = messages[reason] || messages[dataSource];

    // Create a simple toast notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #333;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        max-width: 300px;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: opacity 0.3s ease;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
};

export default {
    initializeDataSource,
    initializeApp,
    showDataSourceNotification
};
