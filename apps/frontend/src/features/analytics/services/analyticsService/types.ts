/**
 * Analytics Service Types
 */

export interface CacheEntry {
  data: any;
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
  status: 'healthy' | 'degraded';
  adapter: string;
  timestamp: number;
  api_status?: any;
  error?: string;
  features?: string[];
  performance?: {
    avgResponseTime: string;
    cacheHitRate: string;
  };
}

export interface Metrics {
  requests: number;
  cacheHits: number;
  errors: number;
  totalResponseTime: number;
}

export interface ServiceMetrics {
  requests: Metrics;
  cache: CacheStats;
  currentAdapter: 'api' | 'mock';
  adapters: {
    real: string;
    mock: string;
  };
}

export interface Logger {
  debug: (message: string, ...args: any[]) => void;
  info: (message: string, ...args: any[]) => void;
  warn: (message: string, ...args: any[]) => void;
  error: (message: string, ...args: any[]) => void;
}

export interface AnalyticsOverview {
  channelId?: string;
  channel_id?: string;
  subscribers?: number;
  views?: number;
  totalViews?: number;
  posts?: number;
  totalPosts?: number;
  engagement_rate?: number;
  engagementRate?: number;
  growth_rate?: number;
  growthRate?: number;
  avg_views_per_post?: number;
  period?: string;
  source: string;
  lastUpdated?: string;
}

export interface PostDynamicsResult {
  success?: boolean;
  data?: any;
  dynamics?: any[];
  source: string;
  period?: string;
  message?: string;
}

export interface TopPostsResult {
  channelId: string;
  period: string;
  sortBy: string;
  posts: any[];
  source: string;
  generatedAt: string;
  message?: string;
}

export interface BestTimeResult {
  channelId?: string;
  timeframe: string;
  recommendations: any[];
  source: string;
  generatedAt?: string;
  message?: string;
}

export interface AIRecommendationsResult {
  channelId?: string;
  recommendations: any[];
  source: string;
  generatedAt?: string;
  message?: string;
}
