/**
 * Application initialization utilities
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://84dp9jc9-11400.euw.devtunnels.ms';

/**
 * Check if API is available and auto-configure data source
 */
export const initializeDataSource = async () => {
    try {
        // API health check with reasonable timeout for devtunnel connections
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort('Connection timeout after 5 seconds'), 5000); // 5 second timeout
        
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            // API is available, keep current preference or default to API
            const savedPreference = localStorage.getItem('useRealAPI');
            if (savedPreference === null) {
                // First time user, default to API mode - user can sign in to demo if needed
                localStorage.setItem('useRealAPI', 'true');
                return 'api';
            }
            return savedPreference === 'true' ? 'api' : 'mock';
        } else {
            // API returned error, don't auto-switch - user should sign in to demo account
            console.info('API health check returned error - continuing with API mode for demo authentication');
            return 'api'; // Keep API mode, let backend handle demo authentication
        }
    } catch (error) {
        // API is not available (connection refused, timeout, etc.)
        if (import.meta.env.DEV) {
            console.log('API health check failed - continuing with API mode for demo authentication:', error.name === 'AbortError' ? 'Connection timeout' : error.message);
        }
        // Don't auto-switch to mock - user should sign in to demo account instead
        return 'api'; // Keep API mode, let backend handle demo authentication
    }
};

/**
 * Initialize application with proper error handling
 */
export const initializeApp = async () => {
    try {
        // Initialize data source
        const dataSource = await initializeDataSource();
        
        // Dispatch initialization event
        window.dispatchEvent(new CustomEvent('appInitialized', { 
            detail: { dataSource, timestamp: Date.now() }
        }));
        
        return { success: true, dataSource };
    } catch (error) {
        console.error('App initialization error:', error);
        
        // Don't fallback to demo mode - user should sign in to demo account instead
        console.info('App initialization encountered an error - continuing with API mode for demo authentication');
        window.dispatchEvent(new CustomEvent('appInitialized', { 
            detail: { dataSource: 'api', error: error.message, timestamp: Date.now() }
        }));
        
        return { success: false, dataSource: 'api', error: error.message };
    }
};

/**
 * Show user-friendly notification about data source
 */
export const showDataSourceNotification = (dataSource, reason = null) => {
    const messages = {
        'api': '🔗 Connected to live API data',
        'mock': '🎭 Using professional demo data',
        'api_unavailable': '⚠️ API unavailable - switched to demo mode automatically',
        'api_error': '❌ API error - using demo data as fallback'
    };
    
    const message = messages[reason] || messages[dataSource];
    
    // Create a simple toast notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #333;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        max-width: 300px;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: opacity 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
};

export default {
    initializeDataSource,
    initializeApp,
    showDataSourceNotification
};
