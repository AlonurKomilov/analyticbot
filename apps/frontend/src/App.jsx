import React, { useEffect } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AppRouter from './AppRouter';
import theme from './theme';
import PerformanceMonitor from './utils/performanceMonitor';

/**
 * Main App Component with Professional Router Architecture
 * Provides theme, routing, and performance monitoring for enterprise-grade application
 */
const App = () => {
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
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <AppRouter />
        </ThemeProvider>
    );
};

export default App;
