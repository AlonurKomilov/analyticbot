/**
 * Password Utilities
 * Password strength calculation and display helpers
 */

import type { PasswordStrength, PasswordRequirements } from './types';

/**
 * Calculate password strength based on requirements
 */
export function calculatePasswordStrength(password: string): PasswordStrength {
    let score = 0;
    const requirements: PasswordRequirements = {
        length: password.length >= 8,
        lowercase: /[a-z]/.test(password),
        uppercase: /[A-Z]/.test(password),
        number: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    Object.values(requirements).forEach(met => {
        if (met) score += 20;
    });

    return { score, requirements };
}

/**
 * Get color for password strength indicator
 */
export function getPasswordStrengthColor(score: number): 'error' | 'warning' | 'success' {
    if (score < 40) return 'error';
    if (score < 80) return 'warning';
    return 'success';
}

/**
 * Get label for password strength
 */
export function getPasswordStrengthLabel(score: number): string {
    if (score < 40) return 'Weak';
    if (score < 80) return 'Good';
    return 'Strong';
}

/**
 * Password requirement descriptions
 */
export const PASSWORD_REQUIREMENTS: Record<keyof PasswordRequirements, string> = {
    length: 'At least 8 characters',
    lowercase: 'Lowercase letter (a-z)',
    uppercase: 'Uppercase letter (A-Z)',
    number: 'Number (0-9)',
    special: 'Special character (!@#$%^&*)'
};
