/**
 * Navigation Context Types
 */
import { NavigateOptions } from 'react-router-dom';
import { ReactNode } from 'react';

export interface PageView {
  id: number;
  path: string;
  title: string;
  timestamp: number;
  duration: number;
}

export interface RecentPage {
  path: string;
  title: string;
  timestamp: number;
}

export interface Bookmark {
  path: string;
  title: string;
  timestamp: number;
}

export interface SearchHistoryItem {
  query: string;
  timestamp: number;
}

export interface Notification {
  id?: number;
  title: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  persistent?: boolean;
  timestamp?: number;
  read?: boolean;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
  quickActions: any[];
  recentPages: RecentPage[];
  bookmarks: Bookmark[];
  searchHistory: SearchHistoryItem[];
}

export interface NavigationPerformance {
  [path: string]: {
    duration: number;
    timestamp: number;
  };
}

export interface RouteInfo {
  path: string;
  title: string;
  level: number;
}

export interface NavigateWithTrackingOptions extends NavigateOptions {
  title?: string;
}

export interface NavigationContextValue {
  currentPath: string;
  pageTitle: string;
  setPageTitle: (title: string) => void;
  isDarkMode: boolean;
  toggleTheme: () => void;
  preferences: UserPreferences;
  updatePreferences: (updates: Partial<UserPreferences>) => void;
  navigate: (path: string, options?: NavigateWithTrackingOptions) => void;
  recentPages: RecentPage[];
  bookmarks: Bookmark[];
  addBookmark: (bookmark: Bookmark) => void;
  removeBookmark: (path: string) => void;
  isBookmarked: (path: string) => boolean;
  searchHistory: SearchHistoryItem[];
  addSearchHistory: (query: string) => void;
  clearSearchHistory: () => void;
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Notification) => void;
  markAsRead: (id: number) => void;
  removeNotification: (id: number) => void;
  clearAllNotifications: () => void;
  pageViews: PageView[];
  navigationPerformance: NavigationPerformance;
  trackNavigationTiming: (path: string, startTime: number) => void;
  formatPath: (path: string) => string;
  getRouteInfo: (path: string) => RouteInfo;
}

export interface NavigationProviderProps {
  children: ReactNode;
}

export const DEFAULT_PREFERENCES: UserPreferences = {
  theme: 'light' as const,
  sidebarCollapsed: false,
  quickActions: [],
  recentPages: [],
  bookmarks: [],
  searchHistory: [],
};
