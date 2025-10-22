/**
 * Offline Storage Utility for Analytics Data
 * Provides caching, offline support, and data synchronization
 */

import localforage from 'localforage';

// Configure localforage for optimal performance
localforage.config({
    driver: [localforage.INDEXEDDB, localforage.WEBSQL, localforage.LOCALSTORAGE],
    name: 'AnalyticBot',
    version: 1.0,
    storeName: 'analytics_cache',
    description: 'Analytics data cache for offline support'
});

interface MaxAge {
    analytics: number;
    dashboard: number;
    realtime: number;
    performance: number;
    mobile: number;
}

interface CacheOptions {
    period?: string;
    format?: string;
    timestamp?: number | string;
}

interface CacheMetadata {
    size: number;
    compressed: boolean;
    version: string;
    [key: string]: any;
}

interface CacheEntry<T = any> {
    data: T | string;
    timestamp: number;
    channelId: string;
    type: string;
    metadata: CacheMetadata;
}

interface CachedData<T = any> extends T {
    _cached: boolean;
    _cacheTime: number;
    _cacheAge: number;
}

interface CacheStats {
    totalEntries: number;
    totalSize: number;
    typeBreakdown: Record<string, number>;
    channelBreakdown: Record<string, number>;
    maxCacheSize: number;
    usagePercentage: number;
}

interface DashboardData {
    metrics?: any;
    trends?: any[];
    alerts?: any[];
    totalViews?: number;
    growthRate?: number;
    engagementRate?: number;
    performanceScore?: number;
}

interface RealTimeMetrics {
    totalViews?: number;
    growthRate?: number;
    engagementRate?: number;
    performanceScore?: number;
    alerts?: any[];
}

interface APIClient {
    get: (url: string) => Promise<any>;
}

class OfflineStorage {
    maxAge: MaxAge;
    maxCacheSize: number;
    compressionEnabled: boolean;

    constructor() {
        this.maxAge = {
            analytics: 3600000,     // 1 hour for analytics data
            dashboard: 1800000,     // 30 minutes for dashboard data
            realtime: 300000,       // 5 minutes for real-time data
            performance: 7200000,   // 2 hours for performance metrics
            mobile: 600000          // 10 minutes for mobile widget data
        };

        this.maxCacheSize = 50 * 1024 * 1024; // 50MB max cache size
        this.compressionEnabled = true;
    }

    /**
     * Generate cache key with metadata
     */
    generateCacheKey(type: string, identifier: string, options: CacheOptions = {}): string {
        const { period, format, timestamp } = options;
        let key = `${type}_${identifier}`;

        if (period) key += `_${period}`;
        if (format) key += `_${format}`;
        if (timestamp) key += `_${timestamp}`;

        return key;
    }

    /**
     * Cache analytics data with metadata
     */
    async cacheAnalyticsData(channelId: string, data: any, type: string = 'analytics', options: CacheOptions = {}): Promise<boolean> {
        try {
            const key = this.generateCacheKey(type, channelId, options);
            const cacheEntry: CacheEntry = {
                data: this.compressionEnabled ? this.compressData(data) : data,
                timestamp: Date.now(),
                channelId,
                type,
                metadata: {
                    size: JSON.stringify(data).length,
                    compressed: this.compressionEnabled,
                    version: '1.0',
                    ...options
                }
            };

            await localforage.setItem(key, cacheEntry);

            // Clean up old cache entries if needed
            await this.cleanupCache();

            return true;
        } catch (error) {
            console.error('Failed to cache analytics data:', error);
            return false;
        }
    }

    /**
     * Retrieve cached analytics data
     */
    async getCachedData<T = any>(channelId: string, type: string = 'analytics', options: CacheOptions = {}): Promise<CachedData<T> | null> {
        try {
            const key = this.generateCacheKey(type, channelId, options);
            const cacheEntry = await localforage.getItem<CacheEntry>(key);

            if (!cacheEntry) return null;

            // Check if cache is still valid
            const maxAge = this.maxAge[type as keyof MaxAge] || this.maxAge.analytics;
            const isExpired = (Date.now() - cacheEntry.timestamp) > maxAge;

            if (isExpired) {
                await localforage.removeItem(key);
                return null;
            }

            // Decompress data if needed
            const data = cacheEntry.metadata?.compressed
                ? this.decompressData(cacheEntry.data)
                : cacheEntry.data;

            return {
                ...data,
                _cached: true,
                _cacheTime: cacheEntry.timestamp,
                _cacheAge: Date.now() - cacheEntry.timestamp
            };
        } catch (error) {
            console.error('Failed to retrieve cached data:', error);
            return null;
        }
    }

    /**
     * Cache dashboard data optimized for mobile
     */
    async cacheDashboardData(channelId: string, dashboardData: DashboardData): Promise<boolean> {
        const compressedData = {
            metrics: dashboardData.metrics,
            trends: dashboardData.trends?.slice(-7), // Last 7 data points only
            alerts: dashboardData.alerts?.slice(0, 5), // Max 5 alerts
            summary: {
                totalViews: dashboardData.totalViews,
                growthRate: dashboardData.growthRate,
                engagementRate: dashboardData.engagementRate,
                performanceScore: dashboardData.performanceScore
            }
        };

        return await this.cacheAnalyticsData(channelId, compressedData, 'dashboard');
    }

    /**
     * Cache real-time metrics for quick access
     */
    async cacheRealTimeMetrics(channelId: string, metricsData: RealTimeMetrics): Promise<boolean> {
        const essentialMetrics = {
            views: metricsData.totalViews,
            growth: metricsData.growthRate,
            engagement: metricsData.engagementRate,
            score: metricsData.performanceScore,
            timestamp: Date.now(),
            alerts: metricsData.alerts?.length || 0
        };

        return await this.cacheAnalyticsData(channelId, essentialMetrics, 'realtime');
    }

    /**
     * Cache mobile widget data
     */
    async cacheMobileWidgetData(channelId: string, widgetData: any, widgetType: string = 'default'): Promise<boolean> {
        const options = { format: widgetType };
        return await this.cacheAnalyticsData(channelId, widgetData, 'mobile', options);
    }

    /**
     * Get all cached channels
     */
    async getCachedChannels(): Promise<string[]> {
        try {
            const keys = await localforage.keys();
            const channels = new Set<string>();

            keys.forEach(key => {
                const parts = key.split('_');
                if (parts.length >= 2) {
                    channels.add(parts[1]); // Channel ID is typically the second part
                }
            });

            return Array.from(channels);
        } catch (error) {
            console.error('Failed to get cached channels:', error);
            return [];
        }
    }

    /**
     * Get cache statistics
     */
    async getCacheStats(): Promise<CacheStats | { error: string }> {
        try {
            const keys = await localforage.keys();
            let totalSize = 0;
            const typeCount: Record<string, number> = {};
            const channelCount: Record<string, number> = {};

            for (const key of keys) {
                const entry = await localforage.getItem<CacheEntry>(key);
                if (entry && entry.metadata) {
                    totalSize += entry.metadata.size || 0;

                    const type = entry.type || 'unknown';
                    typeCount[type] = (typeCount[type] || 0) + 1;

                    const channelId = entry.channelId || 'unknown';
                    channelCount[channelId] = (channelCount[channelId] || 0) + 1;
                }
            }

            return {
                totalEntries: keys.length,
                totalSize,
                typeBreakdown: typeCount,
                channelBreakdown: channelCount,
                maxCacheSize: this.maxCacheSize,
                usagePercentage: (totalSize / this.maxCacheSize) * 100
            };
        } catch (error: any) {
            console.error('Failed to get cache stats:', error);
            return { error: error.message };
        }
    }

    /**
     * Clean up expired cache entries
     */
    async cleanupCache(): Promise<number> {
        try {
            const keys = await localforage.keys();
            const now = Date.now();
            let cleanedCount = 0;

            for (const key of keys) {
                const entry = await localforage.getItem<CacheEntry>(key);
                if (entry && entry.timestamp) {
                    const type = entry.type || 'analytics';
                    const maxAge = this.maxAge[type as keyof MaxAge] || this.maxAge.analytics;

                    if ((now - entry.timestamp) > maxAge) {
                        await localforage.removeItem(key);
                        cleanedCount++;
                    }
                }
            }

            console.log(`Cleaned up ${cleanedCount} expired cache entries`);
            return cleanedCount;
        } catch (error) {
            console.error('Failed to cleanup cache:', error);
            return 0;
        }
    }

    /**
     * Clear all cache data
     */
    async clearCache(): Promise<boolean> {
        try {
            await localforage.clear();
            console.log('All cache data cleared');
            return true;
        } catch (error) {
            console.error('Failed to clear cache:', error);
            return false;
        }
    }

    /**
     * Clear cache for specific channel
     */
    async clearChannelCache(channelId: string): Promise<number> {
        try {
            const keys = await localforage.keys();
            let clearedCount = 0;

            for (const key of keys) {
                if (key.includes(`_${channelId}_`) || key.includes(`_${channelId}`)) {
                    await localforage.removeItem(key);
                    clearedCount++;
                }
            }

            console.log(`Cleared ${clearedCount} cache entries for channel ${channelId}`);
            return clearedCount;
        } catch (error) {
            console.error('Failed to clear channel cache:', error);
            return 0;
        }
    }

    /**
     * Simple data compression (JSON string compression)
     */
    compressData(data: any): string {
        try {
            // Simple compression by removing unnecessary whitespace
            return JSON.stringify(data);
        } catch (error) {
            console.error('Data compression failed:', error);
            return data;
        }
    }

    /**
     * Decompress data
     */
    decompressData(compressedData: any): any {
        try {
            return typeof compressedData === 'string'
                ? JSON.parse(compressedData)
                : compressedData;
        } catch (error) {
            console.error('Data decompression failed:', error);
            return compressedData;
        }
    }

    /**
     * Check if offline
     */
    isOffline(): boolean {
        return !navigator.onLine;
    }

    /**
     * Sync cached data with server when online
     */
    async syncWhenOnline(apiClient: APIClient): Promise<number | false> {
        if (this.isOffline()) {
            console.log('Still offline, sync delayed');
            return false;
        }

        try {
            const channels = await this.getCachedChannels();
            let syncedCount = 0;

            for (const channelId of channels) {
                try {
                    // Fetch fresh data and update cache
                    const freshData = await apiClient.get(`/api/v2/analytics/channels/${channelId}/overview`);
                    await this.cacheAnalyticsData(channelId, freshData);
                    syncedCount++;
                } catch (error) {
                    console.warn(`Failed to sync data for channel ${channelId}:`, error);
                }
            }

            console.log(`Synced ${syncedCount} channels with server`);
            return syncedCount;
        } catch (error) {
            console.error('Failed to sync data:', error);
            return 0;
        }
    }

    /**
     * Initialize offline storage
     */
    async initialize(): Promise<boolean> {
        try {
            // Test if storage is available
            await localforage.setItem('test', 'test');
            await localforage.removeItem('test');

            // Clean up old cache on startup
            await this.cleanupCache();

            console.log('Offline storage initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize offline storage:', error);
            return false;
        }
    }
}

// Create singleton instance
const offlineStorage = new OfflineStorage();

// Initialize on import
offlineStorage.initialize();

export default offlineStorage;
