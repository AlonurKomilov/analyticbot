/**
 * Domain Models
 *
 * Core domain model types used across the application.
 * This file serves as a central location for shared domain types.
 */

// Utility types
export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
export type ID = string | number;
export type Timestamp = string | number | Date;
export type Theme = 'light' | 'dark' | 'auto';
export type SortOrder = 'asc' | 'desc';
export type NotificationType = 'info' | 'success' | 'warning' | 'error';

// Notification type
export interface Notification {
  id: ID;
  message: string;
  type: NotificationType;
  timestamp: Timestamp;
  read?: boolean;
}

// Churn Prediction
export interface ChurnPrediction {
  userId: ID;
  riskLevel: 'low' | 'medium' | 'high';
  probability: number;
  factors?: string[];
}

// Time periods
export type TimePeriod = '1h' | '6h' | '12h' | '24h' | '7d' | '30d' | '90d' | 'all' | 'custom';

// Chart configuration
export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'area';
  title?: string;
  xAxis?: string;
  yAxis?: string;
  colors?: string[];
}

// Best time recommendations
export interface BestTimeRecommendation {
  dayOfWeek: number;
  hour: number;
  engagementScore: number;
  confidence: number;
}

// Scheduled posts (if not in api.ts)
export interface ScheduledPost {
  id: string | number;
  channelId: string | number;
  content: string;
  scheduledTime: string;
  status: 'scheduled' | 'published' | 'failed';
  mediaUrls?: string[];
}

// Engagement metrics
export interface EngagementMetrics {
  likes: number;
  shares: number;
  comments: number;
  reactions: number;
  engagementRate: number;
  averageEngagementTime?: number;
}

// Media management
export interface PendingMedia {
  id: string;
  file: File;
  preview?: string;
  uploadProgress?: number;
  status: 'pending' | 'uploading' | 'complete' | 'error';
  type?: 'image' | 'video' | 'document';
}

// Data sources
export type DataSource = 'api' | 'cache' | 'demo' | 'mock';

// Loading state types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

// Validation result
export interface ValidationResult {
  valid: boolean;
  message?: string;
  errors?: string[];
}

// API Status
export type ApiStatus = 'idle' | 'loading' | 'success' | 'error';

// Placeholder types - to be properly defined when needed
export interface User {
  id: string | number;
  [key: string]: any;
}

export interface Channel {
  id: string | number;
  [key: string]: any;
}

export interface Post {
  id: string | number;
  [key: string]: any;
}

export interface ScheduledPost {
  id: string | number;
  [key: string]: any;
}

export interface AnalyticsOverview {
  [key: string]: any;
}

export interface GrowthMetrics {
  [key: string]: any;
}

export interface ReachMetrics {
  [key: string]: any;
}

export interface TopPost {
  [key: string]: any;
}

export interface PostDynamics {
  [key: string]: any;
}

export interface EngagementMetrics {
  [key: string]: any;
}

export interface BestTimeRecommendation {
  [key: string]: any;
}
