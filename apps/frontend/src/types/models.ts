/**
 * Domain Models Type Definitions
 * Core business domain types used throughout the application
 */

// ============================================================================
// User & Authentication Models
// ============================================================================

export type UserRole = 'user' | 'admin' | 'superadmin';

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
  dataSource?: 'api' | 'mock';
}

// ============================================================================
// Channel Models
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
  settings?: ChannelSettings;
}

export interface ChannelMetrics {
  totalPosts: number;
  totalViews: number;
  totalShares: number;
  totalReactions: number;
  engagementRate: number;
  growthRate: number;
  averageViews: number;
  peakHour?: number;
}

export interface ChannelSettings {
  autoPost?: boolean;
  notifyOnMilestone?: boolean;
  analyticsEnabled?: boolean;
  aiRecommendations?: boolean;
}

export interface ChannelValidationResult {
  valid: boolean;
  exists?: boolean;
  channelData?: {
    id: string;
    title: string;
    subscriberCount: number;
    description?: string;
    username?: string;
  };
  error?: string;
  errorCode?: string;
}

// ============================================================================
// Post Models
// ============================================================================

export type PostStatus = 'draft' | 'scheduled' | 'publishing' | 'published' | 'failed';

export interface Post {
  id: string;
  channelId: string;
  content: string;
  mediaId?: string;
  mediaUrl?: string;
  mediaType?: MediaType;
  scheduledTime?: string;
  publishedTime?: string;
  status: PostStatus;
  views?: number;
  shares?: number;
  reactions?: number;
  engagementRate?: number;
  createdAt: string;
  updatedAt?: string;
  metadata?: PostMetadata;
}

export interface PostMetadata {
  hasHashtags?: boolean;
  hashtagCount?: number;
  mentionCount?: number;
  linkCount?: number;
  characterCount?: number;
  estimatedReadTime?: number;
}

export interface ScheduledPost extends Post {
  scheduledTime: string;
  status: 'scheduled' | 'publishing' | 'failed';
  retryCount?: number;
  lastError?: string;
}

// ============================================================================
// Analytics Models
// ============================================================================

export interface AnalyticsOverview {
  totalViews: number;
  totalShares: number;
  totalReactions: number;
  totalPosts: number;
  engagementRate: number;
  growthRate: number;
  reachScore: number;
  viralityScore?: number;
  avgViewsPerPost: number;
  period: string;
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
  trend: 'up' | 'down' | 'stable';
}

export interface GrowthDataPoint {
  date: string;
  subscribers: number;
  views: number;
  engagement: number;
  posts?: number;
}

export interface ReachMetrics {
  totalReach: number;
  organicReach: number;
  viralReach: number;
  reachRate: number;
  impressions: number;
  uniqueViewers: number;
  frequency: number;
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
  channelId?: string;
  mediaUrl?: string;
}

export interface PostDynamics {
  postId: string;
  views: number[];
  shares: number[];
  reactions: number[];
  timestamps: string[];
  engagementRate: number;
  peakTime?: string;
  decayRate?: number;
}

export interface EngagementMetrics {
  likes: number;
  shares: number;
  comments: number;
  reactions: number;
  engagementRate: number;
  interactionRate: number;
  avgTimeSpent?: number;
}

export interface BestTimeRecommendation {
  hour: number;
  day: string;
  score: number;
  reason: string;
  confidence: number;
  avgEngagement: number;
}

// ============================================================================
// Media Models
// ============================================================================

export type MediaType = 'image' | 'video' | 'document' | 'audio' | 'gif' | 'sticker';

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
  channelId?: string;
  metadata?: MediaMetadata;
}

export interface MediaMetadata {
  format?: string;
  codec?: string;
  bitrate?: number;
  fps?: number;
  aspectRatio?: string;
  hasAudio?: boolean;
}

export interface UploadProgress {
  progress: number;
  loaded: number;
  total: number;
  speed?: number;
  error?: string;
  fileName?: string;
}

export interface PendingMedia {
  file: File;
  preview: string;
  type: MediaType;
  uploadProgress?: number;
}

// ============================================================================
// Analytics Period & Time Range
// ============================================================================

export type TimePeriod = '24h' | '7d' | '30d' | '90d' | 'custom';

export interface DateRange {
  from: Date | string;
  to: Date | string;
}

export interface AnalyticsPeriod {
  period: TimePeriod;
  dateRange?: DateRange;
  label?: string;
}

// ============================================================================
// Data Source & System
// ============================================================================

export type DataSource = 'api' | 'mock' | 'demo';

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version?: string;
  timestamp: string;
  services: {
    database: 'up' | 'down';
    redis?: 'up' | 'down';
    telegram?: 'up' | 'down';
    api?: 'up' | 'down';
  };
  uptime?: number;
}

export interface Alert {
  id: string;
  type: 'warning' | 'error' | 'info' | 'success';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  title?: string;
  timestamp: string;
  resolved: boolean;
  resolvedAt?: string;
  category?: string;
}

// ============================================================================
// Validation Results
// ============================================================================

export interface ValidationResult {
  valid: boolean;
  error?: string;
  errorCode?: string;
  field?: string;
  suggestions?: string[];
}

export interface ValidationErrors {
  [field: string]: string;
}

// ============================================================================
// Pagination
// ============================================================================

export interface PaginationParams {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasMore: boolean;
  hasPrevious: boolean;
}

// ============================================================================
// Charts & Visualization
// ============================================================================

export type ChartType = 'line' | 'bar' | 'pie' | 'area' | 'scatter' | 'heatmap';

export interface ChartDataPoint {
  x: string | number;
  y: number;
  label?: string;
  color?: string;
}

export interface ChartSeries {
  name: string;
  data: ChartDataPoint[];
  color?: string;
  type?: ChartType;
}

export interface ChartConfig {
  type: ChartType;
  series: ChartSeries[];
  title?: string;
  subtitle?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  legend?: boolean;
  tooltip?: boolean;
  height?: number;
}

// ============================================================================
// AI Services
// ============================================================================

export interface ContentOptimizationSuggestion {
  type: 'hashtag' | 'emoji' | 'timing' | 'length' | 'tone';
  suggestion: string;
  reason: string;
  confidence: number;
  impact?: 'high' | 'medium' | 'low';
}

export interface ContentAnalysis {
  sentiment: 'positive' | 'negative' | 'neutral';
  sentimentScore: number;
  readability: number;
  tone: string;
  keywords: string[];
  suggestions: ContentOptimizationSuggestion[];
  predictedEngagement?: number;
}

export interface SecurityThreat {
  id: string;
  type: 'spam' | 'phishing' | 'malware' | 'inappropriate' | 'suspicious';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  detected: string;
  resolved: boolean;
  action?: string;
}

export interface ChurnPrediction {
  userId: string;
  channelId: string;
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high';
  factors: string[];
  recommendations: string[];
  confidence: number;
}

// ============================================================================
// Notification & Toast
// ============================================================================

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title?: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  timestamp: string;
}

// ============================================================================
// Export convenience type unions
// ============================================================================

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export type SortOrder = 'asc' | 'desc';

export type Theme = 'light' | 'dark' | 'auto';

// ============================================================================
// Utility Types
// ============================================================================

export type Optional<T> = T | null | undefined;

export type Nullable<T> = T | null;

export type ID = string | number;

export type Timestamp = string | Date;

export type ApiStatus = 'idle' | 'loading' | 'success' | 'error';
