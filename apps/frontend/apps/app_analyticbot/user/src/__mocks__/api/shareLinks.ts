/**
 * Mock Share Links API
 * Provides mock data for share link generation in demo mode
 */

export interface ShareLinkResponse {
  share_url: string;
  expires_at: string;
  share_id: string;
  data_type: string;
  channel_id: string;
  token?: string;
  access_count?: number;
  analytics_enabled?: boolean;
}

export type TTLOption = '1h' | '6h' | '24h' | '3d' | '7d';

/**
 * Calculate expiry timestamp based on TTL
 */
const calculateExpiry = (ttl: TTLOption): string => {
  const ttlMs: Record<TTLOption, number> = {
    '1h': 3600000,
    '6h': 21600000,
    '24h': 86400000,
    '3d': 259200000,
    '7d': 604800000
  };

  return new Date(Date.now() + ttlMs[ttl]).toISOString();
};

/**
 * Create a mock share link response
 */
export const createMockShareLink = (
  channelId: string,
  dataType: string,
  ttl: TTLOption = '24h'
): ShareLinkResponse => {
  const shareId = `share-${Date.now()}-${Math.random().toString(36).substring(7)}`;

  return {
    share_url: `https://analyticbot.com/share/${channelId}-${dataType}-${Date.now()}`,
    expires_at: calculateExpiry(ttl),
    share_id: shareId,
    data_type: dataType,
    channel_id: channelId,
    token: Math.random().toString(36).substring(2, 15),
    access_count: 0,
    analytics_enabled: true
  };
};

/**
 * Simulate API delay for realistic demo experience
 */
export const mockShareLinkDelay = (ms: number = 800): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Mock share link with metadata
 */
export const mockShareLinks = {
  engagement: createMockShareLink('demo_channel', 'engagement', '24h'),
  analytics: createMockShareLink('demo_channel', 'analytics', '7d'),
  performance: createMockShareLink('demo_channel', 'performance', '3d')
};
