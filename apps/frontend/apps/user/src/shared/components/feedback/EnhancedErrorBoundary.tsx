/**
 * Enhanced Error Boundary with Performance Context
 * Provides comprehensive error handling with performance impact tracking
 */

import React, { Component, ReactNode, ErrorInfo } from 'react';
import { Alert, AlertTitle, Button, Box, Typography } from '@mui/material';
import { ErrorOutline, Refresh, BugReport } from '@mui/icons-material';
import { uiLogger } from '@/utils/logger';

// Extend Window interface for gtag
declare global {
    interface Window {
        gtag?: (
            command: string,
            eventName: string,
            params?: Record<string, any>
        ) => void;
    }
    interface Performance {
        memory?: {
            usedJSHeapSize: number;
            totalJSHeapSize: number;
            jsHeapSizeLimit: number;
        };
    }
}

// Extend PerformanceEntry for navigation timing
interface PerformanceNavigationTiming extends PerformanceEntry {
    loadEventEnd: number;
    loadEventStart: number;
}

interface PerformanceImpact {
    errorTime: number;
    pageLoadTime: number;
    memoryUsage: {
        used: number;
        total: number;
        limit: number;
    } | null;
    userAgent: string;
    viewport: {
        width: number;
        height: number;
    };
    url: string;
    timestamp: string;
}

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
    errorId: string | null;
    retryCount: number;
    performanceImpact: PerformanceImpact | null;
}

interface ErrorBoundaryProps {
    children: ReactNode;
    maxRetries?: number;
    fallback?: ReactNode | ((
        error: Error | null,
        errorInfo: ErrorInfo | null,
        retry: () => void,
        retryCount: number
    ) => ReactNode);
    userFriendlyMessage?: string;
    errorContext?: Record<string, any>;
    onError?: (
        error: Error,
        errorInfo: ErrorInfo,
        performanceImpact: PerformanceImpact,
        errorId: string
    ) => void;
    onGoHome?: () => void;
}

class EnhancedErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
    private maxRetries: number;
    // Performance tracking for error timing
    // private errorStartTime: number | null;

    constructor(props: ErrorBoundaryProps) {
        super(props);

        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
            errorId: null,
            retryCount: 0,
            performanceImpact: null
        };

        this.maxRetries = props.maxRetries || 3;
        // this.errorStartTime = null;
    }

    static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
        return {
            hasError: true,
            error,
            errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        // Track performance impact at error time
        const performanceImpact = this.calculatePerformanceImpact();

        this.setState({ errorInfo, performanceImpact });
        this.logError(error, errorInfo, performanceImpact);
        this.reportError(error, errorInfo, performanceImpact);
    }

    calculatePerformanceImpact(): PerformanceImpact {
        const now = performance.now();
        const navigationEntries = performance.getEntriesByType('navigation');
        const navigationEntry = navigationEntries[0] as PerformanceNavigationTiming | undefined;

        return {
            errorTime: now,
            pageLoadTime: navigationEntry ? navigationEntry.loadEventEnd - navigationEntry.loadEventStart : 0,
            memoryUsage: performance.memory ? {
                used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
            } : null,
            userAgent: navigator.userAgent,
            viewport: { width: window.innerWidth, height: window.innerHeight },
            url: window.location.href,
            timestamp: new Date().toISOString()
        };
    }

    logError(error: Error, errorInfo: ErrorInfo, performanceImpact: PerformanceImpact): void {
        const errorData = {
            errorId: this.state.errorId,
            message: error.message,
            stack: error.stack,
            componentStack: errorInfo.componentStack,
            performanceImpact,
            retryCount: this.state.retryCount,
            props: this.props.errorContext || {}
        };

        uiLogger.error('Enhanced Error Boundary', {
            error: error.toString(),
            errorStack: error.stack,
            componentStack: errorInfo.componentStack,
            performanceImpact,
            errorData
        });

        try {
            const existingErrors = JSON.parse(sessionStorage.getItem('app_errors') || '[]');
            existingErrors.push(errorData);
            if (existingErrors.length > 10) existingErrors.splice(0, existingErrors.length - 10);
            sessionStorage.setItem('app_errors', JSON.stringify(existingErrors));
        } catch (storageError) {
            uiLogger.warn('Failed to store error in session storage', { error: storageError });
        }
    }

    reportError(error: Error, errorInfo: ErrorInfo, performanceImpact: PerformanceImpact): void {
        if (typeof window !== 'undefined' && window.gtag) {
            window.gtag('event', 'exception', {
                description: error.toString(),
                fatal: false,
                custom_parameter: {
                    component_stack: errorInfo.componentStack,
                    error_id: this.state.errorId,
                    retry_count: this.state.retryCount,
                    memory_usage: performanceImpact.memoryUsage?.used,
                    page_load_time: performanceImpact.pageLoadTime
                }
            });
        }

        if (process.env.NODE_ENV === 'production') {
            fetch('/api/errors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    errorId: this.state.errorId,
                    message: error.message,
                    stack: error.stack,
                    componentStack: errorInfo.componentStack,
                    performanceImpact,
                    retryCount: this.state.retryCount,
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            }).catch((reportError) => {
                uiLogger.error('Failed to report error', { error: reportError });
            });
        }

        if (this.props.onError && this.state.errorId) {
            this.props.onError(error, errorInfo, performanceImpact, this.state.errorId);
        }
    }

    handleRetry = (): void => {
        const newRetryCount = this.state.retryCount + 1;

        if (newRetryCount <= this.maxRetries) {
            uiLogger.debug('Retrying component render', { attempt: newRetryCount });
            this.setState({ hasError: false, error: null, errorInfo: null, retryCount: newRetryCount, performanceImpact: null });
        } else {
            uiLogger.warn('Max retry attempts reached', { maxRetries: this.maxRetries });
        }
    };

    handleReportBug = (): void => {
        const errorData = {
            errorId: this.state.errorId,
            message: this.state.error?.message,
            stack: this.state.error?.stack,
            componentStack: this.state.errorInfo?.componentStack,
            performanceImpact: this.state.performanceImpact,
            retryCount: this.state.retryCount
        };

        navigator.clipboard.writeText(JSON.stringify(errorData, null, 2))
            .then(() => alert('Error details copied to clipboard!'))
            .catch(() => {
                uiLogger.debug('Error details', { errorData });
                alert('Error details logged.');
            });
    };

    renderErrorDetails(): ReactNode {
        if (process.env.NODE_ENV !== 'development') return null;

        return (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>🔍 Error Details (Development Mode)</Typography>
                <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', overflow: 'auto', maxHeight: '200px', bgcolor: 'grey.50', p: 1, borderRadius: 0.5 }}>
                    {this.state.error?.stack}
                </Typography>
                {this.state.performanceImpact && (
                    <Box sx={{ mt: 1 }}>
                        <Typography variant="subtitle2">📊 Performance Impact</Typography>
                        <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', bgcolor: 'grey.50', p: 1, borderRadius: 0.5 }}>
                            {JSON.stringify(this.state.performanceImpact, null, 2)}
                        </Typography>
                    </Box>
                )}
            </Box>
        );
    }

    render(): ReactNode {
        if (this.state.hasError) {
            if (this.props.fallback) {
                if (typeof this.props.fallback === 'function') {
                    return this.props.fallback(this.state.error, this.state.errorInfo, this.handleRetry, this.state.retryCount);
                }
                return this.props.fallback;
            }

            return (
                <Box sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 4 }}>
                    <Alert severity="error" icon={<ErrorOutline />} sx={{ mb: 2 }}>
                        <AlertTitle>Something went wrong</AlertTitle>
                        <Typography variant="body2" sx={{ mb: 2 }}>
                            {this.props.userFriendlyMessage || 'An unexpected error occurred. Our team has been notified and is working on a fix.'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">Error ID: {this.state.errorId}</Typography>
                        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {this.state.retryCount < this.maxRetries && (
                                <Button variant="outlined" size="small" startIcon={<Refresh />} onClick={this.handleRetry}>
                                    Try Again {this.state.retryCount > 0 && `(${this.state.retryCount}/${this.maxRetries})`}
                                </Button>
                            )}
                            <Button variant="outlined" size="small" startIcon={<BugReport />} onClick={this.handleReportBug}>Report Bug</Button>
                            {this.props.onGoHome && <Button variant="contained" size="small" onClick={this.props.onGoHome}>Go Home</Button>}
                        </Box>
                    </Alert>
                    {this.renderErrorDetails()}
                </Box>
            );
        }

        return this.props.children;
    }
}

export const withErrorBoundary = <P extends object>(
    WrappedComponent: React.ComponentType<P>,
    errorBoundaryProps: Omit<ErrorBoundaryProps, 'children'> = {}
): React.FC<P> => {
    const WithErrorBoundaryComponent: React.FC<P> = (props) => (
        <EnhancedErrorBoundary {...errorBoundaryProps}>
            <WrappedComponent {...props} />
        </EnhancedErrorBoundary>
    );

    WithErrorBoundaryComponent.displayName = `withErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;
    return WithErrorBoundaryComponent;
};

export const useErrorHandler = () => {
    const handleError = (error: Error | string, _errorInfo: Record<string, any> = {}): never => {
        const errorMessage = typeof error === 'string' ? error : error.message;
        throw new Error(`Manual error: ${errorMessage}`);
    };

    const reportError = (error: Error | string, context: Record<string, any> = {}): void => {
        uiLogger.error('Manual error report', { error, context });
        if (typeof window !== 'undefined' && window.gtag) {
            window.gtag('event', 'exception', {
                description: error.toString(),
                fatal: false,
                custom_parameter: context
            });
        }
    };

    return { handleError, reportError };
};

interface RouteErrorBoundaryProps {
    children: ReactNode;
    routeName: string;
}

export const RouteErrorBoundary: React.FC<RouteErrorBoundaryProps> = ({ children, routeName }) => (
    <EnhancedErrorBoundary
        errorContext={{ route: routeName }}
        userFriendlyMessage={`There was an error loading the ${routeName} page. Please try refreshing or navigate to another page.`}
        onGoHome={() => { window.location.href = '/'; }}
    >
        {children}
    </EnhancedErrorBoundary>
);

export const setupGlobalErrorHandling = (): void => {
    window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
        uiLogger.error('Unhandled promise rejection', { reason: event.reason });
        if (window.gtag) {
            window.gtag('event', 'exception', {
                description: `Unhandled promise rejection: ${event.reason}`,
                fatal: false,
                custom_parameter: { type: 'unhandled_promise_rejection', url: window.location.href }
            });
        }
        event.preventDefault();
    });

    window.addEventListener('error', (event: ErrorEvent) => {
        uiLogger.error('Global error', { error: event.error, message: event.message });
        if (window.gtag) {
            window.gtag('event', 'exception', {
                description: `Global error: ${event.error?.message || event.message}`,
                fatal: false,
                custom_parameter: { type: 'global_error', filename: event.filename, lineno: event.lineno, colno: event.colno, url: window.location.href }
            });
        }
    });
};

export default EnhancedErrorBoundary;
