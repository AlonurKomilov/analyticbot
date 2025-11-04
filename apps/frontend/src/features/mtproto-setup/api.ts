/**
 * MTProto API Client Methods
 *
 * API methods for user MTProto configuration and management
 */

import { apiClient } from '@/api/client';
import type {
  MTProtoSetupRequest,
  MTProtoVerifyRequest,
  MTProtoStatusResponse,
  MTProtoSetupResponse,
  MTProtoActionResponse,
} from './types';

/**
 * Get current MTProto configuration status
 */
export async function getMTProtoStatus(): Promise<MTProtoStatusResponse> {
  const response = await apiClient.get<MTProtoStatusResponse>('/api/user-mtproto/status');
  return response;
}

/**
 * Initiate MTProto setup - sends verification code to phone
 */
export async function setupMTProto(data: MTProtoSetupRequest): Promise<MTProtoSetupResponse> {
  const response = await apiClient.post<MTProtoSetupResponse>('/api/user-mtproto/setup', data);
  return response;
}

/**
 * Resend verification code using stored credentials
 */
export async function resendMTProto(): Promise<MTProtoSetupResponse> {
  const response = await apiClient.post<MTProtoSetupResponse>('/api/user-mtproto/resend', {});
  return response;
}

/**
 * Verify MTProto setup with code from Telegram
 */
export async function verifyMTProto(data: MTProtoVerifyRequest): Promise<MTProtoActionResponse> {
  const response = await apiClient.post<MTProtoActionResponse>('/api/user-mtproto/verify', data);
  return response;
}

/**
 * Disconnect MTProto client (removes session, keeps credentials)
 */
export async function disconnectMTProto(): Promise<MTProtoActionResponse> {
  const response = await apiClient.post<MTProtoActionResponse>('/api/user-mtproto/disconnect', {});
  return response;
}

/**
 * Remove all MTProto configuration
 */
export async function removeMTProto(): Promise<MTProtoActionResponse> {
  const response = await apiClient.delete<MTProtoActionResponse>('/api/user-mtproto/remove');
  return response;
}

/**
 * Get MTProto setting for a specific channel
 */
export async function getChannelMTProtoSetting(channelId: number): Promise<{
  mtproto_enabled: boolean;
  channel_id: number;
  created_at?: string;
  updated_at?: string
}> {
  const response = await apiClient.get<{
    mtproto_enabled: boolean;
    channel_id: number;
    created_at?: string;
    updated_at?: string
  }>(`/api/user-mtproto/channels/${channelId}`);
  return response;
}

/**
 * Toggle MTProto for a specific channel
 */
export async function toggleChannelMTProto(
  channelId: number,
  enabled: boolean
): Promise<{ mtproto_enabled: boolean; channel_id: number; updated_at: string }> {
  const response = await apiClient.post<{
    mtproto_enabled: boolean;
    channel_id: number;
    updated_at: string
  }>(`/api/user-mtproto/channels/${channelId}/toggle`, {
    enabled
  });
  return response;
}
