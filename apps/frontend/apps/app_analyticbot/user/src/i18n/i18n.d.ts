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
      mtproto: typeof import('./locales/en/mtproto.json');
      moderation: typeof import('./locales/en/moderation.json');
      storage: typeof import('./locales/en/storage.json');
      filters: typeof import('./locales/en/filters.json');
      datasource: typeof import('./locales/en/datasource.json');
    };
  }
}

export {};
