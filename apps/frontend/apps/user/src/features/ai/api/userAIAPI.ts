/**
 * User AI API Client
 * Real API integration for User AI features
 * 
 * Endpoints:
 * - GET /user/ai/status - Get AI usage status
 * - GET /user/ai/settings - Get AI settings
 * - PUT /user/ai/settings - Update AI settings
 * - POST /user/ai/analyze - Run AI analysis
 * - GET /user/ai/services - List available AI services
 */

import { apiClient } from '@/api/client';
import { apiLogger } from '@/utils/logger';

const USER_AI_BASE = '/user/ai';

// =====================================
// Types
// =====================================

export interface AIStatusResponse {
  user_id: number;
  tier: 'free' | 'basic' | 'pro' | 'enterprise';
  enabled: boolean;
  usage_today: number;
  usage_limit: number;
  remaining_requests: number;
  features_enabled: string[];
  services_enabled: string[];
}

export interface AISettingsResponse {
  user_id: number;
  tier: string;
  enabled: boolean;
  features: string[];
  limits: {
    requests_per_day: number;
    requests_per_hour: number;
    max_tokens: number;
    max_channels: number;
  };
  usage: {
    requests_today: number;
    requests_this_hour: number;
  };
  settings: {
    preferred_model: string;
    temperature: number;
    language: string;
    response_style: string;
    include_recommendations: boolean;
    include_explanations: boolean;
    auto_insights_enabled: boolean;
    auto_insights_frequency: string;
    enabled_features: string[];
  };
}

export interface UpdateAISettingsRequest {
  enabled_features?: string[];
  preferred_model?: string;
  temperature?: number;
  language?: string;
  response_style?: string;
  include_recommendations?: boolean;
  include_explanations?: boolean;
  auto_insights_enabled?: boolean;
  auto_insights_frequency?: string;
}

export interface AIAnalysisRequest {
  channel_id: number;
  analysis_type: 'overview' | 'engagement' | 'growth' | 'content';
  period_days?: number;
}

export interface AIAnalysisResponse {
  success: boolean;
  channel_id: number;
  analysis_type: string;
  insights: Array<{
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
    category: string;
    actionable: boolean;
  }>;
  recommendations: string[];
  generated_at: string;
}

export interface AIService {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  tier_required: string;
  icon?: string;
  color?: string;
  category?: string;
}

export interface AIServicesResponse {
  user_id: number;
  tier: string;
  services: AIService[];
}

// =====================================
// API Methods
// =====================================

/**
 * Get current AI usage status
 */
export const getAIStatus = async (): Promise<AIStatusResponse> => {
  try {
    const response = await apiClient.get<AIStatusResponse>(`${USER_AI_BASE}/status`);
    apiLogger.info('Fetched AI status', { tier: response.tier });
    return response;
  } catch (error: any) {
    apiLogger.error('Failed to fetch AI status', { error });
    throw new Error(error.response?.data?.detail || 'Failed to fetch AI status');
  }
};

/**
 * Get user's AI settings
 */
export const getAISettings = async (): Promise<AISettingsResponse> => {
  try {
    const response = await apiClient.get<AISettingsResponse>(`${USER_AI_BASE}/settings`);
    apiLogger.info('Fetched AI settings', { tier: response.tier });
    return response;
  } catch (error: any) {
    apiLogger.error('Failed to fetch AI settings', { error });
    throw new Error(error.response?.data?.detail || 'Failed to fetch AI settings');
  }
};

/**
 * Update user's AI settings
 */
export const updateAISettings = async (settings: UpdateAISettingsRequest): Promise<AISettingsResponse> => {
  try {
    const response = await apiClient.put<AISettingsResponse>(`${USER_AI_BASE}/settings`, settings);
    apiLogger.info('Updated AI settings');
    return response;
  } catch (error: any) {
    apiLogger.error('Failed to update AI settings', { error });
    throw new Error(error.response?.data?.detail || 'Failed to update AI settings');
  }
};

/**
 * Run AI analysis on a channel
 */
export const runAIAnalysis = async (request: AIAnalysisRequest): Promise<AIAnalysisResponse> => {
  try {
    const response = await apiClient.post<AIAnalysisResponse>(`${USER_AI_BASE}/analyze`, request);
    apiLogger.info('AI analysis completed', { 
      channel_id: request.channel_id,
      type: request.analysis_type 
    });
    return response;
  } catch (error: any) {
    apiLogger.error('AI analysis failed', { error });
    throw new Error(error.response?.data?.detail || 'AI analysis failed');
  }
};

/**
 * List available AI services
 */
export const getAIServices = async (): Promise<AIServicesResponse> => {
  try {
    const response = await apiClient.get<AIServicesResponse>(`${USER_AI_BASE}/services`);
    apiLogger.info('Fetched AI services', { count: response.services?.length });
    return response;
  } catch (error: any) {
    apiLogger.error('Failed to fetch AI services', { error });
    throw new Error(error.response?.data?.detail || 'Failed to fetch AI services');
  }
};

// Export all as default object
export const UserAIAPI = {
  getStatus: getAIStatus,
  getSettings: getAISettings,
  updateSettings: updateAISettings,
  analyze: runAIAnalysis,
  getServices: getAIServices,
};

export default UserAIAPI;
