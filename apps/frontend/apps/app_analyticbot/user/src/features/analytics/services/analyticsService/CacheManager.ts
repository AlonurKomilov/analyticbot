/**
 * Analytics Cache Manager
 * Handles caching with TTL and LRU eviction
 */

import { MOCK_CONFIG, configUtils } from '@/__mocks__/config/mockConfig';
import type { CacheEntry, CacheStats, Logger } from './types';

export class AnalyticsCacheManager {
  private cache: Map<string, CacheEntry>;
  private defaultTTL: number;
  private maxCacheSize: number;
  private logger: Logger;
  private hitCount: number = 0;
  private missCount: number = 0;

  constructor() {
    this.cache = new Map();
    this.defaultTTL = MOCK_CONFIG.MOCK_CACHE_TTL || 5 * 60 * 1000; // 5 minutes
    this.maxCacheSize = 100;
    this.logger = configUtils.createLogger('AnalyticsCacheManager');
  }

  generateKey(method: string, params: any[]): string {
    return `${method}_${JSON.stringify(params)}`;
  }

  get(key: string): any | null {
    const cached = this.cache.get(key);
    if (!cached) {
      this.missCount++;
      return null;
    }

    if (Date.now() - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      this.missCount++;
      return null;
    }

    this.hitCount++;
    this.logger.debug(`Cache hit for ${key}`);
    return cached.data;
  }

  set(key: string, data: any, ttl: number = this.defaultTTL): void {
    // Implement LRU eviction
    if (this.cache.size >= this.maxCacheSize) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey) {
        this.cache.delete(firstKey);
      }
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });

    this.logger.debug(`Cached data for ${key} (TTL: ${ttl}ms)`);
  }

  clear(pattern: string | null = null): void {
    if (pattern) {
      const regex = new RegExp(pattern);
      for (const key of this.cache.keys()) {
        if (regex.test(key)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }

  getStats(): CacheStats {
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize,
      keys: Array.from(this.cache.keys()),
      hitRatio: this.hitCount / (this.hitCount + this.missCount) || 0,
    };
  }

  getDefaultTTL(): number {
    return this.defaultTTL;
  }
}
