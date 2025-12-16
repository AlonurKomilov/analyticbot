/**
 * User Bot Service API Service
 * API methods for managing bot service features
 */

import type {
  ChatSettings,
  ChatSettingsUpdate,
  BannedWord,
  BannedWordCreate,
  WelcomeMessage,
  WelcomeMessageUpsert,
  InviteStats,
  ModerationLogResponse,
  UserWarningsResponse,
  ModerationChatItem,
} from '@/types';

import { apiClient, UnifiedApiClient } from '../api/client';

/**
 * User Bot Service API Service Class
 */
export class UserBotServiceApiService {
  private client: UnifiedApiClient;
  private basePath = '/user-bot/service';

  constructor(client: UnifiedApiClient) {
    this.client = client;
  }

  // ==================== Chat Settings ====================

  /**
   * Get settings for a specific chat
   */
  async getChatSettings(chatId: number): Promise<ChatSettings | null> {
    try {
      const response = await this.client.get<ChatSettings>(
        `${this.basePath}/settings/${chatId}`
      );
      return response;
    } catch (error: any) {
      if (error?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  /**
   * Create or update settings for a chat
   */
  async upsertChatSettings(
    chatId: number,
    settings: ChatSettingsUpdate
  ): Promise<ChatSettings> {
    const response = await this.client.post<ChatSettings>(
      `${this.basePath}/settings/${chatId}`,
      settings
    );
    return response;
  }

  /**
   * Delete settings for a chat
   */
  async deleteChatSettings(chatId: number): Promise<void> {
    await this.client.delete(`${this.basePath}/settings/${chatId}`);
  }

  /**
   * Get all chats with settings configured
   */
  async getConfiguredChats(): Promise<ModerationChatItem[]> {
    const response = await this.client.get<ModerationChatItem[]>(
      `${this.basePath}/chats`
    );
    return response;
  }

  // ==================== Banned Words ====================

  /**
   * Get banned words for a chat
   */
  async getBannedWords(chatId: number): Promise<BannedWord[]> {
    const response = await this.client.get<BannedWord[]>(
      `${this.basePath}/banned-words`,
      { params: { chat_id: chatId } }
    );
    return response;
  }

  /**
   * Add a banned word to a chat
   */
  async addBannedWord(
    chatId: number,
    data: BannedWordCreate
  ): Promise<BannedWord> {
    const response = await this.client.post<BannedWord>(
      `${this.basePath}/banned-words`,
      data
    );
    return response;
  }

  /**
   * Delete a banned word
   */
  async deleteBannedWord(chatId: number, wordId: number): Promise<void> {
    await this.client.delete(
      `${this.basePath}/banned-words/${wordId}`
    );
  }

  /**
   * Bulk add banned words (implemented client-side as multiple API calls)
   */
  async bulkAddBannedWords(
    chatId: number,
    words: BannedWordCreate[]
  ): Promise<BannedWord[]> {
    // Since backend doesn't have bulk endpoint, add words one by one
    const results: BannedWord[] = [];
    for (const word of words) {
      const result = await this.addBannedWord(chatId, word);
      results.push(result);
    }
    return results;
  }

  // ==================== Welcome Messages ====================

  /**
   * Get welcome message for a chat
   */
  async getWelcomeMessage(
    chatId: number,
    messageType: 'welcome' | 'goodbye' = 'welcome'
  ): Promise<WelcomeMessage | null> {
    try {
      const response = await this.client.get<WelcomeMessage>(
        `${this.basePath}/welcome/${chatId}`,
        { params: { message_type: messageType } }
      );
      return response;
    } catch (error: any) {
      if (error?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  /**
   * Create or update welcome message
   */
  async upsertWelcomeMessage(
    chatId: number,
    data: WelcomeMessageUpsert
  ): Promise<WelcomeMessage> {
    const response = await this.client.post<WelcomeMessage>(
      `${this.basePath}/welcome/${chatId}`,
      data
    );
    return response;
  }

  /**
   * Delete welcome message
   */
  async deleteWelcomeMessage(
    chatId: number,
    messageType: 'welcome' | 'goodbye' = 'welcome'
  ): Promise<void> {
    await this.client.delete(`${this.basePath}/welcome/${chatId}`, {
      params: { message_type: messageType },
    });
  }

  // ==================== Invite Tracking ====================

  /**
   * Get invite statistics for a chat
   */
  async getInviteStats(
    chatId: number,
    limit: number = 20
  ): Promise<InviteStats> {
    const response = await this.client.get<InviteStats>(
      `${this.basePath}/invites/${chatId}`,
      { params: { limit } }
    );
    return response;
  }

  /**
   * Get invite leaderboard for a chat
   */
  async getInviteLeaderboard(
    chatId: number,
    limit: number = 10
  ): Promise<InviteStats> {
    const response = await this.client.get<InviteStats>(
      `${this.basePath}/invites/${chatId}/leaderboard`,
      { params: { limit } }
    );
    return response;
  }

  // ==================== Moderation Log ====================

  /**
   * Get moderation log for a chat
   */
  async getModerationLog(
    chatId: number,
    page: number = 1,
    perPage: number = 20
  ): Promise<ModerationLogResponse> {
    const response = await this.client.get<ModerationLogResponse>(
      `${this.basePath}/log/${chatId}`,
      { params: { page, per_page: perPage } }
    );
    return response;
  }

  // ==================== Warnings ====================

  /**
   * Get warnings for a user in a chat
   */
  async getUserWarnings(
    chatId: number,
    targetTgId: number
  ): Promise<UserWarningsResponse> {
    const response = await this.client.get<UserWarningsResponse>(
      `${this.basePath}/warnings/${chatId}/${targetTgId}`
    );
    return response;
  }

  /**
   * Clear warnings for a user
   */
  async clearUserWarnings(chatId: number, targetTgId: number): Promise<void> {
    await this.client.delete(
      `${this.basePath}/warnings/${chatId}/${targetTgId}`
    );
  }
}

// Export singleton instance using the shared apiClient with authentication
export const userBotServiceApi = new UserBotServiceApiService(apiClient);
