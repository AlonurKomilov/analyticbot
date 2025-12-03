/**
 * Analytics Overview Types
 * =========================
 *
 * TypeScript types for the TGStat-style Analytics Overview dashboard.
 */

export interface SubscriberStats {
  total: number;
  today_change: number;
  week_change: number;
  month_change: number;
  growth_rate: number;
}

export interface PostsStats {
  total: number;
  today: number;
  week: number;
  month: number;
  avg_per_day: number;
}

export interface EngagementStats {
  total_views: number;
  total_reactions: number;
  total_forwards: number;
  total_comments: number;
  avg_views_per_post: number;
  avg_reactions_per_post: number;
  engagement_rate: number;
  err: number;
  err_24h: number;
}

export interface ReachStats {
  avg_post_reach: number;
  avg_ad_reach: number;
  reach_12h: number;
  reach_24h: number;
  reach_48h: number;
  citation_index: number;
}

export interface ChannelInfo {
  id: number;
  title: string;
  username: string | null;
  description: string | null;
  created_at: string | null;  // When added to analytics system
  telegram_created_at: string | null;  // Actual Telegram channel creation date
  age_days: number;  // Days tracked in analytics system
  channel_age_days: number | null;  // Actual channel age (from Telegram)
  age_formatted: string;  // Formatted tracking duration
  channel_age_formatted: string | null;  // Formatted actual channel age
  is_active: boolean;
}

export interface TimeSeriesDataPoint {
  date: string;
  value: number;
  change?: number;
}

export interface ChannelOverviewData {
  channel_info: ChannelInfo;
  subscribers: SubscriberStats;
  posts: PostsStats;
  engagement: EngagementStats;
  reach: ReachStats;
  subscribers_history: TimeSeriesDataPoint[];
  views_history: TimeSeriesDataPoint[];
  posts_history: TimeSeriesDataPoint[];
  generated_at: string;
  data_freshness: 'real-time' | 'cached' | 'historical';
}

export type OverviewPeriod = 'today' | 'last_7_days' | 'last_30_days' | 'last_90_days' | 'all_time';

export interface UseOverviewOptions {
  period?: OverviewPeriod;
  refreshInterval?: number;
  enabled?: boolean;
}

export interface UseOverviewReturn {
  data: ChannelOverviewData | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

// ============================================================================
// Telegram Statistics API Types (Phase 3)
// ============================================================================

export interface LanguageStats {
  language_code: string;
  language_name: string;
  percentage: number;
}

export interface CountryStats {
  country_code: string;
  country_name: string;
  percentage: number;
}

export interface DeviceStats {
  device_type: 'android' | 'ios' | 'desktop' | 'web' | string;
  percentage: number;
}

export interface TrafficSource {
  source_type: 'search' | 'mentions' | 'links' | 'other_channels' | 'direct' | string;
  source_name: string;
  subscribers_count: number;
  percentage: number;
}

export interface GrowthPoint {
  date: string;
  subscribers: number;
  joined: number;
  left: number;
}

export interface InteractionStats {
  views_per_post: number;
  shares_per_post: number;
  reactions_per_post: number;
  comments_per_post: number;
}

export interface TelegramStats {
  channel_id: number;
  is_available: boolean;
  error_message: string | null;

  // Basic stats from Telegram API
  subscriber_count: number;
  mean_view_count: number;
  mean_share_count: number;
  mean_reaction_count: number;

  // Demographics
  languages: LanguageStats[];
  countries: CountryStats[];
  devices: DeviceStats[];

  // Traffic sources
  traffic_sources: TrafficSource[];

  // Growth data
  growth_history: GrowthPoint[];
  followers_growth_rate: number;

  // Interactions
  interactions: InteractionStats | null;

  // Metadata
  fetched_at: string;
  period_start: string | null;
  period_end: string | null;
}

export interface UseTelegramStatsReturn {
  data: TelegramStats | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}
