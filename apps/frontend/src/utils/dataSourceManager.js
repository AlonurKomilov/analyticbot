/**
 * Centralized Data Source Management System
 * Replaces scattered mock switching logic across multiple files
 */

class DataSourceManager {
    static instance = null;

    constructor() {
        if (DataSourceManager.instance) {
            return DataSourceManager.instance;
        }

        this.dataSource = this.getStoredDataSource();
        this.listeners = new Set();
        this.apiStatus = 'unknown'; // unknown, online, offline
        this.lastApiCheck = null;

        DataSourceManager.instance = this;
    }

    static getInstance() {
        if (!DataSourceManager.instance) {
            DataSourceManager.instance = new DataSourceManager();
        }
        return DataSourceManager.instance;
    }

    // Data source management
    getStoredDataSource() {
        const saved = localStorage.getItem('useRealAPI');
        return saved === 'true' ? 'api' : 'mock';
    }

    getDataSource() {
        return this.dataSource;
    }

    setDataSource(source, reason = 'user_choice') {
        if (source !== 'api' && source !== 'mock') {
            console.error('Invalid data source:', source);
            return false;
        }

        const previousSource = this.dataSource;
        this.dataSource = source;

        // Update localStorage
        localStorage.setItem('useRealAPI', source === 'api' ? 'true' : 'false');

        // Notify all listeners if source actually changed
        if (previousSource !== source) {
            this.notifyListeners({ source, previousSource, reason });

            // Log the change
            if (import.meta.env.DEV) {
                console.log(`🔄 Data source changed: ${previousSource} → ${source} (${reason})`);
            }
        }

        return true;
    }

    isUsingRealAPI() {
        return this.dataSource === 'api';
    }

    // API Status management
    getApiStatus() {
        return this.apiStatus;
    }

    async checkApiStatus(force = false) {
        // Don't check too frequently unless forced
        if (!force && this.lastApiCheck && (Date.now() - this.lastApiCheck) < 30000) {
            return this.apiStatus;
        }

        try {
            const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
                                import.meta.env.VITE_API_URL ||
                                'http://185.211.5.244:11400';

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000);

            const response = await fetch(`${API_BASE_URL}/health`, {
                method: 'GET',
                signal: controller.signal,
                headers: { 'Content-Type': 'application/json' }
            });

            clearTimeout(timeoutId);

            const newStatus = response.ok ? 'online' : 'offline';
            const statusChanged = this.apiStatus !== newStatus;

            this.apiStatus = newStatus;
            this.lastApiCheck = Date.now();

            // If API came back online and user prefers API, suggest switching
            if (statusChanged && newStatus === 'online' && !this.isUsingRealAPI()) {
                this.notifyListeners({
                    type: 'api_status_changed',
                    status: newStatus,
                    suggestion: 'switch_to_api'
                });
            }

            // No auto-switch - let user decide through proper demo login
            if (statusChanged && newStatus === 'offline' && this.isUsingRealAPI()) {
                console.info('API unavailable - user should sign in to demo account for mock data');
                // Emit event but don't auto-switch
                this.emit('apiStatusChanged', { status: newStatus, suggestion: 'demo_login' });
            }

            return newStatus;

        } catch (error) {
            this.apiStatus = 'offline';
            this.lastApiCheck = Date.now();

            // No auto-switch - suggest demo login instead
            if (this.isUsingRealAPI()) {
                console.info('API connection failed - user should sign in to demo account for mock data');
                this.emit('apiConnectionFailed', { suggestion: 'demo_login' });
            }

            return 'offline';
        }
    }

    // Event system
    subscribe(callback, options = {}) {
        if (typeof callback !== 'function') {
            console.error('DataSourceManager: Callback must be a function');
            return () => {};
        }

        const listener = { callback, options };
        this.listeners.add(listener);

        // Return unsubscribe function
        return () => this.unsubscribe(listener);
    }

    unsubscribe(listener) {
        this.listeners.delete(listener);
    }

    notifyListeners(eventData) {
        this.listeners.forEach(listener => {
            try {
                // Check if listener wants this type of event
                if (listener.options.eventType &&
                    eventData.type &&
                    listener.options.eventType !== eventData.type) {
                    return;
                }

                listener.callback(eventData);
            } catch (error) {
                console.error('DataSourceManager: Error in listener callback:', error);
            }
        });
    }

    // Convenience methods - DEPRECATED: No longer allow switching to frontend mock
    async switchToMock(reason = 'user_choice') {
        console.warn('switchToMock is deprecated - user should sign in to demo account for mock data');

        // Redirect to demo login instead of switching to frontend mock
        const demoLoginUrl = `/login?demo=true&redirect=${encodeURIComponent(window.location.pathname)}`;
        window.location.href = demoLoginUrl;

        return false; // No switch occurred
    }

    async switchToApi(reason = 'user_choice') {
        // Check API status first
        const apiStatus = await this.checkApiStatus(true);

        if (apiStatus === 'offline') {
            console.warn('Cannot switch to API: API is offline');
            this.notifyListeners({
                type: 'switch_failed',
                reason: 'api_offline',
                requestedSource: 'api'
            });
            return false;
        }

        return this.setDataSource('api', reason);
    }

    // Auto-initialization
    async initialize() {
        // Check API status on startup
        await this.checkApiStatus(true);

        // No auto-switch during initialization - maintain user preference
        if (this.isUsingRealAPI() && this.apiStatus === 'offline') {
            console.info('API offline during initialization - user should sign in to demo account for mock data');
            this.emit('initializationApiOffline', { suggestion: 'demo_login' });
        }

        return {
            dataSource: this.dataSource,
            apiStatus: this.apiStatus
        };
    }

    // Cleanup
    destroy() {
        this.listeners.clear();
        DataSourceManager.instance = null;
    }
}

// Export singleton instance
export const dataSourceManager = DataSourceManager.getInstance();

// Export class for testing
export { DataSourceManager };

// Convenience exports
export const useDataSourceManager = () => dataSourceManager;
export const getDataSource = () => dataSourceManager.getDataSource();
export const setDataSource = (source, reason) => dataSourceManager.setDataSource(source, reason);
export const isUsingRealAPI = () => dataSourceManager.isUsingRealAPI();
