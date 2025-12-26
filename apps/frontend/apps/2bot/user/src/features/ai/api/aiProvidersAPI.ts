/**
 * AI Providers API Client
 * Manages user's AI provider configurations (OpenAI, Claude, Gemini, etc.)
 */

import { apiClient } from '@/api/client';

export interface AIProvider {
  name: string;
  display_name: string;
  default_model: string;
  available_models: string[];
  description?: string;
  website?: string;
}

export interface UserAIProvider {
  provider: string;
  display_name: string;
  model: string;
  api_key_preview: string;
  monthly_budget: number | null;
  is_default: boolean;
  created_at: string;
}

export interface AIProviderSpending {
  provider: string;
  monthly_budget: number | null;
  current_spending: number;
  remaining_budget: number;
  usage_percentage: number;
  period: string;
  tokens_used: number;
}

export interface AddProviderRequest {
  provider: string;
  api_key: string;
  model?: string;
  monthly_budget?: number;
}

export interface AddProviderResponse {
  provider: string;
  display_name: string;
  model: string;
  api_key_preview: string;
  monthly_budget: number | null;
  is_default: boolean;
  message: string;
}

class AIProvidersAPI {
  private readonly baseUrl = '/user/ai/providers';

  /**
   * Get all available AI providers
   */
  async getAvailableProviders(): Promise<{ providers: AIProvider[] }> {
    return await apiClient.get<{ providers: AIProvider[] }>(`${this.baseUrl}/available`);
  }

  /**
   * Get user's configured providers
   */
  async getMyProviders(): Promise<{ providers: UserAIProvider[] }> {
    return await apiClient.get<{ providers: UserAIProvider[] }>(`${this.baseUrl}/mine`);
  }

  /**
   * Add a new AI provider with API key
   */
  async addProvider(data: AddProviderRequest): Promise<AddProviderResponse> {
    return await apiClient.post<AddProviderResponse>(`${this.baseUrl}/add`, data);
  }

  /**
   * Set provider as default
   */
  async setDefaultProvider(provider: string): Promise<{ message: string }> {
    return await apiClient.put<{ message: string }>(`${this.baseUrl}/${provider}/set-default`);
  }

  /**
   * Remove a provider
   */
  async removeProvider(provider: string): Promise<{ message: string }> {
    return await apiClient.delete<{ message: string }>(`${this.baseUrl}/${provider}`);
  }

  /**
   * Get provider spending statistics
   */
  async getProviderSpending(provider: string): Promise<AIProviderSpending> {
    return await apiClient.get<AIProviderSpending>(`${this.baseUrl}/${provider}/spending`);
  }
}

export default new AIProvidersAPI();
