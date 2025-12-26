export const config = {
  apiBaseUrl: import.meta.env.VITE_API_URL || 'https://api.analyticbot.org',
  appName: 'AnalyticBot Owner',
  version: '1.0.0',
} as const;

export default config;
