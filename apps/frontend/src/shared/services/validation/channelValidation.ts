/**
 * Channel Validation Service
 *
 * Pure business logic for channel validation and username handling
 * Separated from store for better testability and reusability
 */

export interface ChannelValidationResult {
  isValid: boolean;
  username: string;
  error?: string;
}

export interface UsernameFormatResult {
  formatted: string;
  original: string;
  hasAtSymbol: boolean;
}

/**
 * Validate channel username format
 * Returns formatted username and validation status
 */
export function validateChannelUsername(username: string): ChannelValidationResult {
  // Trim whitespace
  const trimmed = username.trim();

  // Check if empty
  if (!trimmed) {
    return {
      isValid: false,
      username: trimmed,
      error: 'Channel username cannot be empty',
    };
  }

  // Check minimum length (Telegram usernames are at least 5 characters)
  const withoutAt = trimmed.replace('@', '');
  if (withoutAt.length < 5) {
    return {
      isValid: false,
      username: trimmed,
      error: 'Channel username must be at least 5 characters',
    };
  }

  // Check maximum length (Telegram usernames are max 32 characters)
  if (withoutAt.length > 32) {
    return {
      isValid: false,
      username: trimmed,
      error: 'Channel username must be 32 characters or less',
    };
  }

  // Check valid characters (alphanumeric and underscores only)
  const validPattern = /^@?[a-zA-Z0-9_]+$/;
  if (!validPattern.test(trimmed)) {
    return {
      isValid: false,
      username: trimmed,
      error: 'Channel username can only contain letters, numbers, and underscores',
    };
  }

  // Username is valid
  return {
    isValid: true,
    username: trimmed,
  };
}

/**
 * Format channel username to ensure it starts with @
 */
export function formatChannelUsername(username: string): UsernameFormatResult {
  const trimmed = username.trim();
  const hasAtSymbol = trimmed.startsWith('@');

  return {
    formatted: hasAtSymbol ? trimmed : `@${trimmed}`,
    original: username,
    hasAtSymbol,
  };
}

/**
 * Clean channel username (remove @ symbol)
 */
export function cleanChannelUsername(username: string): string {
  return username.trim().replace(/^@/, '');
}

/**
 * Check if channel username is a valid Telegram username format
 * This performs local validation without API call
 */
export function isValidTelegramUsername(username: string): boolean {
  const validation = validateChannelUsername(username);
  return validation.isValid;
}

/**
 * Validate channel data completeness
 */
export function validateChannelData(data: {
  username?: string;
  title?: string;
  members_count?: number;
}): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!data.username) {
    errors.push('Username is required');
  } else {
    const usernameValidation = validateChannelUsername(data.username);
    if (!usernameValidation.isValid) {
      errors.push(usernameValidation.error || 'Invalid username format');
    }
  }

  if (data.title && data.title.length > 128) {
    errors.push('Title must be 128 characters or less');
  }

  if (data.members_count !== undefined && data.members_count < 0) {
    errors.push('Members count cannot be negative');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Extract username from various Telegram channel formats
 * Handles: t.me/username, @username, username, https://t.me/username
 */
export function extractChannelUsername(input: string): string | null {
  const trimmed = input.trim();

  // Pattern 1: Already clean username with or without @
  if (/^@?[a-zA-Z0-9_]+$/.test(trimmed)) {
    return cleanChannelUsername(trimmed);
  }

  // Pattern 2: t.me/username or https://t.me/username
  const telegramUrlPattern = /(?:https?:\/\/)?(?:www\.)?t\.me\/([a-zA-Z0-9_]+)/;
  const match = trimmed.match(telegramUrlPattern);

  if (match && match[1]) {
    return match[1];
  }

  // Pattern 3: telegram.me/username or https://telegram.me/username
  const telegramMePattern = /(?:https?:\/\/)?(?:www\.)?telegram\.me\/([a-zA-Z0-9_]+)/;
  const telegramMatch = trimmed.match(telegramMePattern);

  if (telegramMatch && telegramMatch[1]) {
    return telegramMatch[1];
  }

  return null;
}

/**
 * Batch validate multiple channel usernames
 */
export function validateChannelUsernames(usernames: string[]): {
  valid: string[];
  invalid: Array<{ username: string; error: string }>;
} {
  const valid: string[] = [];
  const invalid: Array<{ username: string; error: string }> = [];

  usernames.forEach((username) => {
    const validation = validateChannelUsername(username);
    if (validation.isValid) {
      valid.push(validation.username);
    } else {
      invalid.push({
        username,
        error: validation.error || 'Invalid username',
      });
    }
  });

  return { valid, invalid };
}
