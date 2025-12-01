/**
 * UserBotDashboard Types
 */

export interface DialogState {
  showRemoveDialog: boolean;
  showRateLimitDialog: boolean;
  showTestMessageDialog: boolean;
}

export interface TestMessageState {
  testMessage: string;
  selectedChannelId: string;
  manualChatId: string;
  useManualInput: boolean;
}

export interface RateLimitState {
  rateLimitRps: string;
  maxConcurrent: string;
}

export type StatusColor = 'success' | 'error' | 'warning' | 'info' | 'default';
