import { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';

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

    const {
        ui,
        switchToMockWithUserConsent,
        retryApiConnection,
        clearError
    } = useAppStore();

    // Monitor for API connection errors
    useEffect(() => {
        const error = ui.fetchData?.error;

        if (error && error.type === 'API_CONNECTION_FAILED') {
            setCurrentError(error);
            setIsDialogOpen(true);
        }
    }, [ui.fetchData?.error]);

    const handleRetryConnection = async () => {
        setIsRetrying(true);
        try {
            await retryApiConnection();
            // If successful, close dialog
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
        // Clear the error from the store
        clearError('fetchData');
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
