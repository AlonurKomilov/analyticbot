/**
 * MTProto Setup Feature - Type Definitions
 */

export interface MTProtoSetupRequest {
  mtproto_api_id: number;
  telegram_api_hash: string;
  mtproto_phone: string;
}

export interface MTProtoSimpleSetupRequest {
  mtproto_phone: string;
}

export interface MTProtoVerifyRequest {
  verification_code: string;
  phone_code_hash: string;
  password?: string;
}

export interface MTProtoStatusResponse {
  configured: boolean;
  verified: boolean;
  phone: string | null;
  api_id: number | null;
  connected: boolean; // True if session ready OR actively connected
  actively_connected?: boolean; // True only if client is in active pool
  last_used: string | null;
  can_read_history: boolean;
  mtproto_enabled?: boolean; // Global MTProto enable/disable flag
}

export interface MTProtoSetupResponse {
  success: boolean;
  phone_code_hash: string;
  message: string;
}

export interface MTProtoActionResponse {
  success: boolean;
  message: string;
}

export interface MTProtoQRLoginResponse {
  success: boolean;
  qr_code_url: string;
  qr_code_base64: string | null;
  expires_in: number;
  message: string;
}

export interface MTProtoQRStatusResponse {
  status: 'pending' | 'success' | 'expired' | '2fa_required' | 'error';
  success: boolean;
  message: string;
  user_id?: number;
  needs_2fa?: boolean;
}

export interface MTProtoQR2FARequest {
  password: string;
}
