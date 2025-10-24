/**
 * API Type Definitions
 * Comprehensive types for all API requests and responses
 */

// ============================================================================
// Common Types
// ============================================================================

export interface ApiResponse<T = unknown> {
  data?: T;
  message?: string;
  success?: boolean;
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
  details?: Record<string, unknown>;
}

// ============================================================================
// Authentication Types
// ============================================================================

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
  username?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
  user: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export type UserRole = 'viewer' | 'user' | 'moderator' | 'admin' | 'owner';

export interface User {
  id: string;
  email: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  role: UserRole;
  isActive: boolean;
  createdAt: string;
  updatedAt?: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  theme?: 'light' | 'dark' | 'auto';
  language?: string;
  notifications?: boolean;
  timezone?: string;
}

// ============================================================================
// Channel Types
// ============================================================================

export interface Channel {
  id: string;
  name: string;
  telegramId: string;
  username?: string;
  description?: string;
  subscriberCount: number;
  isActive: boolean;
  isVerified?: boolean;
  createdAt: string;
  updatedAt?: string;
  metrics?: ChannelMetrics;
}

export interface ChannelMetrics {
  totalPosts: number;
  totalViews: number;
  totalShares: number;
  engagementRate: number;
  growthRate: number;
}

export interface CreateChannelRequest {
  name: string;
  telegramId?: string;
  username: string;
  description?: string;
}

export interface UpdateChannelRequest {
  name?: string;
  description?: string;
  isActive?: boolean;
}

export interface ChannelValidationResponse {
  valid: boolean;
  exists?: boolean;
  channelData?: {
    id: string;
    title: string;
    subscriberCount: number;
    description?: string;
  };
  error?: string;
}

// ============================================================================
// Post Types
// ============================================================================

export type PostStatus = 'draft' | 'scheduled' | 'publishing' | 'published' | 'failed';

export interface Post {
  id: string;
  channelId: string;
  content: string;
  mediaId?: string;
  mediaUrl?: string;
  scheduledTime?: string;
  publishedTime?: string;
  status: PostStatus;
  views?: number;
  shares?: number;
  reactions?: number;
  createdAt: string;
  updatedAt?: string;
}

export interface CreatePostRequest {
  channelId: string;
  content: string;
  mediaId?: string;
  scheduledTime?: string;
}

export interface UpdatePostRequest {
  content?: string;
  mediaId?: string;
  scheduledTime?: string;
  status?: PostStatus;
}

export interface SchedulePostRequest extends CreatePostRequest {
  scheduledTime: string;
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface AnalyticsOverview {
  totalViews: number;
  totalShares: number;
  totalReactions: number;
  engagementRate: number;
  growthRate: number;
  reachScore: number;
  viralityScore?: number;
  timestamp: string;
}

export interface GrowthMetrics {
  subscriberGrowth: number;
  subscriberGrowthRate: number;
  viewsGrowth: number;
  viewsGrowthRate: number;
  engagementGrowth: number;
  engagementGrowthRate: number;
  period: string;
  data: GrowthDataPoint[];
}

export interface GrowthDataPoint {
  date: string;
  subscribers: number;
  views: number;
  engagement: number;
}

export interface ReachMetrics {
  totalReach: number;
  organicReach: number;
  viralReach: number;
  reachRate: number;
  impressions: number;
  uniqueViewers: number;
}

export interface TopPost {
  id: string;
  content: string;
  views: number;
  shares: number;
  reactions: number;
  engagementRate: number;
  publishedTime: string;
  viralityScore?: number;
}

export interface PostDynamics {
  postId: string;
  views: number[];
  shares: number[];
  reactions: number[];
  timestamps: string[];
  engagementRate: number;
  peakTime?: string;
}

export interface RealTimeMetrics {
  metrics: RealTimeDataPoint[];
  timestamp: string;
}

export interface RealTimeDataPoint {
  timestamp: string;
  views: number;
  activeUsers: number;
  engagementRate: number;
}

export interface Alert {
  id: string;
  type: 'warning' | 'error' | 'info';
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  resolved: boolean;
}

export interface AnalyticsPeriod {
  from: string;
  to: string;
  period: number; // days
}

export interface BatchAnalyticsResponse {
  overview: AnalyticsOverview;
  growth: GrowthMetrics;
  reach: ReachMetrics;
  topPosts: TopPost[];
  realTime: RealTimeMetrics;
  alerts: Alert[];
  timestamp: string;
}

// ============================================================================
// Media Types
// ============================================================================

export type MediaType = 'image' | 'video' | 'document' | 'audio';

export interface MediaFile {
  id: string;
  filename: string;
  originalFilename: string;
  mimeType: string;
  size: number;
  type: MediaType;
  url: string;
  thumbnailUrl?: string;
  width?: number;
  height?: number;
  duration?: number;
  uploadedAt: string;
  uploadedBy: string;
}

export interface UploadResponse {
  file: MediaFile;
  message?: string;
}

export interface UploadProgress {
  progress: number;
  loaded: number;
  total: number;
  speed?: number;
  error?: string;
}

export interface StorageFilesResponse {
  files: MediaFile[];
  total: number;
  limit: number;
  offset: number;
}

// ============================================================================
// System Types
// ============================================================================

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version?: string;
  timestamp: string;
  services?: {
    database: 'up' | 'down';
    redis?: 'up' | 'down';
    telegram?: 'up' | 'down';
  };
}

export interface InitialDataResponse {
  user: User;
  channels: Channel[];
  recentPosts: Post[];
  preferences: UserPreferences;
}

// ============================================================================
// Request Configuration Types
// ============================================================================

export interface RequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: unknown;
  timeout?: number;
  signal?: AbortSignal;
  params?: Record<string, string | number | boolean>;
  onUploadProgress?: (progressEvent: UploadProgress) => void;
}

export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  maxRetries: number;
  retryDelay: number;
  retryMultiplier: number;
}

export type AuthStrategy = 'jwt' | 'twa' | 'none';

// ============================================================================
// Export Types
// ============================================================================

export type ExportType = 'overview' | 'growth' | 'posts' | 'engagement';
export type ExportFormat = 'csv' | 'json' | 'pdf';

export interface ExportRequest {
  type: ExportType;
  channelId: string;
  period: string;
  format: ExportFormat;
}

export interface ExportResponse {
  downloadUrl: string;
  filename: string;
  expiresAt: string;
}
