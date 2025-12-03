/**
 * System Health Check Types
 * Shared type definitions for health check system
 */

/**
 * Health check categories with severity levels
 */
export enum CheckCategory {
    CRITICAL = 'critical',      // Must pass for production
    IMPORTANT = 'important',    // Should pass, but degraded mode possible
    OPTIONAL = 'optional'       // Nice to have, doesn't block startup
}

/**
 * Health check result status
 */
export enum CheckStatus {
    PASSED = 'passed',
    FAILED = 'failed',
    DEGRADED = 'degraded',
    SKIPPED = 'skipped',
    TIMEOUT = 'timeout'
}

export interface CheckDetails {
    [key: string]: any;
}

export interface ComponentStatus {
    [key: string]: {
        status: string;
        [key: string]: any;
    };
}

export interface ProgressInfo {
    current: number;
    total: number;
    check: HealthCheck;
    report: HealthReport;
}

export interface CheckDefinition {
    fn: (signal: AbortSignal) => Promise<HealthCheck>;
    category: CheckCategory;
}

export interface RunCheckOptions {
    skipOptional?: boolean;
    timeout?: number;
    onProgress?: (progress: ProgressInfo) => void;
}

/**
 * Individual health check result
 */
export class HealthCheck {
    name: string;
    category: CheckCategory;
    description: string;
    status: CheckStatus;
    error: string | null;
    details: CheckDetails;
    duration: number;

    constructor(name: string, category: CheckCategory, description: string) {
        this.name = name;
        this.category = category;
        this.description = description;
        this.status = CheckStatus.SKIPPED;
        this.error = null;
        this.details = {};
        this.duration = 0;
    }

    passed(details: CheckDetails = {}): void {
        this.status = CheckStatus.PASSED;
        this.details = details;
    }

    failed(error: string, details: CheckDetails = {}): void {
        this.status = CheckStatus.FAILED;
        this.error = error;
        this.details = details;
    }

    degraded(reason: string, details: CheckDetails = {}): void {
        this.status = CheckStatus.DEGRADED;
        this.error = reason;
        this.details = details;
    }

    timeout(): void {
        this.status = CheckStatus.TIMEOUT;
        this.error = 'Check timed out';
    }
}

/**
 * Production readiness report
 */
export class HealthReport {
    checks: HealthCheck[];
    startTime: number;
    endTime: number | null;
    overallStatus: CheckStatus;
    criticalFailures: HealthCheck[];
    warnings: HealthCheck[];
    recommendations: string[];

    constructor() {
        this.checks = [];
        this.startTime = Date.now();
        this.endTime = null;
        this.overallStatus = CheckStatus.PASSED;
        this.criticalFailures = [];
        this.warnings = [];
        this.recommendations = [];
    }

    addCheck(check: HealthCheck): void {
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

    complete(): void {
        this.endTime = Date.now();
    }

    getDuration(): number {
        return this.endTime ? this.endTime - this.startTime : Date.now() - this.startTime;
    }

    isProductionReady(): boolean {
        return this.criticalFailures.length === 0;
    }

    getStatusEmoji(): string {
        switch (this.overallStatus) {
            case CheckStatus.PASSED: return '✅';
            case CheckStatus.DEGRADED: return '⚠️';
            case CheckStatus.FAILED: return '❌';
            default: return '❓';
        }
    }
}
