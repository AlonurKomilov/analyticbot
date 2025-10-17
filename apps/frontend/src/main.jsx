import React from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import * as Sentry from '@sentry/react';

import App from './App.jsx';
import ErrorBoundary from './components/common/ErrorBoundary.jsx';
import theme from './theme.js'; // Use our enhanced theme
import { showDataSourceNotification } from './utils/initializeApp.js';
import HealthStartupSplash from './components/HealthStartupSplash.jsx';

// Suppress React DevTools suggestion in development
if (import.meta.env.DEV) {
  // This is expected in development - no action needed
  // React DevTools is optional and can be installed from Chrome/Firefox extension stores
}

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
// - High contrast mode support

// Render App with Error Boundary - DEFERRED until initialization completes
const container = document.getElementById('root');
const root = createRoot(container);

/**
 * Initialize app with optional comprehensive health checks
 *
 * Environment variables:
 * - VITE_FULL_HEALTH_CHECK=true       Enable comprehensive health checks (default: false)
 * - VITE_SKIP_OPTIONAL_CHECKS=false   Run optional checks too (default: true - skip them)
 * - VITE_HEALTH_CHECK_SILENT=false    Show blocking splash (default: true - silent mode)
 *
 * Silent mode (default): Health checks run in background, app renders immediately.
 *   Only shows warning banner if critical failures detected.
 *
 * Blocking mode: Shows splash screen until all checks complete.
 *   Useful for admin/debugging scenarios.
 */
const enableFullHealthCheck = import.meta.env.VITE_FULL_HEALTH_CHECK === 'true';
const skipOptionalChecks = import.meta.env.VITE_SKIP_OPTIONAL_CHECKS !== 'false'; // Default: true
const silentMode = import.meta.env.VITE_HEALTH_CHECK_SILENT !== 'false'; // Default: true

// Render the app wrapped by startup splash which handles initialization and health checks
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <HealthStartupSplash
          options={{
            fullHealthCheck: enableFullHealthCheck,
            skipOptional: skipOptionalChecks,
            silent: silentMode
          }}
        >
          <App />
        </HealthStartupSplash>
      </ThemeProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
