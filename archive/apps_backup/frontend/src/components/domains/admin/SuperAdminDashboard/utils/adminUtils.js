/**
 * Utility functions for SuperAdminDashboard
 * Formatting and helper functions for admin dashboard
 */

/**
 * Get appropriate color for user status
 * @param {string} status - User status (active, suspended, pending)
 * @returns {string} Material-UI color name
 */
export const getStatusColor = (status) => {
    switch (status) {
        case 'active': return 'success';
        case 'suspended': return 'error';
        case 'pending': return 'warning';
        default: return 'default';
    }
};

/**
 * Format date string to localized format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
};

/**
 * Get status display text
 * @param {string} status - User status
 * @returns {string} Capitalized status text
 */
export const getStatusText = (status) => {
    return status.charAt(0).toUpperCase() + status.slice(1);
};