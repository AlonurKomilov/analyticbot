/**
 * Overview Page Utility Functions
 */

import React from 'react';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

export function formatNumber(num: number | undefined | null): string {
  if (num === undefined || num === null) return '0';
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toLocaleString();
}

export function formatPercentage(num: number | undefined | null, decimals = 2): string {
  if (num === undefined || num === null) return '0%';
  return `${num.toFixed(decimals)}%`;
}

export interface ChangeInfo {
  text: string;
  color: string;
  icon: React.ReactNode | null;
}

export function formatChange(change: number): ChangeInfo {
  if (change > 0) {
    return {
      text: `+${formatNumber(change)}`,
      color: 'success.main',
      icon: React.createElement(TrendingUp, { fontSize: 'small' }),
    };
  } else if (change < 0) {
    return {
      text: formatNumber(change),
      color: 'error.main',
      icon: React.createElement(TrendingDown, { fontSize: 'small' }),
    };
  }
  return {
    text: '0',
    color: 'text.secondary',
    icon: null,
  };
}
