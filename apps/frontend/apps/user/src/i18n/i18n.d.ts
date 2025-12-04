/**
 * i18n Type Definitions
 *
 * Type declarations for internationalization module
 */

import 'i18next';

// Extend i18next types for proper namespace typing
declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: {
      common: typeof import('./locales/en/common.json');
      auth: typeof import('./locales/en/auth.json');
      dashboard: typeof import('./locales/en/dashboard.json');
      analytics: typeof import('./locales/en/analytics.json');
      channels: typeof import('./locales/en/channels.json');
      posts: typeof import('./locales/en/posts.json');
      settings: typeof import('./locales/en/settings.json');
      errors: typeof import('./locales/en/errors.json');
      navigation: typeof import('./locales/en/navigation.json');
    };
  }
}

export {};
