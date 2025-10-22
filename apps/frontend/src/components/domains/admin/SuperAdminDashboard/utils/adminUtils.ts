/**
 * Utility functions for SuperAdminDashboard
 * Formatting and helper functions for admin dashboard
 */

type StatusColor = 'success' | 'error' | 'warning' | 'default';

/**
 * Get appropriate color for user status
 * @param status - User status (active, suspended, pending)
 * @returns Material-UI color name
 */
export const getStatusColor = (status: string): StatusColor => {
    switch (status) {
        case 'active': return 'success';
        case 'suspended': return 'error';
        case 'pending': return 'warning';
        default: return 'default';
    }
};

/**
 * Format date string to localized format
 * @param dateString - ISO date string
 * @returns Formatted date string
 */
export const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
};

/**
 * Get status display text
 * @param status - User status
 * @returns Capitalized status text
 */
export const getStatusText = (status: string): string => {
    return status.charAt(0).toUpperCase() + status.slice(1);
};
