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
 * Refactored: Nov 2025 - Split into modular files in ./systemHealthCheck/
 * This file re-exports for backward compatibility.
 */

// Re-export everything from the modular implementation
export {
    CheckCategory,
    CheckStatus,
    HealthCheck,
    HealthReport,
    runProductionReadinessCheck,
    quickHealthCheck,
    formatReadinessReport
} from './systemHealthCheck/index';

export type { CheckDetails, RunCheckOptions, ProgressInfo } from './systemHealthCheck/types';

// Default export for backward compatibility
import systemHealthCheck from './systemHealthCheck/index';
export default systemHealthCheck;
