/**
 * MTProto Setup Feature - Type Definitions
 */

export interface MTProtoSetupRequest {
  telegram_api_id: number;
  telegram_api_hash: string;
  telegram_phone: string;
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
  connected: boolean;
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
