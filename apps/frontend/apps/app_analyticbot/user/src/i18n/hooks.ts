/**
 * i18n Custom Hooks
 *
 * Convenient hooks for using translations in components
 */

import { useTranslation as useI18nTranslation } from 'react-i18next';
import { useCallback } from 'react';

type Namespace =
  | 'common'
  | 'auth'
  | 'dashboard'
  | 'analytics'
  | 'channels'
  | 'posts'
  | 'settings'
  | 'errors'
  | 'navigation';

/**
 * Hook for accessing translations with a specific namespace
 * @param ns - The namespace to use (default: 'common')
 * @returns Translation function and i18n instance
 */
export function useTranslation(ns: Namespace | Namespace[] = 'common') {
  return useI18nTranslation(ns);
}

/**
 * Hook for common translations
 */
export function useCommonTranslation() {
  return useI18nTranslation('common');
}

/**
 * Hook for auth translations
 */
export function useAuthTranslation() {
  return useI18nTranslation('auth');
}

/**
 * Hook for dashboard translations
 */
export function useDashboardTranslation() {
  return useI18nTranslation('dashboard');
}

/**
 * Hook for analytics translations
 */
export function useAnalyticsTranslation() {
  return useI18nTranslation('analytics');
}

/**
 * Hook for channels translations
 */
export function useChannelsTranslation() {
  return useI18nTranslation('channels');
}

/**
 * Hook for posts translations
 */
export function usePostsTranslation() {
  return useI18nTranslation('posts');
}

/**
 * Hook for settings translations
 */
export function useSettingsTranslation() {
  return useI18nTranslation('settings');
}

/**
 * Hook for error translations
 */
export function useErrorTranslation() {
  return useI18nTranslation('errors');
}

/**
 * Hook for navigation translations
 */
export function useNavigationTranslation() {
  return useI18nTranslation('navigation');
}

/**
 * Hook for language management
 * @returns Functions to get/set language and list of supported languages
 */
export function useLanguage() {
  const { i18n } = useI18nTranslation();

  const changeLanguage = useCallback(
    (lang: string) => {
      return i18n.changeLanguage(lang);
    },
    [i18n]
  );

  const getCurrentLanguage = useCallback(() => {
    return i18n.language;
  }, [i18n]);

  return {
    currentLanguage: i18n.language,
    changeLanguage,
    getCurrentLanguage,
    isRTL: false, // Add RTL support if needed in future
  };
}
