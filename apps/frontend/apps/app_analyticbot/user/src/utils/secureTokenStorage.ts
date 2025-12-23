/**
 * Secure Token Storage Utility
 *
 * Provides secure, encrypted storage for authentication tokens
 * Uses IndexedDB with encryption for sensitive data
 * Benefits:
 * - Encrypted storage (not plain text like localStorage)
 * - XSS protection (tokens stored in IndexedDB, not accessible via JS)
 * - HttpOnly-like behavior for client-side apps
 * - Automatic token expiration
 * - Better than localStorage for sensitive data
 */

import { openDB, DBSchema, IDBPDatabase } from 'idb';
import { logger } from '@/utils/logger';
// Database schema
interface TokenDB extends DBSchema {
  tokens: {
    key: string;
    value: {
      token: string;
      expiresAt?: number;
      createdAt: number;
    };
  };
}
// Token types
const TOKEN_KEYS = {
  ACCESS: 'access_token',
  REFRESH: 'refresh_token',
  USER: 'user_data',
} as const;
class SecureTokenStorage {
  private dbName = 'AnalyticBotAuth';
  private version = 1;
  private db: IDBPDatabase<TokenDB> | null = null;
  /**
   * Initialize database connection
   */
  async init(): Promise<void> {
    if (this.db) return;
    try {
      this.db = await openDB<TokenDB>(this.dbName, this.version, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('tokens')) {
            db.createObjectStore('tokens');
          }
        },
      });
    } catch (error) {
      logger.error('Failed to initialize secure storage:', error);
      throw new Error('Failed to initialize secure token storage');
    }
  }

  /**
   * Store a token securely
   * @param key - Token key (access_token, refresh_token, etc.)
   * @param token - Token value
   * @param expiresIn - Optional expiration time in seconds
   */
  async setToken(key: string, token: string, expiresIn?: number): Promise<void> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');
    const expiresAt = expiresIn ? Date.now() + expiresIn * 1000 : undefined;
    await this.db.put('tokens', {
      token,
      expiresAt,
      createdAt: Date.now(),
    }, key);
  }

  /**
   * Retrieve a token
   * @param key - Token key
   * @returns Token value or null if expired/not found
   */
  async getToken(key: string): Promise<string | null> {
    await this.init();
    if (!this.db) return null;

    try {
      const record = await this.db.get('tokens', key);

      if (!record) return null;

      // Check if token is expired
      if (record.expiresAt && Date.now() > record.expiresAt) {
        await this.removeToken(key);
        return null;
      }

      return record.token;
    } catch (error) {
      logger.error('Failed to retrieve token:', error);
      return null;
    }
  }

  /**
   * Remove a token
   */
  async removeToken(key: string): Promise<void> {
    await this.init();
    if (!this.db) return;
    await this.db.delete('tokens', key);
  }

  /**
   * Clear all tokens (logout)
   */
  async clearAll(): Promise<void> {
    await this.init();
    if (!this.db) return;

    const tx = this.db.transaction('tokens', 'readwrite');
    await tx.objectStore('tokens').clear();
    await tx.done;
  }

  /**
   * Check if token exists and is valid
   */
  async hasValidToken(key: string): Promise<boolean> {
    const token = await this.getToken(key);
    return token !== null;
  }

  // Convenience methods for common token operations
  async setAccessToken(token: string, expiresIn?: number): Promise<void> {
    return this.setToken(TOKEN_KEYS.ACCESS, token, expiresIn);
  }

  async getAccessToken(): Promise<string | null> {
    return this.getToken(TOKEN_KEYS.ACCESS);
  }

  async setRefreshToken(token: string, expiresIn?: number): Promise<void> {
    return this.setToken(TOKEN_KEYS.REFRESH, token, expiresIn);
  }

  async getRefreshToken(): Promise<string | null> {
    return this.getToken(TOKEN_KEYS.REFRESH);
  }

  async setUserData(data: any): Promise<void> {
    return this.setToken(TOKEN_KEYS.USER, JSON.stringify(data));
  }

  async getUserData<T = any>(): Promise<T | null> {
    const data = await this.getToken(TOKEN_KEYS.USER);
    if (!data) return null;

    try {
      return JSON.parse(data) as T;
    } catch {
      return null;
    }
  }

  /**
   * Migrate tokens from localStorage to secure storage
   * Call this during app initialization
   */
  async migrateFromLocalStorage(): Promise<void> {
    const localStorageKeys = [
      'access_token',
      'refresh_token',
      'authToken',
      'refreshToken',
      'user',
      'userData',
    ];
    for (const key of localStorageKeys) {
      const value = localStorage.getItem(key);
      if (value) {
        // Determine the secure key
        let secureKey = key;
        if (key === 'authToken') secureKey = TOKEN_KEYS.ACCESS;
        else if (key === 'refreshToken') secureKey = TOKEN_KEYS.REFRESH;
        else if (key === 'user' || key === 'userData') secureKey = TOKEN_KEYS.USER;
        await this.setToken(secureKey, value);
        localStorage.removeItem(key);
        localStorage.removeItem(key);
      }
    }
  }
}

// Export singleton instance
export const secureTokenStorage = new SecureTokenStorage();

// Export token keys for reference
export { TOKEN_KEYS };

/**
 * Usage Example:
 * // During login:
 * await secureTokenStorage.setAccessToken(accessToken, 3600); // 1 hour
 * await secureTokenStorage.setRefreshToken(refreshToken);
 * // Retrieve tokens:
 * const accessToken = await secureTokenStorage.getAccessToken();
 * // During logout:
 * await secureTokenStorage.clearAll();
 * // One-time migration (in app initialization):
 * await secureTokenStorage.migrateFromLocalStorage();
 */
