/**
 * Analytics Overview Service
 * ==========================
 * 
 * Service for fetching TGStat-style channel overview data.
 */

import { apiClient } from '@/api/client';
import type { ChannelOverviewData, OverviewPeriod, TelegramStats } from './types';

const BASE_PATH = '/analytics/overview';

export const overviewService = {
  /**
   * Get complete channel overview dashboard data
   */
  async getDashboard(
    channelId: string | number,
    period: OverviewPeriod = 'last_7_days'
  ): Promise<ChannelOverviewData> {
    return apiClient.get<ChannelOverviewData>(
      `${BASE_PATH}/dashboard/${channelId}`,
      { params: { period } }
    );
  },

  /**
   * Get quick stats without chart data (lighter endpoint)
   */
  async getQuickStats(
    channelId: string | number
  ): Promise<Omit<ChannelOverviewData, 'subscribers_history' | 'views_history' | 'posts_history'>> {
    return apiClient.get<Omit<ChannelOverviewData, 'subscribers_history' | 'views_history' | 'posts_history'>>(
      `${BASE_PATH}/stats/${channelId}`
    );
  },

  /**
   * Get chart data only
   */
  async getCharts(
    channelId: string | number,
    days: number = 30
  ): Promise<{
    views_history: ChannelOverviewData['views_history'];
    posts_history: ChannelOverviewData['posts_history'];
    subscribers_history: ChannelOverviewData['subscribers_history'];
  }> {
    return apiClient.get<{
      views_history: ChannelOverviewData['views_history'];
      posts_history: ChannelOverviewData['posts_history'];
      subscribers_history: ChannelOverviewData['subscribers_history'];
    }>(
      `${BASE_PATH}/charts/${channelId}`,
      { params: { days } }
    );
  },

  /**
   * Get Telegram Statistics API data (demographics, traffic sources)
   * Requires channel admin access and 500+ subscribers
   */
  async getTelegramStats(channelId: string | number): Promise<TelegramStats> {
    return apiClient.get<TelegramStats>(
      `${BASE_PATH}/telegram-stats/${channelId}`
    );
  },
};

export default overviewService;
