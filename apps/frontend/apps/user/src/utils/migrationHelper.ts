/**
 * One-Time Token Migration Helper
 * Migrates existing tokens from localStorage to secure IndexedDB storage
 */

import { secureTokenStorage } from './secureTokenStorage';
import { authLogger } from './logger';

const MIGRATION_KEY = 'tokens_migrated_to_secure_storage_v1';

/**
 * Migrate tokens from localStorage to secure storage
 * This should be called ONCE during app initialization
 */
export async function migrateTokensOnce(): Promise<void> {
    // Check if already migrated (using a simple flag in localStorage)
    if (localStorage.getItem(MIGRATION_KEY) === 'true') {
        authLogger.log('Tokens already migrated to secure storage');
        return;
    }

    authLogger.log('Starting token migration to secure storage...');

    try {
        // List of all possible token keys used in the app
        const tokenKeys = [
            'access_token',
            'auth_token',
            'token',
            'accessToken',
            'refresh_token',
            'refreshToken',
            'user',
            'userData',
            'auth_user',
            'is_demo_user',
            'useRealAPI',
            'last_login_time'
        ];

        let migratedCount = 0;

        for (const key of tokenKeys) {
            const value = localStorage.getItem(key);

            if (value) {
                // Map old keys to new secure storage keys
                if (key === 'access_token' || key === 'auth_token' || key === 'token' || key === 'accessToken') {
                    await secureTokenStorage.setAccessToken(value, 3600); // 1 hour
                    migratedCount++;
                } else if (key === 'refresh_token' || key === 'refreshToken') {
                    await secureTokenStorage.setRefreshToken(value, 604800); // 7 days
                    migratedCount++;
                } else if (key === 'user' || key === 'userData' || key === 'auth_user') {
                    try {
                        const userData = JSON.parse(value);
                        await secureTokenStorage.setUserData(userData);
                        migratedCount++;
                    } catch {
                        // If not JSON, store as-is
                        await secureTokenStorage.setToken(key, value);
                        migratedCount++;
                    }
                } else {
                    // Other keys (flags, settings, etc.)
                    await secureTokenStorage.setToken(key, value);
                    migratedCount++;
                }

                // Remove from localStorage after successful migration
                localStorage.removeItem(key);
            }
        }

        // Mark migration as complete
        localStorage.setItem(MIGRATION_KEY, 'true');

        authLogger.log(`✅ Token migration complete! Migrated ${migratedCount} items to secure storage`);
    } catch (error) {
        authLogger.error('❌ Token migration failed:', error);
        throw error;
    }
}

/**
 * Reset migration flag (for testing/debugging only)
 * DO NOT use in production
 */
export function resetMigrationFlag(): void {
    localStorage.removeItem(MIGRATION_KEY);
    authLogger.warn('Migration flag reset - tokens will be migrated again on next app load');
}
