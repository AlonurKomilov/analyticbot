/**
 * Profile Page Types
 * Type definitions for the profile page components
 */

export interface ProfileData {
    username: string;
    fullName: string;
    email: string;
}

export interface PasswordData {
    currentPassword: string;
    newPassword: string;
    confirmPassword: string;
}

export interface PasswordErrors {
    currentPassword?: string;
    newPassword?: string;
    confirmPassword?: string;
}

export interface TabPanelProps {
    children: React.ReactNode;
    value: number;
    index: number;
}
