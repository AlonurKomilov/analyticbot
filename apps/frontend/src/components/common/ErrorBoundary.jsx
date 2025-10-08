import React from 'react';
import { Box, Typography, Button, Alert, Card, CardContent } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import BugReportIcon from '@mui/icons-material/BugReport';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        this.setState({
            error: error,
            errorInfo: errorInfo
        });

        // Log error for debugging
        console.error('ErrorBoundary caught an error:', error, errorInfo);

        // You can also send error to error reporting service here
        if (window.Sentry) {
            window.Sentry.captureException(error, {
                contexts: { errorBoundary: { componentStack: errorInfo.componentStack } }
            });
        }
    }

    handleReload = () => {
        window.location.reload();
    };

    handleRetry = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    render() {
        if (this.state.hasError) {
            const isNetworkError = this.state.error?.name === 'NetworkError' ||
                                 this.state.error?.message?.includes('fetch');

            return (
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minHeight: '400px',
                        p: 3,
                        textAlign: 'center'
                    }}
                    role="alert"
                    aria-labelledby="error-title"
                    aria-describedby="error-description"
                >
                    <Card sx={{ maxWidth: 500, width: '100%' }}>
                        <CardContent sx={{ p: 4 }}>
                            <BugReportIcon
                                sx={{ fontSize: 64, color: 'error.main', mb: 2 }}
                                aria-hidden="true"
                            />

                            <Typography
                                variant="h1"
                                id="error-title"
                                sx={{ fontSize: '1.5rem', mb: 2, fontWeight: 'bold' }}
                            >
                                {isNetworkError ? 'Connection Problem' : 'Oops! Something went wrong'}
                            </Typography>

                            <Typography
                                variant="body1"
                                id="error-description"
                                color="text.secondary"
                                sx={{ mb: 3 }}
                            >
                                {isNetworkError
                                    ? 'Unable to connect to our servers. Please check your internet connection and try again.'
                                    : 'We encountered an unexpected error. Our team has been notified and is working on a fix.'
                                }
                            </Typography>

                            {process.env.NODE_ENV === 'development' && this.state.error && (
                                <Alert severity="error" sx={{ mb: 3, textAlign: 'left' }}>
                                    <Box sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                                        <Typography variant="body2" component="div" sx={{ fontFamily: 'inherit', fontSize: 'inherit' }}>
                                            <strong>Error:</strong> {this.state.error.toString()}
                                        </Typography>
                                        <Typography variant="body2" component="div" sx={{ fontFamily: 'inherit', fontSize: 'inherit', mt: 1 }}>
                                            <strong>Component Stack:</strong>
                                        </Typography>
                                        <pre style={{
                                            whiteSpace: 'pre-wrap',
                                            fontSize: '0.7rem',
                                            marginTop: '8px',
                                            fontFamily: 'inherit',
                                            margin: '8px 0 0 0',
                                            padding: 0,
                                            background: 'transparent',
                                            border: 'none'
                                        }}>
                                            {this.state.errorInfo?.componentStack}
                                        </pre>
                                    </Box>
                                </Alert>
                            )}

                            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                                <Button
                                    variant="contained"
                                    onClick={this.handleRetry}
                                    startIcon={<RefreshIcon />}
                                    sx={{
                                        '&:focus-visible': {
                                            outline: '2px solid #fff',
                                            outlineOffset: '2px'
                                        }
                                    }}
                                >
                                    Try Again
                                </Button>

                                <Button
                                    variant="outlined"
                                    onClick={this.handleReload}
                                    sx={{
                                        '&:focus-visible': {
                                            outline: '2px solid #2196F3',
                                            outlineOffset: '2px'
                                        }
                                    }}
                                >
                                    Reload Page
                                </Button>
                            </Box>

                            <Typography
                                variant="caption"
                                color="text.secondary"
                                sx={{ display: 'block', mt: 2 }}
                            >
                                If the problem persists, please contact support or try refreshing the page.
                            </Typography>
                        </CardContent>
                    </Card>
                </Box>
            );
        }

        return this.props.children;
    }
}

// Higher-order component for easier usage
export const withErrorBoundary = (Component, fallbackComponent = null) => {
    const WrappedComponent = (props) => (
        <ErrorBoundary fallback={fallbackComponent}>
            <Component {...props} />
        </ErrorBoundary>
    );

    WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
    return WrappedComponent;
};

export default ErrorBoundary;
