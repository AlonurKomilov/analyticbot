import React from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import * as Sentry from '@sentry/react';

import App from './App.jsx';
import ErrorBoundary from './components/common/ErrorBoundary.jsx';
import theme from './theme.js'; // Use our enhanced theme
import { initializeApp, showDataSourceNotification } from './utils/initializeApp.js';

// Initialize Sentry (only if DSN is provided)
if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.MODE,
    tracesSampleRate: 0.1,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration(),
    ],
  });
}

// Initialize app early
initializeApp().then((result) => {
  if (import.meta.env.DEV) {
    console.log('🚀 App initialized:', result);
  }
  
  // Show notification about data source
  if (result.dataSource === 'mock' && result.error) {
    showDataSourceNotification('mock', 'api_unavailable');
  }
});

// TWA Mock for development
const mockTelegram = {
  WebApp: {
    ready: () => console.log('🤖 TWA Mock: ready()'),
    expand: () => console.log('🤖 TWA Mock: expand()'),
    close: () => console.log('🤖 TWA Mock: close()'),
    MainButton: {
      setText: (text) => console.log('🤖 TWA Mock: MainButton.setText()', text),
      show: () => console.log('🤖 TWA Mock: MainButton.show()'),
      hide: () => console.log('🤖 TWA Mock: MainButton.hide()'),
      onClick: () => console.log('🤖 TWA Mock: MainButton.onClick()'),
    },
    BackButton: {
      show: () => console.log('🤖 TWA Mock: BackButton.show()'),
      hide: () => console.log('🤖 TWA Mock: BackButton.hide()'),
      onClick: () => console.log('🤖 TWA Mock: BackButton.onClick()'),
    },
    initDataUnsafe: {
      user: {
        id: 123456789,
        first_name: 'Dev',
        last_name: 'User',
        username: 'devuser',
        language_code: 'en'
      }
    },
    platform: 'web',
    version: '6.7'
  }
};

// Set up Telegram WebApp
if (typeof window !== 'undefined') {
  window.Telegram = window.Telegram || mockTelegram;
  
  // Initialize TWA
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
    }
}

// Enhanced Material-UI Theme is now imported from theme.js
// The theme includes:
// - High contrast colors (WCAG AA compliance)
// - Enhanced focus indicators
// - Proper touch target sizes (44px minimum)
// - Reduced motion support
// - High contrast mode support// Render App with Error Boundary
const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
