/**
 * Demo User Utilities
 * Helper functions for detecting and handling demo users
 */

/**
 * Check if the current user is a demo user
 * @returns {boolean} True if current user is a demo user
 */
export const isDemoUser = () => {
    return localStorage.getItem('is_demo_user') === 'true';
};

/**
 * Get demo-appropriate data provider based on user type
 * @returns {Object} Appropriate data provider for the user
 */
export const getDemoAwareDataProvider = async () => {
    if (isDemoUser()) {
        // For demo users, use enhanced mock services with fallbacks
        const { MockDataProvider } = await import('../providers/MockDataProvider.js');
        return new MockDataProvider();
    } else {
        // For real users, use production API
        const { productionDataProvider } = await import('../../providers/DataProvider.js');
        return productionDataProvider;
    }
};

/**
 * Show demo user guidance message
 */
export const showDemoUserGuidance = () => {
    if (isDemoUser()) {
        console.info('🎭 Demo Mode: You\'re viewing enhanced demo data. Sign up for a real account to access live analytics!');
        return true;
    }
    return false;
};

/**
 * Get demo user status for UI components
 */
export const getDemoUserStatus = () => {
    const isDemo = isDemoUser();
    return {
        isDemoUser: isDemo,
        statusMessage: isDemo ? 'Demo Mode' : 'Live Data',
        statusColor: isDemo ? 'warning' : 'success'
    };
};

/**
 * Mark the current user as a demo user
 */
export const markUserAsDemo = () => {
    localStorage.setItem('is_demo_user', 'true');
};

/**
 * Clear demo user status
 */
export const clearDemoStatus = () => {
    localStorage.removeItem('is_demo_user');
};
