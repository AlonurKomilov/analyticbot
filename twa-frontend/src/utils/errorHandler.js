import * as Sentry from "@sentry/react";

export class ErrorHandler {
    /**
     * Centralized error handling for the application
     */
    static handleError(error, context = {}) {
        // Log to console for development
        console.error('Application Error:', {
            message: error.message,
            stack: error.stack,
            context,
            timestamp: new Date().toISOString()
        });

        // Report to Sentry
        Sentry.captureException(error, {
            tags: {
                component: context.component || 'unknown',
                action: context.action || 'unknown'
            },
            extra: context
        });

        // Show user-friendly error message
        this.showUserError(error, context);
    }

    /**
     * Handle API errors specifically
     */
    static handleApiError(error, endpoint, context = {}) {
        const apiContext = {
            ...context,
            endpoint,
            errorType: 'api_error',
            status: error.response?.status,
            statusText: error.response?.statusText
        };

        this.handleError(error, apiContext);

        // Return structured error for UI handling
        return {
            type: 'api_error',
            message: this.getErrorMessage(error),
            status: error.response?.status,
            canRetry: this.canRetry(error)
        };
    }

    /**
     * Show user-friendly error notifications
     */
    static showUserError(error, context = {}) {
        const message = this.getErrorMessage(error);
        
        // Use browser notification API if available
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Error occurred', {
                body: message,
                icon: '/favicon.ico'
            });
        } else {
            // Fallback to alert (you might want to use a toast library)
            alert(`Error: ${message}`);
        }
    }

    /**
     * Get user-friendly error message
     */
    static getErrorMessage(error) {
        if (error.response?.data?.detail) {
            return error.response.data.detail;
        }
        
        if (error.message) {
            return error.message;
        }
        
        return 'An unexpected error occurred';
    }

    /**
     * Determine if operation can be retried
     */
    static canRetry(error) {
        const retryableStatuses = [408, 429, 500, 502, 503, 504];
        return retryableStatuses.includes(error.response?.status);
    }
}

/**
 * Higher-order component for error boundary
 */
export const withErrorBoundary = (Component, fallbackComponent = null) => {
    return Sentry.withErrorBoundary(Component, {
        fallback: fallbackComponent || (({ error, resetError }) => (
            <div style={{ padding: '20px', textAlign: 'center' }}>
                <h2>Something went wrong</h2>
                <p>{error.message}</p>
                <button onClick={resetError}>Try again</button>
            </div>
        )),
        beforeCapture: (scope) => {
            scope.setTag('errorBoundary', true);
        }
    });
};

/**
 * Hook for handling async operations with error handling
 */
export const useErrorHandler = () => {
    const handleAsyncError = (asyncFn, context = {}) => {
        return async (...args) => {
            try {
                return await asyncFn(...args);
            } catch (error) {
                ErrorHandler.handleError(error, context);
                throw error; // Re-throw for component handling
            }
        };
    };

    return { handleAsyncError };
};
