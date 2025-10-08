/**
 * Enhanced Error Boundary with Performance Context
 * Provides comprehensive error handling with performance impact tracking
 */

import React, { Component, createElement } from 'react';
import { Alert, AlertTitle, Button, Box, Typography } from '@mui/material';
import { ErrorOutline, Refresh, BugReport } from '@mui/icons-material';

class EnhancedErrorBoundary extends Component {
    constructor(props) {
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
        this.errorStartTime = null;
    }

    static getDerivedStateFromError(error) {
        // Update state to show error UI
        return {
            hasError: true,
            error,
            errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        };
    }

    componentDidCatch(error, errorInfo) {
        this.errorStartTime = performance.now();

        // Calculate performance impact
        const performanceImpact = this.calculatePerformanceImpact();

        this.setState({
            errorInfo,
            performanceImpact
        });

        // Log error with enhanced context
        this.logError(error, errorInfo, performanceImpact);

        // Report to error tracking service
        this.reportError(error, errorInfo, performanceImpact);
    }

    calculatePerformanceImpact() {
        const now = performance.now();
        const navigationEntry = performance.getEntriesByType('navigation')[0];

        return {
            errorTime: now,
            pageLoadTime: navigationEntry ? navigationEntry.loadEventEnd - navigationEntry.loadEventStart : 0,
            memoryUsage: performance.memory ? {
                used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
            } : null,
            userAgent: navigator.userAgent,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            url: window.location.href,
            timestamp: new Date().toISOString()
        };
    }

    logError(error, errorInfo, performanceImpact) {
        const errorData = {
            errorId: this.state.errorId,
            message: error.message,
            stack: error.stack,
            componentStack: errorInfo.componentStack,
            performanceImpact,
            retryCount: this.state.retryCount,
            props: this.props.errorContext || {}
        };

        console.group('🚨 Enhanced Error Boundary');
        console.error('Error:', error);
        console.error('Error Info:', errorInfo);
        console.log('Performance Impact:', performanceImpact);
        console.log('Full Error Data:', errorData);
        console.groupEnd();

        // Store in session storage for debugging
        try {
            const existingErrors = JSON.parse(sessionStorage.getItem('app_errors') || '[]');
            existingErrors.push(errorData);

            // Keep only last 10 errors
            if (existingErrors.length > 10) {
                existingErrors.splice(0, existingErrors.length - 10);
            }

            sessionStorage.setItem('app_errors', JSON.stringify(existingErrors));
        } catch (storageError) {
            console.warn('Failed to store error in session storage:', storageError);
        }
    }

    reportError(error, errorInfo, performanceImpact) {
        // Report to external error tracking service
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

        // Report to custom error tracking endpoint
        if (process.env.NODE_ENV === 'production') {
            fetch('/api/errors', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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
            }).catch(reportError => {
                console.error('Failed to report error:', reportError);
            });
        }

        // Custom error reporting callback
        if (this.props.onError) {
            this.props.onError(error, errorInfo, performanceImpact, this.state.errorId);
        }
    }

    handleRetry = () => {
        const newRetryCount = this.state.retryCount + 1;

        if (newRetryCount <= this.maxRetries) {
            console.log(`🔄 Retrying component render (attempt ${newRetryCount})`);

            this.setState({
                hasError: false,
                error: null,
                errorInfo: null,
                retryCount: newRetryCount,
                performanceImpact: null
            });
        } else {
            console.warn(`❌ Max retry attempts (${this.maxRetries}) reached`);
        }
    };

    handleReportBug = () => {
        const errorData = {
            errorId: this.state.errorId,
            message: this.state.error?.message,
            stack: this.state.error?.stack,
            componentStack: this.state.errorInfo?.componentStack,
            performanceImpact: this.state.performanceImpact,
            retryCount: this.state.retryCount
        };

        // Copy error data to clipboard
        navigator.clipboard.writeText(JSON.stringify(errorData, null, 2))
            .then(() => {
                alert('Error details copied to clipboard! Please paste this information when reporting the bug.');
            })
            .catch(() => {
                console.log('Error details:', errorData);
                alert('Error details logged to console. Please copy and paste when reporting the bug.');
            });
    };

    renderErrorDetails() {
        if (process.env.NODE_ENV !== 'development') return null;

        return (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                    🔍 Error Details (Development Mode)
                </Typography>
                <Typography variant="body2" component="pre" sx={{
                    fontSize: '0.75rem',
                    overflow: 'auto',
                    maxHeight: '200px',
                    bgcolor: 'grey.50',
                    p: 1,
                    borderRadius: 0.5
                }}>
                    {this.state.error?.stack}
                </Typography>

                {this.state.performanceImpact && (
                    <Box sx={{ mt: 1 }}>
                        <Typography variant="subtitle2">
                            📊 Performance Impact
                        </Typography>
                        <Typography variant="body2" component="pre" sx={{
                            fontSize: '0.75rem',
                            bgcolor: 'grey.50',
                            p: 1,
                            borderRadius: 0.5
                        }}>
                            {JSON.stringify(this.state.performanceImpact, null, 2)}
                        </Typography>
                    </Box>
                )}
            </Box>
        );
    }

    render() {
        if (this.state.hasError) {
            // Custom error UI from props
            if (this.props.fallback) {
                if (typeof this.props.fallback === 'function') {
                    return this.props.fallback(
                        this.state.error,
                        this.state.errorInfo,
                        this.handleRetry,
                        this.state.retryCount
                    );
                }
                return this.props.fallback;
            }

            // Default error UI
            return (
                <Box sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 4 }}>
                    <Alert
                        severity="error"
                        icon={<ErrorOutline />}
                        sx={{ mb: 2 }}
                    >
                        <AlertTitle>
                            Something went wrong
                        </AlertTitle>

                        <Typography variant="body2" sx={{ mb: 2 }}>
                            {this.props.userFriendlyMessage ||
                             'An unexpected error occurred. Our team has been notified and is working on a fix.'}
                        </Typography>

                        <Typography variant="caption" color="text.secondary">
                            Error ID: {this.state.errorId}
                        </Typography>

                        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {this.state.retryCount < this.maxRetries && (
                                <Button
                                    variant="outlined"
                                    size="small"
                                    startIcon={<Refresh />}
                                    onClick={this.handleRetry}
                                >
                                    Try Again {this.state.retryCount > 0 && `(${this.state.retryCount}/${this.maxRetries})`}
                                </Button>
                            )}

                            <Button
                                variant="outlined"
                                size="small"
                                startIcon={<BugReport />}
                                onClick={this.handleReportBug}
                            >
                                Report Bug
                            </Button>

                            {this.props.onGoHome && (
                                <Button
                                    variant="contained"
                                    size="small"
                                    onClick={this.props.onGoHome}
                                >
                                    Go Home
                                </Button>
                            )}
                        </Box>
                    </Alert>

                    {this.renderErrorDetails()}
                </Box>
            );
        }

        return this.props.children;
    }
}

// Higher-order component for error boundary wrapping
export const withErrorBoundary = (WrappedComponent, errorBoundaryProps = {}) => {
    const WithErrorBoundaryComponent = (props) => {
        return (
            <EnhancedErrorBoundary {...errorBoundaryProps}>
                <WrappedComponent {...props} />
            </EnhancedErrorBoundary>
        );
    };

    WithErrorBoundaryComponent.displayName = `withErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name})`;

    return WithErrorBoundaryComponent;
};

// Hook for error boundary context
export const useErrorHandler = () => {
    const handleError = (error, errorInfo = {}) => {
        // Throw error to be caught by nearest error boundary
        throw new Error(`Manual error: ${error.message || error}`);
    };

    const reportError = (error, context = {}) => {
        console.error('Manual error report:', error, context);

        // Report to analytics
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

// Error boundary for route components
export const RouteErrorBoundary = ({ children, routeName }) => {
    return (
        <EnhancedErrorBoundary
            errorContext={{ route: routeName }}
            userFriendlyMessage={`There was an error loading the ${routeName} page. Please try refreshing or navigate to another page.`}
            onGoHome={() => window.location.href = '/'}
        >
            {children}
        </EnhancedErrorBoundary>
    );
};

// Global error handler setup
export const setupGlobalErrorHandling = () => {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', event => {
        console.error('Unhandled promise rejection:', event.reason);

        // Report to analytics
        if (window.gtag) {
            window.gtag('event', 'exception', {
                description: `Unhandled promise rejection: ${event.reason}`,
                fatal: false,
                custom_parameter: {
                    type: 'unhandled_promise_rejection',
                    url: window.location.href
                }
            });
        }

        // Prevent default browser error handling
        event.preventDefault();
    });

    // Handle global errors
    window.addEventListener('error', event => {
        console.error('Global error:', event.error);

        // Report to analytics
        if (window.gtag) {
            window.gtag('event', 'exception', {
                description: `Global error: ${event.error?.message || event.message}`,
                fatal: false,
                custom_parameter: {
                    type: 'global_error',
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno,
                    url: window.location.href
                }
            });
        }
    });
};

export default EnhancedErrorBoundary;
