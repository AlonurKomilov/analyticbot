import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AppRouter from './AppRouter';
import theme from './theme';

/**
 * Main App Component with Professional Router Architecture
 * Provides theme and routing for enterprise-grade application
 */
const App = () => {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <AppRouter />
        </ThemeProvider>
    );
};

export default App;
