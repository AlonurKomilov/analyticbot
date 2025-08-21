import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme.js';
import * as Sentry from "@sentry/react";

// Development mode TWA Mock
if (!window.Telegram) {
  window.Telegram = {
    WebApp: {
      ready: () => console.log('TWA: Ready (mocked)'),
      expand: () => console.log('TWA: Expand (mocked)'),
      colorScheme: 'dark',
      initData: '',
      showAlert: (msg) => alert(msg),
      HapticFeedback: {
        impactOccurred: () => console.log('TWA: Haptic feedback (mocked)')
      }
    }
  }
}
import * as Sentry from "@sentry/react";

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme.js';
import * as Sentry from "@sentry/react";

// Development mode TWA Mock
if (!window.Telegram) {
  window.Telegram = {
    WebApp: {
      ready: () => console.log('TWA: Ready (mocked)'),
      expand: () => console.log('TWA: Expand (mocked)'),
      colorScheme: 'dark',
      initData: '',
      showAlert: (msg) => alert(msg),
      HapticFeedback: {
        impactOccurred: () => console.log('TWA: Haptic feedback (mocked)')
      }
    }
  }
}

// Sentry'ni sizning yangi DSN kalitingiz bilan ishga tushiramiz
Sentry.init({
  dsn: "https://ee3c1d2017b9bd97f484190782d92e01@o4509801364324352.ingest.us.sentry.io/4509801367732224",
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  // Performance Monitoring
  tracesSampleRate: 1.0,
  // Session Replay
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});


ReactDOM.createRoot(document.getElementById('root')).render(
  <ThemeProvider theme={theme}>
    <CssBaseline />
    <App />
  </ThemeProvider>
)
