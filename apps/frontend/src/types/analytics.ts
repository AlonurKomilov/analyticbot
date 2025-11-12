/**
 * Analytics Type Definitions
 * Comprehensive types for analytics services and API responses
 */

// ============================================================================
// Common Analytics Types
// ============================================================================

export interface TimeSeriesDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface AnalyticsMetric {
  current: number;
  previous: number;
  change: number;
  changePercent: number;
  trend: 'up' | 'down' | 'stable';
}

export type AnalyticsPeriod = '24h' | '7d' | '30d' | '90d' | 'custom';

export interface DateRangeFilter {
  startDate: string;
  endDate: string;
}

// ============================================================================
// Analytics Overview
// ============================================================================

export interface AnalyticsOverviewData {
  channelId: string;
  period: AnalyticsPeriod;
  metrics: {
    totalViews: AnalyticsMetric;
    totalShares: AnalyticsMetric;
    totalReactions: AnalyticsMetric;
    engagementRate: AnalyticsMetric;
    subscriberCount: AnalyticsMetric;
    postCount: AnalyticsMetric;
  };
  timeSeries?: {
    views: TimeSeriesDataPoint[];
    shares: TimeSeriesDataPoint[];
    engagement: TimeSeriesDataPoint[];
  };
  timestamp: string;
}

export interface AnalyticsOverviewResponse {
  success: boolean;
  data: AnalyticsOverviewData;
  message?: string;
}

// ============================================================================
// Post Dynamics
// ============================================================================

export interface PostDynamicsDataPoint {
  date: string;
  views: number;
  shares: number;
  forwards?: number;
  reactions?: number;
  engagement?: number;
  post_count?: number;  // Number of posts in this time bucket
  postCount?: number;   // Alternative camelCase naming
}

export interface PostDynamicsData {
  channelId: string;
  period: AnalyticsPeriod;
  dataPoints: PostDynamicsDataPoint[];
  summary: {
    totalViews: number;
    totalShares: number;
    totalReactions: number;
    averageEngagement: number;
    peakDate: string;
    peakViews: number;
  };
  timestamp: string;
}

export interface PostDynamicsResponse {
  success: boolean;
  data: PostDynamicsData | PostDynamicsDataPoint[];
  message?: string;
}

// ============================================================================
// Top Posts
// ============================================================================

export interface TopPost {
  id: string | number;
  postId: string;
  channelId: string;
  title?: string;
  content: string;
  publishedAt: string;
  views: number;
  shares: number;
  forwards?: number;
  reactions: number;
  comments?: number;
  engagementRate: number;
  engagementScore?: number;
  rank?: number;
  mediaType?: 'text' | 'image' | 'video' | 'document';
  thumbnailUrl?: string;
}

export interface TopPostsData {
  channelId: string;
  period: AnalyticsPeriod;
  sortBy: 'views' | 'shares' | 'engagement' | 'reactions';
  posts: TopPost[];
  summary: {
    totalPosts: number;
    totalViews: number;
    averageEngagement: number;
  };
  timestamp: string;
}

export interface TopPostsResponse {
  success: boolean;
  data: TopPostsData | TopPost[];
  message?: string;
}

// ============================================================================
// Engagement Metrics
// ============================================================================

export interface EngagementBreakdown {
  views: number;
  shares: number;
  forwards: number;
  reactions: number;
  comments: number;
  saves?: number;
}

export interface EngagementMetricsData {
  channelId: string;
  period: AnalyticsPeriod;
  overall: {
    engagementRate: number;
    averageViewTime?: number;
    interactionRate: number;
  };
  breakdown: EngagementBreakdown;
  byType: {
    text: EngagementBreakdown;
    image: EngagementBreakdown;
    video: EngagementBreakdown;
  };
  timeSeries: Array<{
    date: string;
    engagementRate: number;
    interactions: number;
  }>;
  topEngagingHours?: Array<{
    hour: number;
    engagementRate: number;
  }>;
  timestamp: string;
}

export interface EngagementMetricsResponse {
  success: boolean;
  data: EngagementMetricsData;
  message?: string;
}

// ============================================================================
// Subscriber Growth
// ============================================================================

export interface SubscriberGrowthDataPoint {
  date: string;
  subscriberCount: number;
  newSubscribers: number;
  unsubscribers: number;
  netGrowth: number;
  growthRate: number;
}

export interface SubscriberGrowthData {
  channelId: string;
  period: AnalyticsPeriod;
  dataPoints: SubscriberGrowthDataPoint[];
  summary: {
    currentSubscribers: number;
    totalNewSubscribers: number;
    totalUnsubscribers: number;
    netGrowth: number;
    growthRate: number;
    averageDailyGrowth: number;
  };
  projections?: {
    nextMonth: number;
    nextQuarter: number;
    confidence: number;
  };
  timestamp: string;
}

export interface SubscriberGrowthResponse {
  success: boolean;
  data: SubscriberGrowthData;
  message?: string;
}

// ============================================================================
// Demographic Insights
// ============================================================================

export interface DemographicDistribution {
  value: string | number;
  count: number;
  percentage: number;
}

export interface DemographicInsightsData {
  channelId: string;
  period: AnalyticsPeriod;
  ageGroups: DemographicDistribution[];
  genders: DemographicDistribution[];
  locations: DemographicDistribution[];
  languages: DemographicDistribution[];
  devices: DemographicDistribution[];
  activeHours: Array<{
    hour: number;
    activityLevel: number;
  }>;
  timestamp: string;
}

export interface DemographicInsightsResponse {
  success: boolean;
  data: DemographicInsightsData;
  message?: string;
}

// ============================================================================
// Content Performance
// ============================================================================

export interface ContentPerformanceData {
  channelId: string;
  period: AnalyticsPeriod;
  byMediaType: {
    text: { count: number; avgViews: number; avgEngagement: number };
    image: { count: number; avgViews: number; avgEngagement: number };
    video: { count: number; avgViews: number; avgEngagement: number };
    document: { count: number; avgViews: number; avgEngagement: number };
  };
  byContentLength: {
    short: { count: number; avgEngagement: number };    // < 100 chars
    medium: { count: number; avgEngagement: number };   // 100-500 chars
    long: { count: number; avgEngagement: number };     // > 500 chars
  };
  bestPerforming: TopPost[];
  worstPerforming: TopPost[];
  recommendations: string[];
  timestamp: string;
}

export interface ContentPerformanceResponse {
  success: boolean;
  data: ContentPerformanceData;
  message?: string;
}

// ============================================================================
// Predictive Analytics
// ============================================================================

export interface PredictiveInsight {
  type: 'trend' | 'anomaly' | 'opportunity' | 'warning';
  title: string;
  description: string;
  confidence: number;
  impact: 'high' | 'medium' | 'low';
  actionable: boolean;
  recommendations?: string[];
}

export interface PredictiveAnalyticsData {
  channelId: string;
  forecasts: {
    subscribers: Array<{ date: string; predicted: number; confidence: number }>;
    engagement: Array<{ date: string; predicted: number; confidence: number }>;
    views: Array<{ date: string; predicted: number; confidence: number }>;
  };
  insights: PredictiveInsight[];
  bestPostingTimes: Array<{
    dayOfWeek: number;
    hour: number;
    score: number;
  }>;
  churnRisk?: {
    level: 'low' | 'medium' | 'high';
    probability: number;
    factors: string[];
  };
  timestamp: string;
}

export interface PredictiveAnalyticsResponse {
  success: boolean;
  data: PredictiveAnalyticsData;
  message?: string;
}

// ============================================================================
// Cache and Service Types
// ============================================================================

export interface CacheEntry<T = unknown> {
  data: T;
  timestamp: number;
  ttl: number;
}

export interface CacheStats {
  size: number;
  maxSize: number;
  keys: string[];
  hitRatio: number;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'offline';
  adapter: 'api' | 'mock';
  timestamp: number;
  api_status?: {
    connected: boolean;
    responseTime?: number;
    lastCheck: string;
  };
  error?: string;
  features?: string[];
  performance?: {
    avgResponseTime: string;
    cacheHitRate: string;
  };
}

export interface ServiceMetrics {
  requests: {
    total: number;
    success: number;
    errors: number;
    cacheHits: number;
    totalResponseTime: number;
  };
  cache: CacheStats;
  currentAdapter: 'api' | 'mock';
  adapters: {
    real: string;
    mock: string;
  };
}

// ============================================================================
// Logger Interface
// ============================================================================

export interface Logger {
  debug: (message: string, ...args: unknown[]) => void;
  info: (message: string, ...args: unknown[]) => void;
  warn: (message: string, ...args: unknown[]) => void;
  error: (message: string, ...args: unknown[]) => void;
}

// ============================================================================
// Utility Types
// ============================================================================

export type AnalyticsDataType =
  | 'overview'
  | 'postDynamics'
  | 'topPosts'
  | 'engagement'
  | 'subscriberGrowth'
  | 'demographics'
  | 'contentPerformance'
  | 'predictive';

export interface AnalyticsRequestParams {
  channelId: string;
  period?: AnalyticsPeriod;
  dateRange?: DateRangeFilter;
  sortBy?: string;
  limit?: number;
  offset?: number;
}

export interface AnalyticsError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
}
