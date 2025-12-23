/**
 * Post Validation Service
 *
 * Pure business logic for post validation and scheduling
 * Separated from store for better testability and reusability
 */

export interface PostValidationResult {
  isValid: boolean;
  errors: string[];
}

export interface ScheduleValidationResult {
  isValid: boolean;
  error?: string;
  scheduledTime?: Date;
}

/**
 * Validate post content
 */
export function validatePostContent(content: string): { isValid: boolean; error?: string } {
  const trimmed = content.trim();

  // Check if empty
  if (!trimmed) {
    return {
      isValid: false,
      error: 'Post content cannot be empty',
    };
  }

  // Check minimum length (at least 1 character)
  if (trimmed.length < 1) {
    return {
      isValid: false,
      error: 'Post must contain at least 1 character',
    };
  }

  // Check maximum length (Telegram allows up to 4096 characters)
  if (trimmed.length > 4096) {
    return {
      isValid: false,
      error: `Post content exceeds maximum length (${trimmed.length}/4096 characters)`,
    };
  }

  return { isValid: true };
}

/**
 * Validate channel selection for post
 */
export function validateChannelSelection(channelId: string | number | null | undefined): {
  isValid: boolean;
  error?: string;
} {
  if (!channelId) {
    return {
      isValid: false,
      error: 'Please select a channel',
    };
  }

  return { isValid: true };
}

/**
 * Validate scheduled time for post
 */
export function validateScheduleTime(
  scheduledTime: Date | string | null | undefined,
  minMinutesFromNow: number = 1
): ScheduleValidationResult {
  if (!scheduledTime) {
    return {
      isValid: false,
      error: 'Scheduled time is required',
    };
  }

  const scheduleDate = typeof scheduledTime === 'string' ? new Date(scheduledTime) : scheduledTime;

  // Check if valid date
  if (isNaN(scheduleDate.getTime())) {
    return {
      isValid: false,
      error: 'Invalid date format',
    };
  }

  const now = new Date();
  const minTime = new Date(now.getTime() + minMinutesFromNow * 60 * 1000);

  // Check if in the past
  if (scheduleDate < now) {
    return {
      isValid: false,
      error: 'Scheduled time cannot be in the past',
    };
  }

  // Check if too soon (within minimum time)
  if (scheduleDate < minTime) {
    return {
      isValid: false,
      error: `Scheduled time must be at least ${minMinutesFromNow} minute(s) from now`,
    };
  }

  // Check if too far in the future (e.g., max 1 year)
  const maxTime = new Date(now.getTime() + 365 * 24 * 60 * 60 * 1000);
  if (scheduleDate > maxTime) {
    return {
      isValid: false,
      error: 'Scheduled time cannot be more than 1 year in the future',
    };
  }

  return {
    isValid: true,
    scheduledTime: scheduleDate,
  };
}

/**
 * Validate complete post data before submission
 */
export function validatePost(data: {
  content?: string;
  channelId?: string | number | null;
  scheduledTime?: Date | string | null;
  mediaIds?: string[];
}): PostValidationResult {
  const errors: string[] = [];

  // Validate content
  const contentValidation = validatePostContent(data.content || '');
  if (!contentValidation.isValid) {
    errors.push(contentValidation.error || 'Invalid content');
  }

  // Validate channel selection
  const channelValidation = validateChannelSelection(data.channelId);
  if (!channelValidation.isValid) {
    errors.push(channelValidation.error || 'Invalid channel');
  }

  // Validate scheduled time
  const timeValidation = validateScheduleTime(data.scheduledTime);
  if (!timeValidation.isValid) {
    errors.push(timeValidation.error || 'Invalid schedule time');
  }

  // Validate media if present
  if (data.mediaIds && data.mediaIds.length > 10) {
    errors.push('Maximum 10 media files allowed per post');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Check if post content contains URLs
 */
export function containsUrls(content: string): boolean {
  const urlPattern = /(https?:\/\/[^\s]+)/g;
  return urlPattern.test(content);
}

/**
 * Extract URLs from post content
 */
export function extractUrls(content: string): string[] {
  const urlPattern = /(https?:\/\/[^\s]+)/g;
  const matches = content.match(urlPattern);
  return matches || [];
}

/**
 * Count characters for Telegram's limit
 * Telegram counts emojis as multiple characters
 */
export function countTelegramCharacters(content: string): number {
  // Basic implementation - can be enhanced to handle emojis properly
  return content.length;
}

/**
 * Validate media file for Telegram post
 */
export function validateMediaFile(file: File): { isValid: boolean; error?: string } {
  // Check file size (Telegram limits: 2GB for files, 10MB for photos)
  const maxPhotoSize = 10 * 1024 * 1024; // 10 MB
  const maxFileSize = 2 * 1024 * 1024 * 1024; // 2 GB

  if (file.type.startsWith('image/')) {
    if (file.size > maxPhotoSize) {
      return {
        isValid: false,
        error: `Image file too large (max 10 MB). Current: ${(file.size / 1024 / 1024).toFixed(2)} MB`,
      };
    }
  } else {
    if (file.size > maxFileSize) {
      return {
        isValid: false,
        error: `File too large (max 2 GB). Current: ${(file.size / 1024 / 1024 / 1024).toFixed(2)} GB`,
      };
    }
  }

  // Check allowed file types
  const allowedTypes = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'video/mp4',
    'video/quicktime',
    'audio/mpeg',
    'audio/mp4',
    'application/pdf',
  ];

  if (!allowedTypes.includes(file.type)) {
    return {
      isValid: false,
      error: `File type not supported: ${file.type}`,
    };
  }

  return { isValid: true };
}

/**
 * Generate schedule suggestions (common times)
 */
export function getScheduleSuggestions(): Array<{ label: string; date: Date }> {
  const now = new Date();
  const suggestions: Array<{ label: string; date: Date }> = [];

  // In 1 hour
  const oneHour = new Date(now.getTime() + 60 * 60 * 1000);
  suggestions.push({ label: 'In 1 hour', date: oneHour });

  // In 3 hours
  const threeHours = new Date(now.getTime() + 3 * 60 * 60 * 1000);
  suggestions.push({ label: 'In 3 hours', date: threeHours });

  // Tomorrow at 9 AM
  const tomorrow9AM = new Date(now);
  tomorrow9AM.setDate(tomorrow9AM.getDate() + 1);
  tomorrow9AM.setHours(9, 0, 0, 0);
  suggestions.push({ label: 'Tomorrow at 9 AM', date: tomorrow9AM });

  // Tomorrow at 6 PM
  const tomorrow6PM = new Date(now);
  tomorrow6PM.setDate(tomorrow6PM.getDate() + 1);
  tomorrow6PM.setHours(18, 0, 0, 0);
  suggestions.push({ label: 'Tomorrow at 6 PM', date: tomorrow6PM });

  // Next Monday at 9 AM
  const nextMonday = new Date(now);
  const daysUntilMonday = (8 - now.getDay()) % 7 || 7;
  nextMonday.setDate(nextMonday.getDate() + daysUntilMonday);
  nextMonday.setHours(9, 0, 0, 0);
  suggestions.push({ label: 'Next Monday at 9 AM', date: nextMonday });

  return suggestions;
}
