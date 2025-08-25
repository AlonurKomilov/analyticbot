import React from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import * as Sentry from '@sentry/react';

import App from './App.jsx';

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

// Material-UI Theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          margin: 0,
          padding: 0,
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
        },
      },
    },
  },
});

// Render App
const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
