/**
 * RegisterForm Types
 * Type definitions for registration form components
 */

export interface FormData {
    email: string;
    password: string;
    confirmPassword: string;
    username: string;
    fullName: string;
}

export interface FormErrors {
    email?: string;
    password?: string;
    confirmPassword?: string;
    username?: string;
    fullName?: string;
}

export interface PasswordRequirements {
    length: boolean;
    lowercase: boolean;
    uppercase: boolean;
    number: boolean;
    special: boolean;
}

export interface PasswordStrength {
    score: number;
    requirements: PasswordRequirements;
}

export interface RegisterFormProps {
    onToggleMode?: (() => void) | null;
}
