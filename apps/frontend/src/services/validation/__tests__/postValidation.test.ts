/**
 * Post Validation Service Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  validatePostContent,
  validateChannelSelection,
  validateScheduleTime,
  validatePost,
  containsUrls,
  extractUrls,
  validateMediaFile,
  getScheduleSuggestions,
} from '../postValidation';

describe('postValidation', () => {
  beforeEach(() => {
    // Reset Date to real implementation for each test
    vi.useRealTimers();
  });

  describe('validatePostContent', () => {
    it('should validate correct content', () => {
      const result = validatePostContent('This is a valid post');
      expect(result.isValid).toBe(true);
    });

    it('should reject empty content', () => {
      const result = validatePostContent('');
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('cannot be empty');
    });

    it('should reject whitespace-only content', () => {
      const result = validatePostContent('   ');
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('cannot be empty');
    });

    it('should reject content exceeding 4096 characters', () => {
      const longContent = 'a'.repeat(4097);
      const result = validatePostContent(longContent);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('exceeds maximum length');
    });

    it('should accept content at max length (4096 characters)', () => {
      const maxContent = 'a'.repeat(4096);
      const result = validatePostContent(maxContent);
      expect(result.isValid).toBe(true);
    });
  });

  describe('validateChannelSelection', () => {
    it('should validate numeric channel ID', () => {
      const result = validateChannelSelection(123);
      expect(result.isValid).toBe(true);
    });

    it('should validate string channel ID', () => {
      const result = validateChannelSelection('channel-123');
      expect(result.isValid).toBe(true);
    });

    it('should reject null channel ID', () => {
      const result = validateChannelSelection(null);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('select a channel');
    });

    it('should reject undefined channel ID', () => {
      const result = validateChannelSelection(undefined);
      expect(result.isValid).toBe(false);
    });
  });

  describe('validateScheduleTime', () => {
    it('should validate future date', () => {
      const futureDate = new Date(Date.now() + 60 * 60 * 1000); // 1 hour from now
      const result = validateScheduleTime(futureDate);
      expect(result.isValid).toBe(true);
      expect(result.scheduledTime).toEqual(futureDate);
    });

    it('should reject past dates', () => {
      const pastDate = new Date(Date.now() - 60 * 60 * 1000); // 1 hour ago
      const result = validateScheduleTime(pastDate);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('cannot be in the past');
    });

    it('should reject dates too close to now (within minimum time)', () => {
      const tooSoon = new Date(Date.now() + 30 * 1000); // 30 seconds from now
      const result = validateScheduleTime(tooSoon, 1); // Minimum 1 minute
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('at least 1 minute');
    });

    it('should reject dates more than 1 year in future', () => {
      const tooFar = new Date(Date.now() + 366 * 24 * 60 * 60 * 1000); // >1 year
      const result = validateScheduleTime(tooFar);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('more than 1 year');
    });

    it('should accept ISO string format', () => {
      const futureDate = new Date(Date.now() + 60 * 60 * 1000);
      const result = validateScheduleTime(futureDate.toISOString());
      expect(result.isValid).toBe(true);
    });

    it('should reject invalid date string', () => {
      const result = validateScheduleTime('invalid-date');
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('Invalid date format');
    });

    it('should reject null', () => {
      const result = validateScheduleTime(null);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('required');
    });
  });

  describe('validatePost', () => {
    const validFutureDate = new Date(Date.now() + 60 * 60 * 1000);

    it('should validate complete post data', () => {
      const result = validatePost({
        content: 'Valid post content',
        channelId: 123,
        scheduledTime: validFutureDate,
      });

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should collect all validation errors', () => {
      const result = validatePost({
        content: '', // Empty
        channelId: null, // Missing
        scheduledTime: new Date(Date.now() - 1000), // Past
      });

      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(3);
    });

    it('should reject too many media files', () => {
      const result = validatePost({
        content: 'Valid content',
        channelId: 123,
        scheduledTime: validFutureDate,
        mediaIds: Array(11).fill('media-id'), // 11 files
      });

      expect(result.isValid).toBe(false);
      expect(result.errors.some((e) => e.includes('Maximum 10 media'))).toBe(true);
    });

    it('should accept valid media count', () => {
      const result = validatePost({
        content: 'Valid content',
        channelId: 123,
        scheduledTime: validFutureDate,
        mediaIds: Array(10).fill('media-id'), // Exactly 10
      });

      expect(result.isValid).toBe(true);
    });
  });

  describe('containsUrls', () => {
    it('should detect HTTP URLs', () => {
      expect(containsUrls('Check this out http://example.com')).toBe(true);
    });

    it('should detect HTTPS URLs', () => {
      expect(containsUrls('Check this out https://example.com')).toBe(true);
    });

    it('should detect multiple URLs', () => {
      expect(containsUrls('Links: https://one.com and https://two.com')).toBe(true);
    });

    it('should return false for no URLs', () => {
      expect(containsUrls('Just plain text')).toBe(false);
    });
  });

  describe('extractUrls', () => {
    it('should extract single URL', () => {
      const urls = extractUrls('Check this out https://example.com');
      expect(urls).toHaveLength(1);
      expect(urls[0]).toBe('https://example.com');
    });

    it('should extract multiple URLs', () => {
      const urls = extractUrls('Links: https://one.com and https://two.com');
      expect(urls).toHaveLength(2);
      expect(urls).toContain('https://one.com');
      expect(urls).toContain('https://two.com');
    });

    it('should return empty array for no URLs', () => {
      const urls = extractUrls('Just plain text');
      expect(urls).toHaveLength(0);
    });

    it('should handle HTTP and HTTPS', () => {
      const urls = extractUrls('http://one.com and https://two.com');
      expect(urls).toHaveLength(2);
    });
  });

  describe('validateMediaFile', () => {
    it('should validate image file within size limit', () => {
      const file = new File(['x'.repeat(5 * 1024 * 1024)], 'test.jpg', {
        type: 'image/jpeg',
      });
      const result = validateMediaFile(file);
      expect(result.isValid).toBe(true);
    });

    it('should reject image file exceeding 10 MB', () => {
      const file = new File(['x'.repeat(11 * 1024 * 1024)], 'test.jpg', {
        type: 'image/jpeg',
      });
      const result = validateMediaFile(file);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('Image file too large');
    });

    it('should validate video file within size limit', () => {
      // Create a smaller test file (10MB instead of 100MB to avoid timeout)
      // The validation checks file size, not actual content
      const file = new File(['x'.repeat(10 * 1024 * 1024)], 'test.mp4', {
        type: 'video/mp4',
      });
      const result = validateMediaFile(file);
      expect(result.isValid).toBe(true);
    }, 10000); // 10 second timeout

    it('should reject unsupported file types', () => {
      const file = new File(['test'], 'test.exe', {
        type: 'application/x-msdownload',
      });
      const result = validateMediaFile(file);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('File type not supported');
    });

    it('should accept PDF files', () => {
      const file = new File(['test'], 'test.pdf', {
        type: 'application/pdf',
      });
      const result = validateMediaFile(file);
      expect(result.isValid).toBe(true);
    });

    it('should accept various image formats', () => {
      const formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      formats.forEach((type) => {
        const file = new File(['test'], `test.${type.split('/')[1]}`, { type });
        const result = validateMediaFile(file);
        expect(result.isValid).toBe(true);
      });
    });
  });

  describe('getScheduleSuggestions', () => {
    it('should return 5 schedule suggestions', () => {
      const suggestions = getScheduleSuggestions();
      expect(suggestions).toHaveLength(5);
    });

    it('should have all suggestions in the future', () => {
      const now = new Date();
      const suggestions = getScheduleSuggestions();

      suggestions.forEach((suggestion) => {
        expect(suggestion.date.getTime()).toBeGreaterThan(now.getTime());
      });
    });

    it('should include specific suggestion labels', () => {
      const suggestions = getScheduleSuggestions();
      const labels = suggestions.map((s) => s.label);

      expect(labels).toContain('In 1 hour');
      expect(labels).toContain('In 3 hours');
      expect(labels).toContain('Tomorrow at 9 AM');
      expect(labels).toContain('Tomorrow at 6 PM');
      expect(labels).toContain('Next Monday at 9 AM');
    });

    it('should set tomorrow 9 AM correctly', () => {
      const suggestions = getScheduleSuggestions();
      const tomorrow9AM = suggestions.find((s) => s.label === 'Tomorrow at 9 AM');

      expect(tomorrow9AM).toBeDefined();
      expect(tomorrow9AM!.date.getHours()).toBe(9);
      expect(tomorrow9AM!.date.getMinutes()).toBe(0);
    });
  });
});
