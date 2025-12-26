export const config = {
  // In dev mode, use relative URL to leverage Vite proxy
  // In production, use the full API URL
  apiBaseUrl: import.meta.env.DEV ? '/api' : (import.meta.env.VITE_API_URL || 'https://api.analyticbot.org'),
  appName: 'AnalyticBot Owner',
  version: '1.0.0',
} as const;

export default config;
