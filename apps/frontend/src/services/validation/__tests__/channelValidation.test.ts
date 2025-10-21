/**
 * Channel Validation Service Tests
 */

import { describe, it, expect } from 'vitest';
import {
  validateChannelUsername,
  formatChannelUsername,
  cleanChannelUsername,
  isValidTelegramUsername,
  extractChannelUsername,
  validateChannelUsernames,
  validateChannelData,
} from '../channelValidation';

describe('channelValidation', () => {
  describe('validateChannelUsername', () => {
    it('should validate correct usernames', () => {
      const result = validateChannelUsername('@testchannel');
      expect(result.isValid).toBe(true);
      expect(result.username).toBe('@testchannel');
    });

    it('should validate usernames without @ symbol', () => {
      const result = validateChannelUsername('testchannel');
      expect(result.isValid).toBe(true);
      expect(result.username).toBe('testchannel');
    });

    it('should reject empty usernames', () => {
      const result = validateChannelUsername('');
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('cannot be empty');
    });

    it('should reject usernames that are too short', () => {
      const result = validateChannelUsername('@abc');
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('at least 5 characters');
    });

    it('should reject usernames that are too long', () => {
      const result = validateChannelUsername('@' + 'a'.repeat(33));
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('32 characters or less');
    });

    it('should reject usernames with invalid characters', () => {
      const result = validateChannelUsername('@test-channel');
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('letters, numbers, and underscores');
    });

    it('should allow underscores in usernames', () => {
      const result = validateChannelUsername('@test_channel_123');
      expect(result.isValid).toBe(true);
    });
  });

  describe('formatChannelUsername', () => {
    it('should add @ symbol if missing', () => {
      const result = formatChannelUsername('testchannel');
      expect(result.formatted).toBe('@testchannel');
      expect(result.hasAtSymbol).toBe(false);
    });

    it('should keep @ symbol if present', () => {
      const result = formatChannelUsername('@testchannel');
      expect(result.formatted).toBe('@testchannel');
      expect(result.hasAtSymbol).toBe(true);
    });

    it('should trim whitespace', () => {
      const result = formatChannelUsername('  testchannel  ');
      expect(result.formatted).toBe('@testchannel');
    });
  });

  describe('cleanChannelUsername', () => {
    it('should remove @ symbol', () => {
      const result = cleanChannelUsername('@testchannel');
      expect(result).toBe('testchannel');
    });

    it('should handle usernames without @ symbol', () => {
      const result = cleanChannelUsername('testchannel');
      expect(result).toBe('testchannel');
    });

    it('should trim whitespace', () => {
      const result = cleanChannelUsername('  @testchannel  ');
      expect(result).toBe('testchannel');
    });
  });

  describe('isValidTelegramUsername', () => {
    it('should return true for valid usernames', () => {
      expect(isValidTelegramUsername('@testchannel')).toBe(true);
      expect(isValidTelegramUsername('testchannel')).toBe(true);
      expect(isValidTelegramUsername('@test_channel_123')).toBe(true);
    });

    it('should return false for invalid usernames', () => {
      expect(isValidTelegramUsername('')).toBe(false);
      expect(isValidTelegramUsername('@abc')).toBe(false);
      expect(isValidTelegramUsername('@test-channel')).toBe(false);
    });
  });

  describe('extractChannelUsername', () => {
    it('should extract from clean username', () => {
      expect(extractChannelUsername('@testchannel')).toBe('testchannel');
      expect(extractChannelUsername('testchannel')).toBe('testchannel');
    });

    it('should extract from t.me URL', () => {
      expect(extractChannelUsername('t.me/testchannel')).toBe('testchannel');
      expect(extractChannelUsername('https://t.me/testchannel')).toBe('testchannel');
      expect(extractChannelUsername('http://t.me/testchannel')).toBe('testchannel');
    });

    it('should extract from telegram.me URL', () => {
      expect(extractChannelUsername('telegram.me/testchannel')).toBe('testchannel');
      expect(extractChannelUsername('https://telegram.me/testchannel')).toBe('testchannel');
    });

    it('should return null for invalid input', () => {
      expect(extractChannelUsername('invalid-format')).toBe(null);
      expect(extractChannelUsername('https://example.com')).toBe(null);
    });
  });

  describe('validateChannelUsernames', () => {
    it('should separate valid and invalid usernames', () => {
      const result = validateChannelUsernames([
        '@validchannel',
        'anothergood',
        '@abc', // Too short
        '@test-channel', // Invalid characters
        '@valid_channel_123',
      ]);

      expect(result.valid).toHaveLength(3);
      expect(result.valid).toContain('@validchannel');
      expect(result.valid).toContain('anothergood');
      expect(result.valid).toContain('@valid_channel_123');

      expect(result.invalid).toHaveLength(2);
      expect(result.invalid[0].username).toBe('@abc');
      expect(result.invalid[1].username).toBe('@test-channel');
    });

    it('should handle empty array', () => {
      const result = validateChannelUsernames([]);
      expect(result.valid).toHaveLength(0);
      expect(result.invalid).toHaveLength(0);
    });
  });

  describe('validateChannelData', () => {
    it('should validate complete channel data', () => {
      const result = validateChannelData({
        username: '@testchannel',
        title: 'Test Channel',
        members_count: 1000,
      });

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject missing username', () => {
      const result = validateChannelData({
        title: 'Test Channel',
      });

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Username is required');
    });

    it('should reject invalid username', () => {
      const result = validateChannelData({
        username: '@abc', // Too short
      });

      expect(result.isValid).toBe(false);
      expect(result.errors.some((e) => e.includes('5 characters'))).toBe(true);
    });

    it('should reject title that is too long', () => {
      const result = validateChannelData({
        username: '@testchannel',
        title: 'a'.repeat(129),
      });

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Title must be 128 characters or less');
    });

    it('should reject negative members count', () => {
      const result = validateChannelData({
        username: '@testchannel',
        members_count: -10,
      });

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Members count cannot be negative');
    });

    it('should collect multiple errors', () => {
      const result = validateChannelData({
        title: 'a'.repeat(129),
        members_count: -10,
      });

      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(3); // Missing username + long title + negative count
    });
  });
});
