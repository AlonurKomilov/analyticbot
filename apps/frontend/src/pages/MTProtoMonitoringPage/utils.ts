/**
 * MTProto Monitoring Utilities
 * Shared helper functions for monitoring components
 */

/**
 * Format date string to locale date time
 */
export const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return 'Never';
  const date = new Date(dateStr);
  return date.toLocaleString();
};

/**
 * Format time ago string (e.g., "5 minutes ago")
 */
export const formatTimeAgo = (dateStr: string | null): string => {
  if (!dateStr) return 'Never';
  const date = new Date(dateStr);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

/**
 * Get health color based on score
 */
export const getHealthColor = (score: number): 'success' | 'warning' | 'error' => {
  if (score >= 80) return 'success';
  if (score >= 50) return 'warning';
  return 'error';
};
