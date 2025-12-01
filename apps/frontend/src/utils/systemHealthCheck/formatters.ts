/**
 * Health Report Formatters
 * Utilities for formatting health check reports
 */

import { HealthReport, HealthCheck, CheckStatus, CheckCategory } from './types';

/**
 * Generate human-readable report
 */
export function formatReadinessReport(report: HealthReport): string {
    const lines: string[] = [];

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
    const categories: Record<CheckCategory, HealthCheck[]> = {
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
