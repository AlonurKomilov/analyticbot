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
  MTProtoQRLoginResponse,
  MTProtoQRStatusResponse,
} from './types';

/**
 * Get current MTProto configuration status
 */
export async function getMTProtoStatus(): Promise<MTProtoStatusResponse> {
  const response = await apiClient.get<MTProtoStatusResponse>('/user-mtproto/status');
  return response;
}

/**
 * Initiate MTProto setup - sends verification code to phone
 */
export async function setupMTProto(data: MTProtoSetupRequest): Promise<MTProtoSetupResponse> {
  const response = await apiClient.post<MTProtoSetupResponse>('/user-mtproto/setup', data);
  return response;
}

/**
 * Simplified MTProto setup - only requires phone number
 * Uses system-provided API credentials
 */
export async function setupMTProtoSimple(phone: string): Promise<MTProtoSetupResponse> {
  const response = await apiClient.post<MTProtoSetupResponse>('/user-mtproto/setup-simple', {
    mtproto_phone: phone,
  });
  return response;
}

/**
 * Resend verification code using stored credentials
 */
export async function resendMTProto(): Promise<MTProtoSetupResponse> {
  const response = await apiClient.post<MTProtoSetupResponse>('/user-mtproto/resend', {});
  return response;
}

/**
 * Verify MTProto setup with code from Telegram
 */
export async function verifyMTProto(data: MTProtoVerifyRequest): Promise<MTProtoActionResponse> {
  const response = await apiClient.post<MTProtoActionResponse>('/user-mtproto/verify', data);
  return response;
}

/**
 * Disconnect MTProto client (removes session, keeps credentials)
 */
export async function disconnectMTProto(): Promise<MTProtoActionResponse> {
  const response = await apiClient.post<MTProtoActionResponse>('/user-mtproto/disconnect', {});
  return response;
}

/**
 * Remove all MTProto configuration
 */
export async function removeMTProto(): Promise<MTProtoActionResponse> {
  const response = await apiClient.delete<MTProtoActionResponse>('/user-mtproto/remove');
  return response;
}

/**
 * Toggle global MTProto feature (enable/disable for the user)
 * Note: backend exposes this as POST /api/user-mtproto/toggle
 */
export async function toggleGlobalMTProto(enabled: boolean): Promise<MTProtoActionResponse> {
  const response = await apiClient.post<MTProtoActionResponse>('/user-mtproto/toggle', {
    enabled,
  });
  return response;
}

/**
 * Manually connect MTProto client and add to active pool
 * Use this to establish an immediate active connection instead of lazy loading
 */
export async function connectMTProto(): Promise<MTProtoActionResponse> {
  const response = await apiClient.post<MTProtoActionResponse>('/user-mtproto/connect', {});
  return response;
}

/**
 * Get MTProto setting for a specific channel
 * Returns null if no per-channel setting exists (uses global default)
 */
export async function getChannelMTProtoSetting(channelId: number): Promise<{
  mtproto_enabled: boolean;
  channel_id: number;
  created_at?: string;
  updated_at?: string
} | null> {
  try {
    const response = await apiClient.get<{
      mtproto_enabled: boolean;
      channel_id: number;
      created_at?: string;
      updated_at?: string
    }>(`/user-mtproto/channels/${channelId}/settings`);
    return response;
  } catch (error: any) {
    // 404 is expected when no per-channel setting exists (uses global default)
    if (error.status === 404) {
      return null;
    }
    throw error;
  }
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
  }>(`/user-mtproto/channels/${channelId}/toggle`, {
    enabled
  });
  return response;
}

/**
 * Request QR code for login
 * Returns a QR code URL and optional base64 image
 */
export async function requestQRLogin(): Promise<MTProtoQRLoginResponse> {
  const response = await apiClient.post<MTProtoQRLoginResponse>('/user-mtproto/qr-login/request', {});
  return response;
}

/**
 * Check QR login status
 * Should be polled every 2-3 seconds after displaying QR code
 */
export async function checkQRLoginStatus(): Promise<MTProtoQRStatusResponse> {
  const response = await apiClient.get<MTProtoQRStatusResponse>('/user-mtproto/qr-login/status');
  return response;
}

/**
 * Submit 2FA password for QR login
 * Called when QR status returns '2fa_required'
 */
export async function submitQR2FA(password: string): Promise<MTProtoQRStatusResponse> {
  const response = await apiClient.post<MTProtoQRStatusResponse>('/user-mtproto/qr-login/2fa', {
    password,
  });
  return response;
}
