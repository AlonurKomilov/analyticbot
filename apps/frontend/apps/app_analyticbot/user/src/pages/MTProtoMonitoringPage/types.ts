/**
 * MTProto Monitoring Types
 * Shared interfaces for monitoring components
 */

export interface SessionHealth {
  session_valid: boolean;
  session_connected: boolean;
  session_last_used: string | null;
  api_calls_today: number;
  rate_limit_hits_today: number;
  connection_errors_today: number;
  health_score: number;
}

export interface CollectionProgress {
  total_channels: number;
  active_channels: number;
  total_posts_collected: number;
  collection_active: boolean;
  last_collection_time: string | null;
  next_collection_eta: string | null;
  estimated_completion_percent: number;
}

export interface WorkerStatus {
  worker_running: boolean;
  worker_interval_minutes: number;
  min_interval_minutes: number;  // Minimum allowed interval for user's plan
  plan_name: string;  // User's plan name (free, pro, business, enterprise)
  last_run: string | null;
  next_run: string | null;
  runs_today: number;
  errors_today: number;
  currently_collecting: boolean;
  current_channel: string | null;
  channels_processed: number;
  channels_total: number;
  messages_collected_current_run: number;
  errors_current_run: number;
  collection_start_time: string | null;
  estimated_time_remaining: number | null;
}

export interface ChannelStats {
  channel_id: number;
  channel_name: string;
  total_posts: number;
  latest_post_date: string | null;
  oldest_post_date: string | null;
  last_collected: string | null;
  collection_enabled: boolean;
}

export interface MonitoringData {
  user_id: number;
  mtproto_enabled: boolean;
  session_health: SessionHealth;
  collection_progress: CollectionProgress;
  worker_status: WorkerStatus;
  channels: ChannelStats[];
  timestamp: string;
}
