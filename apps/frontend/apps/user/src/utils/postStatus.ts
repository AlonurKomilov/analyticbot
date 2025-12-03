/**
 * Post Status Utilities
 *
 * Helper functions for working with post statuses
 *
 * Created: October 25, 2025
 */

import { PostStatus, BackendPostStatus, mapBackendPostStatus } from '@/types';

/**
 * Check if post is published
 *
 * @param status - Post status
 * @returns true if post is published
 */
export function isPostPublished(status: PostStatus): boolean {
  return status === 'published';
}

/**
 * Check if post is scheduled
 *
 * @param status - Post status
 * @returns true if post is scheduled for future
 */
export function isPostScheduled(status: PostStatus): boolean {
  return status === 'scheduled';
}

/**
 * Check if post is being published
 *
 * @param status - Post status
 * @returns true if post is in publishing state
 */
export function isPostPublishing(status: PostStatus): boolean {
  return status === 'publishing';
}

/**
 * Check if post is in draft
 *
 * @param status - Post status
 * @returns true if post is draft
 */
export function isPostDraft(status: PostStatus): boolean {
  return status === 'draft';
}

/**
 * Check if post failed to publish
 *
 * @param status - Post status
 * @returns true if post publishing failed
 */
export function isPostFailed(status: PostStatus): boolean {
  return status === 'failed';
}

/**
 * Check if post was cancelled
 *
 * @param status - Post status
 * @returns true if post was cancelled
 */
export function isPostCancelled(status: PostStatus): boolean {
  return status === 'cancelled';
}

/**
 * Check if post can be edited
 *
 * @param status - Post status
 * @returns true if post can be edited
 */
export function canEditPost(status: PostStatus): boolean {
  return status === 'draft' || status === 'scheduled' || status === 'failed';
}

/**
 * Check if post can be cancelled
 *
 * @param status - Post status
 * @returns true if post can be cancelled
 */
export function canCancelPost(status: PostStatus): boolean {
  return status === 'scheduled';
}

/**
 * Check if post can be deleted
 *
 * @param status - Post status
 * @returns true if post can be deleted
 */
export function canDeletePost(status: PostStatus): boolean {
  // Can delete any post except those currently publishing
  return status !== 'publishing';
}

/**
 * Check if post can be republished
 *
 * @param status - Post status
 * @returns true if post can be republished
 */
export function canRepublishPost(status: PostStatus): boolean {
  return status === 'failed' || status === 'cancelled';
}

/**
 * Get user-friendly post status label
 *
 * @param status - Post status
 * @returns Human-readable status label
 */
export function getPostStatusLabel(status: PostStatus): string {
  switch (status) {
    case 'draft':
      return 'Draft';
    case 'scheduled':
      return 'Scheduled';
    case 'publishing':
      return 'Publishing...';
    case 'published':
      return 'Published';
    case 'failed':
      return 'Failed';
    case 'cancelled':
      return 'Cancelled';
  }
}

/**
 * Get post status description
 *
 * @param status - Post status
 * @returns Description of what the status means
 */
export function getPostStatusDescription(status: PostStatus): string {
  switch (status) {
    case 'draft':
      return 'Post is being edited and not yet scheduled';
    case 'scheduled':
      return 'Post is scheduled for future publication';
    case 'publishing':
      return 'Post is currently being published to the channel';
    case 'published':
      return 'Post has been successfully published';
    case 'failed':
      return 'Post publication failed - you can retry or edit';
    case 'cancelled':
      return 'Scheduled post was cancelled before publication';
  }
}

/**
 * Get post status color for UI
 *
 * @param status - Post status
 * @returns Color designation for status badge
 */
export function getPostStatusColor(status: PostStatus): 'success' | 'info' | 'warning' | 'error' | 'default' {
  switch (status) {
    case 'published':
      return 'success';
    case 'scheduled':
      return 'info';
    case 'publishing':
      return 'info';
    case 'draft':
      return 'default';
    case 'failed':
      return 'error';
    case 'cancelled':
      return 'warning';
  }
}

/**
 * Get available actions for post status
 *
 * @param status - Post status
 * @returns Array of available action names
 */
export function getPostAvailableActions(status: PostStatus): string[] {
  const actions: string[] = [];

  if (canEditPost(status)) {
    actions.push('edit');
  }

  if (canCancelPost(status)) {
    actions.push('cancel');
  }

  if (canDeletePost(status)) {
    actions.push('delete');
  }

  if (canRepublishPost(status)) {
    actions.push('republish');
  }

  if (status === 'published') {
    actions.push('view_analytics');
  }

  return actions;
}

/**
 * Normalize post from backend API
 * Converts backend status to frontend display status
 *
 * @param post - Post object from backend
 * @returns Post with frontend-appropriate status
 */
export function normalizePost(post: any): any {
  if (!post.status) {
    return post;
  }

  // Map backend status to frontend status
  const frontendStatus = mapBackendPostStatus(
    post.status as BackendPostStatus,
    post.scheduledTime
  );

  return {
    ...post,
    status: frontendStatus
  };
}

/**
 * Check if post should show as publishing
 * Based on scheduled time vs current time
 *
 * @param status - Current post status
 * @param scheduledTime - Scheduled publication time
 * @returns true if post should display as publishing
 */
export function shouldShowAsPublishing(status: PostStatus, scheduledTime?: string): boolean {
  if (status !== 'scheduled' || !scheduledTime) {
    return false;
  }

  const scheduled = new Date(scheduledTime).getTime();
  const now = Date.now();

  // Show as publishing if scheduled time has passed
  // But keep showing for max 5 minutes (likely already published, just waiting for status update)
  const timeSinceScheduled = now - scheduled;
  return timeSinceScheduled >= 0 && timeSinceScheduled < 5 * 60 * 1000; // 5 minutes
}

/**
 * Get time until post publication
 *
 * @param scheduledTime - Scheduled publication time
 * @returns Time remaining in human-readable format, or null if not scheduled/already published
 */
export function getTimeUntilPublication(scheduledTime?: string): string | null {
  if (!scheduledTime) {
    return null;
  }

  const scheduled = new Date(scheduledTime).getTime();
  const now = Date.now();
  const diff = scheduled - now;

  if (diff <= 0) {
    return 'Publishing now';
  }

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    return `in ${days} day${days !== 1 ? 's' : ''}`;
  }
  if (hours > 0) {
    return `in ${hours} hour${hours !== 1 ? 's' : ''}`;
  }
  if (minutes > 0) {
    return `in ${minutes} minute${minutes !== 1 ? 's' : ''}`;
  }
  return `in ${seconds} second${seconds !== 1 ? 's' : ''}`;
}
