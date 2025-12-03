/**
 * Telegram Login Button Component
 *
 * Integrates Telegram Login Widget with authentication system.
 * Supports auto-registration and account switching.
 */

import React, { useEffect, useRef, useState } from 'react';
import { Box, Button, Card, CardContent, Typography, Avatar } from '@mui/material';
import { Telegram as TelegramIcon, SwapHoriz as SwapHorizIcon } from '@mui/icons-material';
import { apiClient } from '@/api/client';

// Telegram auth data interface
interface TelegramAuthData {
    id: number;
    first_name: string;
    last_name?: string;
    username?: string;
    photo_url?: string;
    auth_date: number;
    hash: string;
}

// Extend window interface for Telegram callback
declare global {
    interface Window {
        onTelegramAuth?: (user: TelegramAuthData) => void;
    }
}

interface TelegramLoginButtonProps {
    onSuccess?: () => void;
    onError?: (error: string) => void;
    disabled?: boolean;
}

export const TelegramLoginButton: React.FC<TelegramLoginButtonProps> = ({
    onSuccess,
    onError,
    disabled = false
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>('');
    const [loggedInUser, setLoggedInUser] = useState<TelegramAuthData | null>(null);

    const BOT_USERNAME = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'abccontrol_bot';

    // Cleanup function to remove Telegram widget
    const cleanupTelegramWidget = () => {
        if (containerRef.current) {
            // Remove all child elements (widget iframe)
            while (containerRef.current.firstChild) {
                containerRef.current.removeChild(containerRef.current.firstChild);
            }
        }

        // Remove the Telegram script if it exists
        const existingScript = document.querySelector('script[src*="telegram.org/js/telegram-widget"]');
        if (existingScript) {
            existingScript.remove();
        }

        // Clear any Telegram-related items from localStorage
        const telegramKeys = Object.keys(localStorage).filter(key =>
            key.includes('telegram') || key.includes('Telegram')
        );
        telegramKeys.forEach(key => localStorage.removeItem(key));
    };

    // Handle Telegram authentication
    const handleTelegramAuth = async (user: TelegramAuthData) => {
        setLoading(true);
        setError('');

        try {
            // Call backend API to verify and login
            const response = await apiClient.post<{
                access_token: string;
                refresh_token?: string;
                user: any;
            }>('/auth/telegram/login', user);

            if (response && response.access_token) {
                // Store tokens and user data with correct keys
                localStorage.setItem('auth_token', response.access_token);
                localStorage.setItem('access_token', response.access_token); // Backup key

                if (response.refresh_token) {
                    localStorage.setItem('refresh_token', response.refresh_token);
                }

                localStorage.setItem('auth_user', JSON.stringify(response.user));
                localStorage.setItem('user', JSON.stringify(response.user)); // Backup key

                // Set fresh login timestamp to skip /auth/me timeout
                localStorage.setItem('last_login_time', Date.now().toString());

                // Set logged in user for display
                setLoggedInUser(user);

                // Success callback
                if (onSuccess) {
                    onSuccess();
                }

                // Redirect to dashboard with full page reload
                window.location.href = '/';
            }
        } catch (err: any) {
            const errorMessage = err.message || 'Telegram authentication failed';
            setError(errorMessage);
            if (onError) {
                onError(errorMessage);
            }
        } finally {
            setLoading(false);
        }
    };

    // Initialize Telegram widget
    const initTelegramWidget = () => {
        // Don't initialize if disabled
        if (disabled) return;

        // Cleanup any existing widget first
        cleanupTelegramWidget();

        if (!containerRef.current) return;

        // Create callback function
        const callbackName = `telegramCallback_${Date.now()}`;
        (window as any)[callbackName] = handleTelegramAuth;

        // Create script element
        const script = document.createElement('script');
        script.src = 'https://telegram.org/js/telegram-widget.js?22';
        script.setAttribute('data-telegram-login', BOT_USERNAME);
        script.setAttribute('data-size', 'large');
        script.setAttribute('data-radius', '8');
        script.setAttribute('data-onauth', `${callbackName}(user)`);
        script.setAttribute('data-request-access', 'write');
        script.async = true;

        containerRef.current.appendChild(script);
    };

    // Handle account switch
    const handleSwitchAccount = () => {
        // Clear logged in user
        setLoggedInUser(null);

        // Clear all authentication data
        localStorage.removeItem('auth_token');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('auth_user');
        localStorage.removeItem('user');
        localStorage.removeItem('last_login_time');

        // Reinitialize widget with cache-busting
        setTimeout(() => {
            initTelegramWidget();
        }, 100);
    };

    // Initialize on mount
    useEffect(() => {
        initTelegramWidget();

        return () => {
            // Cleanup on unmount
            const callbackNames = Object.keys(window).filter(key =>
                key.startsWith('telegramCallback_')
            );
            callbackNames.forEach(name => {
                delete (window as any)[name];
            });
        };
    }, []);

    return (
        <Box sx={{ width: '100%' }}>
            {error && (
                <Typography color="error" variant="body2" sx={{ mb: 2, textAlign: 'center' }}>
                    {error}
                </Typography>
            )}

            {loggedInUser && (
                <Card sx={{ mb: 2, bgcolor: 'background.paper' }}>
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            {loggedInUser.photo_url && (
                                <Avatar src={loggedInUser.photo_url} alt={loggedInUser.first_name} />
                            )}
                            <Box sx={{ flex: 1 }}>
                                <Typography variant="subtitle2">
                                    Logged in as
                                </Typography>
                                <Typography variant="body1" fontWeight="bold">
                                    {loggedInUser.first_name} {loggedInUser.last_name}
                                </Typography>
                                {loggedInUser.username && (
                                    <Typography variant="body2" color="text.secondary">
                                        @{loggedInUser.username}
                                    </Typography>
                                )}
                            </Box>
                            <Button
                                size="small"
                                startIcon={<SwapHorizIcon />}
                                onClick={handleSwitchAccount}
                                variant="outlined"
                            >
                                Switch Account
                            </Button>
                        </Box>
                    </CardContent>
                </Card>
            )}

            <Box
                ref={containerRef}
                sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    minHeight: '50px',
                    opacity: (loading || disabled) ? 0.5 : 1,
                    pointerEvents: (loading || disabled) ? 'none' : 'auto'
                }}
            />

            {loading && (
                <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mt: 2, textAlign: 'center' }}
                >
                    Authenticating...
                </Typography>
            )}

            <Typography
                variant="caption"
                color="text.secondary"
                sx={{ mt: 2, display: 'block', textAlign: 'center' }}
            >
                <TelegramIcon sx={{ fontSize: 14, verticalAlign: 'middle', mr: 0.5 }} />
                Secure login via Telegram
            </Typography>
        </Box>
    );
};

export default TelegramLoginButton;
