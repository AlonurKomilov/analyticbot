/**
 * Application initialization utilities
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:11400';

/**
 * Check if API is available and auto-configure data source
 */
export const initializeDataSource = async () => {
    try {
        // Quick API health check with short timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000); // 2 second timeout
        
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            // API is available, keep current preference or default to mock for better UX
            const savedPreference = localStorage.getItem('useRealAPI');
            if (savedPreference === null) {
                // First time user, default to demo mode for better initial experience
                localStorage.setItem('useRealAPI', 'false');
                return 'mock';
            }
            return savedPreference === 'true' ? 'api' : 'mock';
        } else {
            // API returned error, use demo mode
            localStorage.setItem('useRealAPI', 'false');
            return 'mock';
        }
    } catch (error) {
        // API is not available (connection refused, timeout, etc.)
        if (import.meta.env.DEV) {
            console.log('API check failed, using demo mode:', error.message);
        }
        localStorage.setItem('useRealAPI', 'false');
        return 'mock';
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
        
        // Fallback to demo mode
        localStorage.setItem('useRealAPI', 'false');
        window.dispatchEvent(new CustomEvent('appInitialized', { 
            detail: { dataSource: 'mock', error: error.message, timestamp: Date.now() }
        }));
        
        return { success: false, dataSource: 'mock', error: error.message };
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
