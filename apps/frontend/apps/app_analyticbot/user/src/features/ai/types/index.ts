/**
 * User AI Types
 * TypeScript types for User AI feature
 */

export type AITier = 'free' | 'basic' | 'pro' | 'enterprise';

export type AIFeature = 
  | 'channel_analytics'
  | 'content_suggestions'
  | 'posting_schedule'
  | 'custom_queries'
  | 'competitor_analysis'
  | 'auto_reply'
  | 'content_scheduler';

export type AnalysisType = 'overview' | 'engagement' | 'growth' | 'content';

export interface AIStatus {
  user_id: number;
  tier: AITier;
  enabled: boolean;
  usage_today: number;
  usage_limit: number;
  remaining_requests: number;
  features_enabled: string[];
  services_enabled: string[];
}

export interface AISettings {
  preferred_model: string;
  temperature: number;
  language: string;
  response_style: string;
  include_recommendations: boolean;
  include_explanations: boolean;
  auto_insights_enabled: boolean;
  auto_insights_frequency: string;
  enabled_features: string[];
}

export interface AILimits {
  requests_per_day: number;
  requests_per_hour: number;
  max_tokens: number;
  max_channels: number;
}

export interface AIUsage {
  requests_today: number;
  requests_this_hour: number;
}

export interface AIInsight {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
  actionable: boolean;
  created_at: string;
}

export interface ActiveAIService {
  id: string;
  service_key: string;
  service_name: string;
  icon: string | null;
  color: string | null;
  status: 'active' | 'expired' | 'cancelled';
  expires_at: string;
  usage_quota_daily: number | null;
  usage_quota_monthly: number | null;
  usage_count_daily: number;
  usage_count_monthly: number;
}

export interface AvailableAIService {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  tier_required: string;
  icon?: string;
  color?: string;
  category?: string;
  price_credits?: number;
}

// Dialog state types
export interface AIDialogState {
  showSettingsDialog: boolean;
}

// Component props
export interface AIStatusCardProps {
  status: AIStatus | null;
  isLoading: boolean;
}

export interface AISettingsCardProps {
  settings: AISettings | null;
  limits: AILimits | null;
  isLoading: boolean;
  onUpdateSettings: (settings: Partial<AISettings>) => Promise<void>;
}

export interface ActiveAIServicesCardProps {
  services: ActiveAIService[];
  isLoading: boolean;
}

export interface AvailableAIServicesCardProps {
  services: AvailableAIService[];
  activeServiceKeys: string[];
  isLoading: boolean;
}
