import { useState, useEffect } from 'react';
import { useUIStore } from '../stores';

/**
 * Hook for managing API failure dialog state
 *
 * This hook monitors for API connection failures and provides
 * methods to handle user responses to connection issues.
 */
export const useApiFailureDialog = () => {
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [currentError, setCurrentError] = useState(null);
    const [isRetrying, setIsRetrying] = useState(false);

    const { isGlobalLoading } = useUIStore();

    // Monitor for API connection errors
    // TODO: Implement proper error tracking in UI store when migrating error handling
    useEffect(() => {
        // Note: Error tracking moved to individual stores (analytics, channels, etc.)
        // This hook will be refactored to use proper error state when available
        const error = null; // globalLoading.error was removed during TypeScript migration

        if (error && error.type === 'API_CONNECTION_FAILED') {
            setCurrentError(error);
            setIsDialogOpen(true);
        }
    }, [isGlobalLoading]);

    const handleRetryConnection = async () => {
        setIsRetrying(true);
        try {
            // Retry logic would be implemented in the relevant store
            // For now, just close the dialog
            handleCloseDialog();
        } catch (error) {
            console.error('Retry failed:', error);
            // Update error state for display
            setCurrentError({
                ...currentError,
                retryCount: (currentError.retryCount || 0) + 1,
                lastRetryError: error
            });
        } finally {
            setIsRetrying(false);
        }
    };

    const handleSwitchToMock = async () => {
        // No longer support switching to mock data - redirect to demo login instead
        const demoLoginUrl = `/login?demo=true&redirect=${encodeURIComponent(window.location.pathname)}`;
        window.location.href = demoLoginUrl;
    };

    const handleCloseDialog = () => {
        setIsDialogOpen(false);
        setCurrentError(null);
        setIsRetrying(false);
        // Error will be cleared when next operation succeeds
    };

    return {
        isDialogOpen,
        currentError,
        isRetrying,
        handleRetryConnection,
        handleSwitchToMock,
        handleCloseDialog
    };
};

export default useApiFailureDialog;
