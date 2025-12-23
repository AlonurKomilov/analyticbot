/**
 * User Bot Moderation Types
 * Type definitions for moderation features
 */

// Chat types
export type ChatType = 'channel' | 'group' | 'supergroup';

// Moderation action types
export type ModerationAction = 'delete' | 'warn' | 'mute' | 'ban' | 'kick';

// Message types for welcome/goodbye
export type MessageType = 'welcome' | 'goodbye';

/**
 * Chat Settings Interface
 */
export interface ChatSettings {
  id: number;
  user_id: number;
  chat_id: number;
  chat_type: ChatType;
  chat_title: string | null;

  // Feature toggles
  clean_join_messages: boolean;
  clean_leave_messages: boolean;
  banned_words_enabled: boolean;
  anti_spam_enabled: boolean;
  anti_link_enabled: boolean;
  anti_forward_enabled: boolean;
  welcome_enabled: boolean;
  invite_tracking_enabled: boolean;
  captcha_enabled: boolean;
  slow_mode_enabled: boolean;
  night_mode_enabled: boolean;

  // Anti-spam settings
  spam_action: ModerationAction;
  max_warnings: number;
  warning_action: ModerationAction;
  mute_duration_minutes: number;
  flood_limit: number;
  flood_interval_seconds: number;

  // Night mode
  night_mode_start_hour: number;
  night_mode_end_hour: number;
  night_mode_timezone: string;

  // Permissions
  whitelisted_users: number[];
  admin_users: number[];

  created_at: string;
  updated_at: string;
}

/**
 * Chat Settings Update Request
 */
export interface ChatSettingsUpdate {
  chat_type?: ChatType;
  chat_title?: string;

  clean_join_messages?: boolean;
  clean_leave_messages?: boolean;
  banned_words_enabled?: boolean;
  anti_spam_enabled?: boolean;
  anti_link_enabled?: boolean;
  anti_forward_enabled?: boolean;
  welcome_enabled?: boolean;
  invite_tracking_enabled?: boolean;
  captcha_enabled?: boolean;
  slow_mode_enabled?: boolean;
  night_mode_enabled?: boolean;

  spam_action?: ModerationAction;
  max_warnings?: number;
  warning_action?: ModerationAction;
  mute_duration_minutes?: number;
  flood_limit?: number;
  flood_interval_seconds?: number;

  night_mode_start_hour?: number;
  night_mode_end_hour?: number;
  night_mode_timezone?: string;

  whitelisted_users?: number[];
  admin_users?: number[];
}

/**
 * Banned Word Interface
 */
export interface BannedWord {
  id: number;
  user_id: number;
  chat_id: number;
  word: string;
  is_regex: boolean;
  action: ModerationAction;
  created_at: string;
}

/**
 * Banned Word Create Request
 */
export interface BannedWordCreate {
  word: string;
  is_regex?: boolean;
  action?: ModerationAction;
}

/**
 * Welcome Message Interface
 */
export interface WelcomeMessage {
  id: number;
  user_id: number;
  chat_id: number;
  message_type: MessageType;
  message_template: string;
  parse_mode: string;
  buttons: MessageButton[] | null;
  delete_after_seconds: number | null;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Message Button for inline keyboards
 */
export interface MessageButton {
  text: string;
  url?: string;
  callback_data?: string;
}

/**
 * Welcome Message Create/Update Request
 */
export interface WelcomeMessageUpsert {
  message_type: MessageType;
  message_template: string;
  parse_mode?: string;
  buttons?: MessageButton[];
  delete_after_seconds?: number;
  is_enabled?: boolean;
}

/**
 * Invite Record Interface
 */
export interface InviteRecord {
  id: number;
  inviter_tg_id: number;
  inviter_username: string | null;
  inviter_name: string | null;
  invited_tg_id: number;
  invited_username: string | null;
  invited_name: string | null;
  invited_at: string;
  is_still_member: boolean;
  left_at: string | null;
}

/**
 * Invite Statistics Interface
 */
export interface InviteStats {
  chat_id: number;
  leaderboard: InviterStats[];
  total_invites: number;
  active_members_invited: number;
}

/**
 * Individual Inviter Stats
 */
export interface InviterStats {
  inviter_tg_id: number;
  inviter_username: string | null;
  inviter_name: string | null;
  total_invited: number;
  still_members: number;
  left_members: number;
}

/**
 * Moderation Log Entry
 */
export interface ModerationLogEntry {
  id: number;
  user_id: number;
  chat_id: number;
  target_tg_id: number;
  target_username: string | null;
  target_name: string | null;
  action: ModerationAction;
  reason: string | null;
  message_content: string | null;
  moderator_tg_id: number | null;
  created_at: string;
}

/**
 * Moderation Log Response
 */
export interface ModerationLogResponse {
  logs: ModerationLogEntry[];
  total: number;
  page: number;
  per_page: number;
}

/**
 * Warning Interface
 */
export interface Warning {
  id: number;
  user_id: number;
  chat_id: number;
  target_tg_id: number;
  target_username: string | null;
  warning_type: string;
  reason: string | null;
  issued_by_tg_id: number | null;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
}

/**
 * User Warnings Response
 */
export interface UserWarningsResponse {
  warnings: Warning[];
  total_active: number;
  max_warnings: number;
}

/**
 * Chat List Item (for channel/group selector)
 */
export interface ModerationChatItem {
  chat_id: number;
  chat_title: string;
  chat_type: ChatType;
  settings_configured: boolean;
}
