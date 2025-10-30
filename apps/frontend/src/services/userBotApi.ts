/**
 * User Bot API Service
 * API methods for managing user bots and admin operations
 */

import type {
  CreateBotRequest,
  CreateBotResponse,
  BotStatusResponse,
  VerifyBotRequest,
  VerifyBotResponse,
  UpdateRateLimitRequest,
  RateLimitUpdateResponse,
  RemoveBotResponse,
  AdminBotListResponse,
  SuspendBotRequest,
  SuspendBotResponse,
  ActivateBotResponse,
  AdminAccessResponse,
} from '@/types';

import { apiClient, UnifiedApiClient } from '../api/client';

/**
 * User Bot API Service Class
 */
export class UserBotApiService {
  private client: UnifiedApiClient;

  constructor(client: UnifiedApiClient) {
    this.client = client;
  }

  // ==================== User Bot Operations ====================

  /**
   * Create a new user bot
   */
  async createBot(data: CreateBotRequest): Promise<CreateBotResponse> {
    const response = await this.client.post<CreateBotResponse>(
      '/api/user-bot/create',
      data
    );
    return response;
  }

  /**
   * Get user bot status
   */
  async getBotStatus(): Promise<BotStatusResponse> {
    const response = await this.client.get<BotStatusResponse>(
      '/api/user-bot/status'
    );
    return response;
  }

  /**
   * Verify user bot credentials
   */
  async verifyBot(data?: VerifyBotRequest): Promise<VerifyBotResponse> {
    const response = await this.client.post<VerifyBotResponse>(
      '/api/user-bot/verify',
      data || {}
    );
    return response;
  }

  /**
   * Remove user bot
   */
  async removeBot(): Promise<RemoveBotResponse> {
    const response = await this.client.delete<RemoveBotResponse>(
      '/api/user-bot/remove'
    );
    return response;
  }

  /**
   * Update bot rate limits
   */
  async updateRateLimits(data: UpdateRateLimitRequest): Promise<RateLimitUpdateResponse> {
    const response = await this.client.patch<RateLimitUpdateResponse>(
      '/api/user-bot/rate-limits',
      data
    );
    return response;
  }

  // ==================== Admin Bot Operations ====================

  /**
   * List all user bots (admin)
   */
  async listAllBots(params?: {
    limit?: number;
    offset?: number;
    status?: string;
  }): Promise<AdminBotListResponse> {
    const response = await this.client.get<AdminBotListResponse>(
      '/api/admin/bots/list',
      { params }
    );
    return response;
  }

  /**
   * Access user bot (admin)
   */
  async accessUserBot(userId: number): Promise<AdminAccessResponse> {
    const response = await this.client.post<AdminAccessResponse>(
      `/api/admin/bots/${userId}/access`
    );
    return response;
  }

  /**
   * Suspend user bot (admin)
   */
  async suspendBot(userId: number, data: SuspendBotRequest): Promise<SuspendBotResponse> {
    const response = await this.client.patch<SuspendBotResponse>(
      `/api/admin/bots/${userId}/suspend`,
      data
    );
    return response;
  }

  /**
   * Activate user bot (admin)
   */
  async activateBot(userId: number): Promise<ActivateBotResponse> {
    const response = await this.client.patch<ActivateBotResponse>(
      `/api/admin/bots/${userId}/activate`
    );
    return response;
  }

  /**
   * Update user bot rate limits (admin)
   */
  async updateUserBotRateLimits(
    userId: number,
    data: UpdateRateLimitRequest
  ): Promise<RateLimitUpdateResponse> {
    const response = await this.client.patch<RateLimitUpdateResponse>(
      `/api/admin/bots/${userId}/rate-limit`,
      data
    );
    return response;
  }

  /**
   * Get specific user bot status (admin)
   */
  async getUserBotStatus(userId: number): Promise<BotStatusResponse> {
    const response = await this.client.get<BotStatusResponse>(
      `/api/admin/bots/${userId}/status`
    );
    return response;
  }
}

// Export singleton instance using the shared apiClient with authentication
export const userBotApi = new UserBotApiService(apiClient);
