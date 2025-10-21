/**
 * Store State Type Definitions
 * Type-safe state management for Zustand stores
 */

import type {
  User,
  Channel,
  Post,
  ScheduledPost,
  AnalyticsOverview,
  GrowthMetrics,
  ReachMetrics,
  TopPost,
  PostDynamics,
  EngagementMetrics,
  BestTimeRecommendation,
  MediaFile,
  PendingMedia,
  DataSource,
  LoadingState,
  ValidationResult,
} from './models';

// ============================================================================
// Auth Store
// ============================================================================

export interface AuthState {
  // State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: {
    email: string;
    password: string;
    firstName?: string;
    lastName?: string;
  }) => Promise<void>;
  fetchUser: () => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
  updatePreferences: (preferences: Partial<User['preferences']>) => Promise<void>;
  clearError: () => void;
}

// ============================================================================
// Channel Store
// ============================================================================

export interface ChannelState {
  // State
  channels: Channel[];
  selectedChannel: Channel | null;
  isLoading: boolean;
  isValidating: boolean;
  error: string | null;
  validationError: string | null;

  // Actions
  fetchChannels: () => Promise<void>;
  addChannel: (channelData: {
    name: string;
    username: string;
    description?: string;
  }) => Promise<void>;
  updateChannel: (channelId: string, data: Partial<Channel>) => Promise<void>;
  deleteChannel: (channelId: string) => Promise<void>;
  selectChannel: (channel: Channel | null) => void;
  validateChannel: (username: string) => Promise<ValidationResult>;
  clearError: () => void;
  clearValidationError: () => void;
}

// ============================================================================
// Post Store
// ============================================================================

export interface PostState {
  // State
  posts: Post[];
  scheduledPosts: ScheduledPost[];
  currentPost: Post | null;
  isLoading: boolean;
  isScheduling: boolean;
  isPublishing: boolean;
  error: string | null;

  // Actions
  fetchPosts: (channelId: string) => Promise<void>;
  fetchScheduledPosts: (channelId: string) => Promise<void>;
  createPost: (postData: {
    channelId: string;
    content: string;
    mediaId?: string;
  }) => Promise<void>;
  schedulePost: (postData: {
    channelId: string;
    content: string;
    mediaId?: string;
    scheduledTime: string;
  }) => Promise<void>;
  updatePost: (postId: string, data: Partial<Post>) => Promise<void>;
  deletePost: (postId: string) => Promise<void>;
  publishNow: (postId: string) => Promise<void>;
  setCurrentPost: (post: Post | null) => void;
  clearError: () => void;
}

// ============================================================================
// Analytics Store
// ============================================================================

export interface AnalyticsState {
  // State
  overview: AnalyticsOverview | null;
  growth: GrowthMetrics | null;
  reach: ReachMetrics | null;
  topPosts: TopPost[];
  postDynamics: PostDynamics | null;
  engagementMetrics: EngagementMetrics | null;
  bestTimes: BestTimeRecommendation[];

  // Loading states (granular)
  isLoadingOverview: boolean;
  isLoadingGrowth: boolean;
  isLoadingReach: boolean;
  isLoadingTopPosts: boolean;
  isLoadingPostDynamics: boolean;
  isLoadingEngagement: boolean;
  isLoadingBestTimes: boolean;

  // Error states (granular)
  overviewError: string | null;
  growthError: string | null;
  reachError: string | null;
  topPostsError: string | null;
  postDynamicsError: string | null;
  engagementError: string | null;
  bestTimesError: string | null;

  // Actions
  fetchOverview: (channelId: string, period?: string) => Promise<void>;
  fetchGrowth: (channelId: string, period?: string) => Promise<void>;
  fetchReach: (channelId: string, period?: string) => Promise<void>;
  fetchTopPosts: (channelId: string, limit?: number) => Promise<void>;
  fetchPostDynamics: (postId: string) => Promise<void>;
  fetchEngagementMetrics: (channelId: string, period?: string) => Promise<void>;
  fetchBestTimes: (channelId: string) => Promise<void>;
  fetchAllAnalytics: (channelId: string, period?: string) => Promise<void>;
  clearAnalytics: () => void;
  clearErrors: () => void;
}

// ============================================================================
// Media Store
// ============================================================================

export interface MediaState {
  // State
  files: MediaFile[];
  pendingMedia: PendingMedia[];
  uploadProgress: { [key: string]: number };
  isUploading: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchFiles: (limit?: number, offset?: number) => Promise<void>;
  uploadFile: (file: File, channelId?: string) => Promise<MediaFile>;
  uploadMultipleFiles: (files: File[], channelId?: string) => Promise<MediaFile[]>;
  deleteFile: (fileId: string) => Promise<void>;
  addPendingMedia: (file: File) => void;
  removePendingMedia: (index: number) => void;
  clearPendingMedia: () => void;
  updateUploadProgress: (fileId: string, progress: number) => void;
  clearError: () => void;
}

// ============================================================================
// UI Store
// ============================================================================

export interface UIState {
  // State
  theme: 'light' | 'dark' | 'auto';
  sidebarCollapsed: boolean;
  dataSource: DataSource;
  globalLoading: boolean;
  globalError: string | null;
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    duration?: number;
  }>;

  // Modal states
  modals: {
    [key: string]: boolean;
  };

  // Actions
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setDataSource: (source: DataSource) => void;
  setGlobalLoading: (loading: boolean) => void;
  setGlobalError: (error: string | null) => void;
  addNotification: (notification: {
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    duration?: number;
  }) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  openModal: (modalId: string) => void;
  closeModal: (modalId: string) => void;
  toggleModal: (modalId: string) => void;
}

// ============================================================================
// Combined Store Types (for multi-store usage)
// ============================================================================

export interface AppStores {
  auth: AuthState;
  channels: ChannelState;
  posts: PostState;
  analytics: AnalyticsState;
  media: MediaState;
  ui: UIState;
}

// ============================================================================
// Store Action Types (for async actions)
// ============================================================================

export type AsyncAction<T = void> = () => Promise<T>;

export type AsyncActionWithParam<P, T = void> = (param: P) => Promise<T>;

// ============================================================================
// Store Selector Types
// ============================================================================

export type StoreSelector<State, Result> = (state: State) => Result;

// ============================================================================
// Zustand Store Creator Types
// ============================================================================

export type StoreCreator<State> = (
  set: (partial: Partial<State> | ((state: State) => Partial<State>)) => void,
  get: () => State
) => State;

// ============================================================================
// Store Middleware Types
// ============================================================================

export interface PersistConfig<State> {
  name: string;
  storage?: Storage;
  partialize?: (state: State) => Partial<State>;
  onRehydrateStorage?: (state: State) => void;
}

export interface DevtoolsConfig {
  name: string;
  enabled?: boolean;
}

// ============================================================================
// Loading & Error State Helpers
// ============================================================================

export interface AsyncStateSlice {
  isLoading: boolean;
  error: string | null;
  loadingState: LoadingState;
}

export interface AsyncStateActions {
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setLoadingState: (state: LoadingState) => void;
  clearError: () => void;
}

// ============================================================================
// Store Hooks Return Types
// ============================================================================

export type UseAuthStore = () => AuthState;
export type UseChannelStore = () => ChannelState;
export type UsePostStore = () => PostState;
export type UseAnalyticsStore = () => AnalyticsState;
export type UseMediaStore = () => MediaState;
export type UseUIStore = () => UIState;

// ============================================================================
// Selector Hook Types (for optimized re-renders)
// ============================================================================

export type UseAuthSelector = <T>(selector: (state: AuthState) => T) => T;
export type UseChannelSelector = <T>(selector: (state: ChannelState) => T) => T;
export type UsePostSelector = <T>(selector: (state: PostState) => T) => T;
export type UseAnalyticsSelector = <T>(selector: (state: AnalyticsState) => T) => T;
export type UseMediaSelector = <T>(selector: (state: MediaState) => T) => T;
export type UseUISelector = <T>(selector: (state: UIState) => T) => T;
