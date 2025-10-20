import { useState, useEffect } from 'react';
import { useUIStore } from '../stores';

/**
 * API Error type
 */
interface APIError {
    type: string;
    message: string;
    retryCount?: number;
    lastRetryError?: unknown;
}

/**
 * useApiFailureDialog hook return type
 */
export interface UseApiFailureDialogReturn {
    isDialogOpen: boolean;
    currentError: APIError | null;
    isRetrying: boolean;
    handleRetryConnection: () => Promise<void>;
    handleSwitchToMock: () => Promise<void>;
    handleCloseDialog: () => void;
}

/**
 * Hook for managing API failure dialog state
 *
 * This hook monitors for API connection failures and provides
 * methods to handle user responses to connection issues.
 */
export const useApiFailureDialog = (): UseApiFailureDialogReturn => {
    const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
    const [currentError, setCurrentError] = useState<APIError | null>(null);
    const [isRetrying, setIsRetrying] = useState<boolean>(false);

    const { isGlobalLoading } = useUIStore();

    // Monitor for API connection errors
    // TODO: Implement proper error tracking in UI store when migrating error handling
    useEffect(() => {
        // Note: Error tracking moved to individual stores (analytics, channels, etc.)
        // This hook will be refactored to use proper error state when available
        // const error: APIError | null = null; // globalLoading.error was removed during TypeScript migration

        // Temporarily disabled until error tracking is properly implemented in stores
        // if (error?.type === 'API_CONNECTION_FAILED') {
        //     setCurrentError(error);
        //     setIsDialogOpen(true);
        // }
    }, [isGlobalLoading]);

    const handleRetryConnection = async (): Promise<void> => {
        setIsRetrying(true);
        try {
            // Retry logic would be implemented in the relevant store
            // For now, just close the dialog
            handleCloseDialog();
        } catch (error) {
            console.error('Retry failed:', error);
            // Update error state for display
            if (currentError) {
                setCurrentError({
                    ...currentError,
                    retryCount: (currentError.retryCount || 0) + 1,
                    lastRetryError: error
                });
            }
        } finally {
            setIsRetrying(false);
        }
    };

    const handleSwitchToMock = async (): Promise<void> => {
        // No longer support switching to mock data - redirect to demo login instead
        const demoLoginUrl = `/login?demo=true&redirect=${encodeURIComponent(window.location.pathname)}`;
        window.location.href = demoLoginUrl;
    };

    const handleCloseDialog = (): void => {
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
