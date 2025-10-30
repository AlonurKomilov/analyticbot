/**
 * User Bot Management Types
 * Types for multi-tenant bot credentials and management
 */

/**
 * Bot status enum
 */
export enum BotStatus {
  PENDING = 'pending',
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  RATE_LIMITED = 'rate_limited',
  ERROR = 'error'
}

/**
 * User bot credentials
 */
export interface UserBotCredentials {
  id: number;
  user_id: number;
  bot_username: string | null;
  bot_id: number | null;
  status: BotStatus;
  is_verified: boolean;
  rate_limit_rps: number;
  max_concurrent_requests: number;
  total_requests: number;
  created_at: string;
  updated_at: string;
  last_used_at: string | null;
  suspension_reason?: string | null;
}

/**
 * Create bot request
 */
export interface CreateBotRequest {
  bot_token: string;
  api_id?: number;
  api_hash?: string;
  max_requests_per_second?: number;
  max_concurrent_requests?: number;
}

/**
 * Create bot response
 */
export interface CreateBotResponse {
  success: boolean;
  bot_id: number;
  bot_username: string | null;
  status: BotStatus;
}

/**
 * Bot status response
 */
export interface BotStatusResponse {
  user_id: number;
  bot_username: string | null;
  bot_id: number | null;
  status: BotStatus;
  is_verified: boolean;
  max_requests_per_second: number;
  max_concurrent_requests: number;
  total_requests: number;
  created_at: string;
  updated_at?: string;
  last_used_at: string | null;
  suspension_reason?: string | null;
}

/**
 * Verify bot request
 */
export interface VerifyBotRequest {
  send_test_message?: boolean;
  test_chat_id?: number;
  test_message?: string;
}

/**
 * Verify bot response
 */
export interface VerifyBotResponse {
  success: boolean;
  bot_username: string | null;
  bot_id: number | null;
  is_verified: boolean;
  message: string;
}

/**
 * Update rate limit request
 */
export interface UpdateRateLimitRequest {
  max_requests_per_second: number;
  max_concurrent_requests: number;
}

/**
 * Rate limit update response
 */
export interface RateLimitUpdateResponse {
  success: boolean;
  max_requests_per_second: number;
  max_concurrent_requests: number;
}

/**
 * Remove bot response
 */
export interface RemoveBotResponse {
  success: boolean;
  message: string;
}

/**
 * Admin bot list item
 */
export interface AdminBotListItem {
  user_id: number;
  bot_username: string | null;
  status: BotStatus;
  is_verified: boolean;
  max_requests_per_second: number;
  max_concurrent_requests: number;
  total_requests: number;
  created_at: string;
  last_used_at: string | null;
}

/**
 * Admin bot list response
 */
export interface AdminBotListResponse {
  bots: AdminBotListItem[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Suspend bot request
 */
export interface SuspendBotRequest {
  reason: string;
}

/**
 * Suspend bot response
 */
export interface SuspendBotResponse {
  success: boolean;
  status: BotStatus;
  reason: string;
}

/**
 * Activate bot response
 */
export interface ActivateBotResponse {
  success: boolean;
  status: BotStatus;
  is_verified: boolean;
}

/**
 * Admin access response
 */
export interface AdminAccessResponse {
  success: boolean;
  message: string;
  bot_username: string | null;
  admin_id: number;
}

/**
 * Bot wizard step
 */
export interface BotWizardStep {
  id: number;
  title: string;
  description: string;
  completed: boolean;
}

/**
 * Bot wizard state
 */
export interface BotWizardState {
  currentStep: number;
  steps: BotWizardStep[];
  formData: Partial<CreateBotRequest>;
  errors: Record<string, string>;
  isSubmitting: boolean;
}
