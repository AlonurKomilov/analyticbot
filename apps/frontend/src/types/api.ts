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

// ============================================================================
// User Types
// ============================================================================

export type UserRole = 'viewer' | 'user' | 'moderator' | 'admin' | 'owner';

/**
 * User account status
 * Aligned with backend UserStatus enum
 *
 * CHANGED: Expanded from boolean isActive to 5-state enum
 */
export type UserStatus =
  | 'active'      // Account active and accessible
  | 'inactive'    // Account inactive but not deleted
  | 'suspended'   // Account suspended (violation/payment)
  | 'pending'     // Account pending verification
  | 'deleted';    // Account soft-deleted

// Import UserTier from subscription types
import { UserTier } from './subscription';

export interface User {
  id: string;
  email: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  role: UserRole;
  tier?: UserTier;      // ✅ ADDED: User subscription tier
  status: UserStatus;   // ✅ CHANGED: from isActive: boolean
  isActive?: boolean;   // ✅ DEPRECATED: kept for backward compatibility, use status instead
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
  // Legacy format (deprecated)
  valid?: boolean;
  exists?: boolean;
  channelData?: {
    id: string;
    title: string;
    subscriberCount: number;
    description?: string;
  };
  error?: string;
  
  // New format (from backend ChannelValidationResult)
  is_valid: boolean;
  telegram_id?: number;
  username?: string;
  title?: string;
  subscriber_count?: number;
  description?: string;
  is_verified?: boolean;
  is_scam?: boolean;
  error_message?: string;
}

// ============================================================================
// Post Types
// ============================================================================

// ============================================================================
// Post Types
// ============================================================================

/**
 * Post status - Frontend includes transition states
 * Backend PostStatus: draft, scheduled, published, failed, cancelled
 *
 * Note: 'publishing' is a frontend-only transition state
 *
 * Backend flow: scheduled → published (or failed)
 * Frontend flow: scheduled → publishing → published (or failed)
 *
 * The 'publishing' state is shown in UI when:
 * - Post status is 'scheduled'
 * - Current time >= scheduled time
 * - Status hasn't updated to 'published' yet (polling delay)
 *
 * ADDED: 'cancelled' status for scheduled posts that were cancelled
 */
export type PostStatus =
  | 'draft'       // Post being edited
  | 'scheduled'   // Scheduled for future publication
  | 'publishing'  // ⚠️ FRONTEND-ONLY: Currently publishing (transition state)
  | 'published'   // Successfully published
  | 'failed'      // Publishing failed
  | 'cancelled';  // ✅ ADDED: Scheduled post cancelled

/**
 * Backend post status (for API compatibility)
 * Backend doesn't have 'publishing' state
 */
export type BackendPostStatus = Exclude<PostStatus, 'publishing'>;

/**
 * Map backend status to frontend display status
 * Optionally show 'publishing' for scheduled posts past their time
 *
 * @param backendStatus - Status from backend API
 * @param scheduledTime - Optional scheduled time to determine if publishing
 * @returns Frontend post status for display
 */
export function mapBackendPostStatus(
  backendStatus: BackendPostStatus,
  scheduledTime?: string
): PostStatus {
  // If scheduled and past scheduled time, show as publishing
  if (backendStatus === 'scheduled' && scheduledTime) {
    const scheduled = new Date(scheduledTime).getTime();
    const now = Date.now();

    if (now >= scheduled) {
      return 'publishing';
    }
  }

  return backendStatus;
}

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
  _retry?: boolean; // Internal flag to track retry attempts
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
