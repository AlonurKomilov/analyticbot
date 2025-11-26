import React, { useEffect } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AppRouter from './AppRouter';
import theme from './theme';
import PerformanceMonitor from './utils/performanceMonitor';
import { AuthProvider } from './contexts/AuthContext';
import EnhancedErrorBoundary from '@shared/components/feedback/EnhancedErrorBoundary';

/**
 * Main App Component with Professional Router Architecture
 * Provides theme, routing, authentication, and performance monitoring for enterprise-grade application
 */
const App: React.FC = () => {
    useEffect(() => {
        // Initialize performance monitoring on app start
        const monitor = new PerformanceMonitor();
        // Note: monitor.init() is automatically called in constructor

        // Cleanup on unmount
        return () => {
            monitor.reportMetrics(); // Report final metrics
            monitor.cleanup(); // Cleanup observers
        };
    }, []);

    return (
        <EnhancedErrorBoundary
            errorContext={{ component: 'App' }}
            userFriendlyMessage="The application encountered an unexpected error. Please refresh the page to continue."
            maxRetries={2}
        >
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <AuthProvider>
                    <AppRouter />
                </AuthProvider>
            </ThemeProvider>
        </EnhancedErrorBoundary>
    );
};

export default App;
