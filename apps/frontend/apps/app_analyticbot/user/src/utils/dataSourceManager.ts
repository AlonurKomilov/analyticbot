/**
 * Centralized Data Source Management System
 * Replaces scattered mock switching logic across multiple files
 */

type DataSource = 'api' | 'mock';
type ApiStatus = 'unknown' | 'online' | 'offline';

interface DataSourceChangeEvent {
    source?: DataSource;
    previousSource?: DataSource;
    reason?: string;
    type?: string;
    status?: ApiStatus;
    suggestion?: string;
}

interface ListenerOptions {
    eventType?: string;
}

interface Listener {
    callback: (eventData: DataSourceChangeEvent) => void;
    options: ListenerOptions;
}

interface InitializationResult {
    dataSource: DataSource;
    apiStatus: ApiStatus;
}

class DataSourceManager {
    private static instance: DataSourceManager | null = null;
    private dataSource!: DataSource;
    private listeners!: Set<Listener>;
    private apiStatus!: ApiStatus;
    private lastApiCheck!: number | null;

    constructor() {
        if (DataSourceManager.instance) {
            return DataSourceManager.instance;
        }

        this.dataSource = this.getStoredDataSource();
        this.listeners = new Set();
        this.apiStatus = 'unknown';
        this.lastApiCheck = null;

        DataSourceManager.instance = this;
    }

    static getInstance(): DataSourceManager {
        if (!DataSourceManager.instance) {
            DataSourceManager.instance = new DataSourceManager();
        }
        return DataSourceManager.instance;
    }

    // Data source management
    private getStoredDataSource(): DataSource {
        const saved = localStorage.getItem('useRealAPI');
        return saved === 'true' ? 'api' : 'mock';
    }

    getDataSource(): DataSource {
        return this.dataSource;
    }

    setDataSource(source: DataSource, reason: string = 'user_choice'): boolean {
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

    isUsingRealAPI(): boolean {
        return this.dataSource === 'api';
    }

    // API Status management
    getApiStatus(): ApiStatus {
        return this.apiStatus;
    }

    async checkApiStatus(force: boolean = false): Promise<ApiStatus> {
        // Don't check too frequently unless forced
        if (!force && this.lastApiCheck && (Date.now() - this.lastApiCheck) < 30000) {
            return this.apiStatus;
        }

        try {
            const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
                                import.meta.env.VITE_API_URL ||
                                'https://b2qz1m0n-11400.euw.devtunnels.ms';

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // Increased to 10s to match slow API response times

            const response = await fetch(`${API_BASE_URL}/health`, {
                method: 'GET',
                signal: controller.signal,
                headers: { 'Content-Type': 'application/json' }
            });

            clearTimeout(timeoutId);

            const newStatus: ApiStatus = response.ok ? 'online' : 'offline';
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
    subscribe(callback: (eventData: DataSourceChangeEvent) => void, options: ListenerOptions = {}): () => void {
        if (typeof callback !== 'function') {
            console.error('DataSourceManager: Callback must be a function');
            return () => {};
        }

        const listener: Listener = { callback, options };
        this.listeners.add(listener);

        // Return unsubscribe function
        return () => this.unsubscribe(listener);
    }

    private unsubscribe(listener: Listener): void {
        this.listeners.delete(listener);
    }

    private notifyListeners(eventData: DataSourceChangeEvent): void {
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

    private emit(eventType: string, data: DataSourceChangeEvent): void {
        this.notifyListeners({ ...data, type: eventType });
    }

    // Convenience methods - DEPRECATED: No longer allow switching to frontend mock
    async switchToMock(): Promise<boolean> {
        console.warn('switchToMock is deprecated - user should sign in to demo account for mock data');

        // Redirect to demo login instead of switching to frontend mock
        const demoLoginUrl = `/login?demo=true&redirect=${encodeURIComponent(window.location.pathname)}`;
        window.location.href = demoLoginUrl;

        return false; // No switch occurred
    }

    async switchToApi(reason: string = 'user_choice'): Promise<boolean> {
        // Check API status first
        const apiStatus = await this.checkApiStatus(true);

        if (apiStatus === 'offline') {
            console.warn('Cannot switch to API: API is offline');
            this.notifyListeners({
                type: 'switch_failed',
                reason: 'api_offline',
                source: 'api'
            });
            return false;
        }

        return this.setDataSource('api', reason);
    }

    // Auto-initialization
    async initialize(): Promise<InitializationResult> {
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
    destroy(): void {
        this.listeners.clear();
        DataSourceManager.instance = null;
    }
}

// Export singleton instance
export const dataSourceManager = DataSourceManager.getInstance();

// Export class for testing
export { DataSourceManager };

// Convenience exports
export const useDataSourceManager = (): DataSourceManager => dataSourceManager;
export const getDataSource = (): DataSource => dataSourceManager.getDataSource();
export const setDataSource = (source: DataSource, reason?: string): boolean => dataSourceManager.setDataSource(source, reason);
export const isUsingRealAPI = (): boolean => dataSourceManager.isUsingRealAPI();
