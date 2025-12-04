/**
 * Telegram Web App (TWA) Auto-Login Utility
 *
 * Automatically authenticates users when they open the app from Telegram bot
 * without requiring manual login via the widget.
 */

import { apiClient } from '@/api/client';

interface TelegramUser {
    id: number;
    first_name: string;
    last_name?: string;
    username?: string;
    photo_url?: string;
    language_code?: string;
}

interface TelegramWebAppData {
    initData?: string;
    initDataUnsafe?: {
        user?: TelegramUser;
        auth_date?: number;
        hash?: string;
    };
}

/**
 * Check if app is running inside Telegram
 */
export const isTelegramWebApp = (): boolean => {
    const tg = (window as any).Telegram?.WebApp;
    const hasInitData = !!tg && !!tg.initData && tg.initData.length > 0;

    // Debug logging
    console.log('🔍 Telegram WebApp Detection:', {
        hasTelegramObject: !!(window as any).Telegram,
        hasWebApp: !!tg,
        hasInitData,
        initDataLength: tg?.initData?.length || 0,
        initDataPreview: tg?.initData ? tg.initData.substring(0, 50) + '...' : 'none',
        hasInitDataUnsafe: !!tg?.initDataUnsafe,
        hasUser: !!tg?.initDataUnsafe?.user,
        platform: tg?.platform || 'unknown',
        version: tg?.version || 'unknown'
    });

    return hasInitData;
};

/**
 * Get Telegram user data from WebApp
 */
export const getTelegramUser = (): TelegramUser | null => {
    const tg = (window as any).Telegram?.WebApp as TelegramWebAppData | undefined;

    if (!tg || !tg.initDataUnsafe?.user) {
        return null;
    }

    return tg.initDataUnsafe.user;
};

/**
 * Get Telegram initData for backend verification
 */
export const getTelegramInitData = (): string | null => {
    const tg = (window as any).Telegram?.WebApp as TelegramWebAppData | undefined;
    return tg?.initData || null;
};

/**
 * Attempt to auto-login from Telegram Web App
 *
 * @returns true if login was successful, false otherwise
 */
export const autoLoginFromTelegram = async (): Promise<boolean> => {
    if (!isTelegramWebApp()) {
        return false;
    }

    // Check if we've already successfully logged in this session AND tokens still exist
    const alreadyLoggedIn = sessionStorage.getItem('twa_logged_in') === 'true';
    const hasTokens = !!localStorage.getItem('auth_token') || !!localStorage.getItem('access_token');

    if (alreadyLoggedIn && hasTokens) {
        console.log('ℹ️ TWA already logged in this session with valid tokens');
        return true;
    }

    // If session says logged in but no tokens, clear the session flag and re-login
    if (alreadyLoggedIn && !hasTokens) {
        console.log('⚠️ TWA session flag exists but tokens missing - re-authenticating');
        sessionStorage.removeItem('twa_logged_in');
    }

    const initData = getTelegramInitData();
    const user = getTelegramUser();

    if (!initData || !user) {
        console.warn('⚠️ TWA detected but no user data available');
        return false;
    }

    console.log('🔐 Auto-logging in from Telegram Web App...', {
        userId: user.id,
        username: user.username || user.first_name
    });

    try {
        // Call backend with TWA initData for verification
        const response = await apiClient.post<{
            access_token: string;
            refresh_token?: string;
            user: any;
        }>('/auth/telegram/webapp', {
            initData,
            user: {
                id: user.id,
                first_name: user.first_name,
                last_name: user.last_name,
                username: user.username,
                photo_url: user.photo_url,
                language_code: user.language_code
            }
        });

        if (response && response.access_token) {
            // Store tokens
            localStorage.setItem('auth_token', response.access_token);
            localStorage.setItem('access_token', response.access_token);

            if (response.refresh_token) {
                localStorage.setItem('refresh_token', response.refresh_token);
            }

            // Store user data
            localStorage.setItem('auth_user', JSON.stringify(response.user));
            localStorage.setItem('user', JSON.stringify(response.user));

            // Set login timestamp
            localStorage.setItem('last_login_time', Date.now().toString());

            // Mark as TWA session
            localStorage.setItem('is_twa_session', 'true');

            // Mark successful login in session storage (prevents retries)
            sessionStorage.setItem('twa_logged_in', 'true');

            // Trigger auth context update via custom event
            window.dispatchEvent(new CustomEvent('twa-auth-complete'));

            console.log('✅ TWA auto-login successful');
            return true;
        }

        console.warn('⚠️ TWA auto-login failed: no token received');
        return false;
    } catch (error: any) {
        // Log detailed error info for debugging
        console.error('❌ TWA auto-login error:', {
            message: error.message || error,
            status: error.status,
            response: error.response,
            data: error.data,
            initDataLength: initData?.length,
            userId: user?.id
        });
        return false;
    }
};

/**
 * Check if current session is from TWA
 */
export const isTWASession = (): boolean => {
    return localStorage.getItem('is_twa_session') === 'true';
};

/**
 * Initialize Telegram WebApp features
 */
export const initializeTelegramWebApp = (): void => {
    const tg = (window as any).Telegram?.WebApp;

    if (!tg) {
        return;
    }

    // Expand the app to full height
    tg.expand?.();

    // Enable closing confirmation (optional)
    tg.enableClosingConfirmation?.();

    // Set header color to match theme
    tg.setHeaderColor?.('#1e293b'); // Dark theme color

    // Set background color
    tg.setBackgroundColor?.('#0f172a');

    console.log('✅ Telegram WebApp initialized');
};
