import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import locale files
import enCommon from './locales/en/common.json';
import enAuth from './locales/en/auth.json';
import enDashboard from './locales/en/dashboard.json';
import enAnalytics from './locales/en/analytics.json';
import enChannels from './locales/en/channels.json';
import enPosts from './locales/en/posts.json';
import enSettings from './locales/en/settings.json';
import enErrors from './locales/en/errors.json';
import enNavigation from './locales/en/navigation.json';

import ruCommon from './locales/ru/common.json';
import ruAuth from './locales/ru/auth.json';
import ruDashboard from './locales/ru/dashboard.json';
import ruAnalytics from './locales/ru/analytics.json';
import ruChannels from './locales/ru/channels.json';
import ruPosts from './locales/ru/posts.json';
import ruSettings from './locales/ru/settings.json';
import ruErrors from './locales/ru/errors.json';
import ruNavigation from './locales/ru/navigation.json';

import uzCommon from './locales/uz/common.json';
import uzAuth from './locales/uz/auth.json';
import uzDashboard from './locales/uz/dashboard.json';
import uzAnalytics from './locales/uz/analytics.json';
import uzChannels from './locales/uz/channels.json';
import uzPosts from './locales/uz/posts.json';
import uzSettings from './locales/uz/settings.json';
import uzErrors from './locales/uz/errors.json';
import uzNavigation from './locales/uz/navigation.json';

export const resources = {
  en: {
    common: enCommon,
    auth: enAuth,
    dashboard: enDashboard,
    analytics: enAnalytics,
    channels: enChannels,
    posts: enPosts,
    settings: enSettings,
    errors: enErrors,
    navigation: enNavigation,
  },
  ru: {
    common: ruCommon,
    auth: ruAuth,
    dashboard: ruDashboard,
    analytics: ruAnalytics,
    channels: ruChannels,
    posts: ruPosts,
    settings: ruSettings,
    errors: ruErrors,
    navigation: ruNavigation,
  },
  uz: {
    common: uzCommon,
    auth: uzAuth,
    dashboard: uzDashboard,
    analytics: uzAnalytics,
    channels: uzChannels,
    posts: uzPosts,
    settings: uzSettings,
    errors: uzErrors,
    navigation: uzNavigation,
  },
};

export const supportedLanguages = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
  { code: 'ru', name: 'Russian', nativeName: 'Русский', flag: '🇷🇺' },
  { code: 'uz', name: 'Uzbek', nativeName: "O'zbekcha", flag: '🇺🇿' },
] as const;

export type SupportedLanguage = (typeof supportedLanguages)[number]['code'];

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    defaultNS: 'common',
    ns: [
      'common',
      'auth',
      'dashboard',
      'analytics',
      'channels',
      'posts',
      'settings',
      'errors',
      'navigation',
    ],
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'analyticbot-language',
    },
    react: {
      useSuspense: false,
    },
  });

// Export custom hooks for convenient usage
export * from './hooks';

export default i18n;
