/**
 * Utility functions for formatting data in tables and components
 */

/**
 * Format large numbers with appropriate suffixes (K, M, B)
 */
export const formatNumber = (num) => {
    if (num === null || num === undefined || isNaN(num)) return '0';

    const number = parseInt(num);

    if (number >= 1000000000) {
        return (number / 1000000000).toFixed(1) + 'B';
    }
    if (number >= 1000000) {
        return (number / 1000000).toFixed(1) + 'M';
    }
    if (number >= 1000) {
        return (number / 1000).toFixed(1) + 'K';
    }

    return number.toString();
};

/**
 * Format date to readable string
 */
export const formatDate = (dateInput) => {
    if (!dateInput) return 'Unknown';

    const date = new Date(dateInput);
    if (isNaN(date.getTime())) return 'Invalid Date';

    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    // If within 24 hours, show relative time
    if (diffInHours < 24) {
        if (diffInHours < 1) {
            const minutes = Math.floor((now - date) / (1000 * 60));
            return `${minutes}m ago`;
        }
        return `${Math.floor(diffInHours)}h ago`;
    }

    // If within a week, show days ago
    if (diffInHours < 24 * 7) {
        const days = Math.floor(diffInHours / 24);
        return `${days}d ago`;
    }

    // Otherwise show formatted date
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
};

/**
 * Calculate engagement rate for a post
 */
export const calculateEngagementRate = (post) => {
    if (!post) return 0;

    const views = parseInt(post.views) || 0;
    const likes = parseInt(post.likes) || 0;
    const shares = parseInt(post.shares) || 0;
    const comments = parseInt(post.comments) || 0;

    if (views === 0) return 0;

    const totalEngagement = likes + shares + comments;
    return (totalEngagement / views) * 100;
};

/**
 * Format percentage with appropriate decimal places
 */
export const formatPercentage = (value, decimals = 1) => {
    if (value === null || value === undefined || isNaN(value)) return '0%';
    return `${parseFloat(value).toFixed(decimals)}%`;
};

/**
 * Format currency values
 */
export const formatCurrency = (amount, currency = 'USD') => {
    if (amount === null || amount === undefined || isNaN(amount)) return '$0';

    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(amount);
};

/**
 * Format duration in seconds to human readable format
 */
export const formatDuration = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0s';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
};

/**
 * Truncate text to specified length with ellipsis
 */
export const truncateText = (text, maxLength = 100) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
};

/**
 * Get status color based on value
 */
export const getStatusColor = (status) => {
    if (!status) return 'default';

    const statusMap = {
        'published': 'success',
        'active': 'success',
        'live': 'success',
        'online': 'success',
        'completed': 'success',
        'approved': 'success',

        'scheduled': 'info',
        'pending': 'info',
        'processing': 'info',
        'in-progress': 'info',

        'draft': 'warning',
        'paused': 'warning',
        'review': 'warning',
        'waiting': 'warning',

        'archived': 'default',
        'inactive': 'default',
        'disabled': 'default',

        'failed': 'error',
        'error': 'error',
        'rejected': 'error',
        'cancelled': 'error'
    };

    return statusMap[status.toLowerCase()] || 'default';
};

/**
 * Sort array of objects by field
 */
export const sortByField = (array, field, direction = 'asc') => {
    return [...array].sort((a, b) => {
        let aVal = a[field];
        let bVal = b[field];

        // Handle null/undefined values
        if (aVal === null || aVal === undefined) aVal = '';
        if (bVal === null || bVal === undefined) bVal = '';

        // Convert to numbers if possible
        if (!isNaN(aVal) && !isNaN(bVal)) {
            aVal = parseFloat(aVal);
            bVal = parseFloat(bVal);
        }

        // Convert to strings for comparison
        if (typeof aVal === 'string') aVal = aVal.toLowerCase();
        if (typeof bVal === 'string') bVal = bVal.toLowerCase();

        if (direction === 'desc') {
            return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
        }
        return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
    });
};

/**
 * Filter array of objects by search term across multiple fields
 */
export const filterBySearch = (array, searchTerm, searchFields = []) => {
    if (!searchTerm || !searchTerm.trim()) return array;

    const term = searchTerm.toLowerCase().trim();

    return array.filter(item => {
        // Search in specified fields
        if (searchFields.length > 0) {
            return searchFields.some(field => {
                const value = item[field];
                if (value === null || value === undefined) return false;
                return String(value).toLowerCase().includes(term);
            });
        }

        // Search in all string fields if no specific fields provided
        return Object.values(item).some(value => {
            if (value === null || value === undefined) return false;
            return String(value).toLowerCase().includes(term);
        });
    });
};
