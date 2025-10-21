/**
 * API Module Index (TypeScript)
 * Unified API exports for the frontend application
 */

// Import unified client
import { apiClient, UnifiedApiClient, AuthStrategies, apiFetch, ApiRequestError } from './client';

// Re-export everything for easy access
export {
  // Main client instance
  apiClient,

  // Class for custom instances
  UnifiedApiClient,

  // Authentication strategies
  AuthStrategies,

  // Backward compatibility
  apiFetch,

  // Error class
  ApiRequestError
};

// Re-export types
export type {
  ApiResponse,
  PaginatedResponse,
  ApiError,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  RefreshTokenRequest,
  User,
  UserRole,
  UserPreferences,
  Channel,
  ChannelMetrics,
  CreateChannelRequest,
  UpdateChannelRequest,
  ChannelValidationResponse,
  Post,
  PostStatus,
  CreatePostRequest,
  UpdatePostRequest,
  SchedulePostRequest,
  AnalyticsOverview,
  GrowthMetrics,
  GrowthDataPoint,
  ReachMetrics,
  TopPost,
  PostDynamics,
  RealTimeMetrics,
  RealTimeDataPoint,
  Alert,
  AnalyticsPeriod,
  BatchAnalyticsResponse,
  MediaFile,
  MediaType,
  UploadResponse,
  UploadProgress,
  StorageFilesResponse,
  HealthCheckResponse,
  InitialDataResponse,
  RequestConfig,
  ApiClientConfig,
  AuthStrategy,
  ExportType,
  ExportFormat,
  ExportRequest,
  ExportResponse
} from '../types/api';

// Default export (main client instance)
export default apiClient;

/**
 * Migration Guide:
 *
 * BEFORE (JavaScript):
 * import { apiClient } from '../api/client.js';
 *
 * AFTER (TypeScript):
 * import { apiClient } from '@/api';
 * import type { User, Channel } from '@/api';
 *
 * Usage with types:
 * ```typescript
 * const user = await apiClient.get<User>('/auth/me');
 * const channels = await apiClient.get<Channel[]>('/channels');
 * const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
 * ```
 *
 * API methods:
 * - apiClient.get<T>(url, config)
 * - apiClient.post<T>(url, data, config)
 * - apiClient.put<T>(url, data, config)
 * - apiClient.patch<T>(url, data, config)
 * - apiClient.delete<T>(url, config)
 * - apiClient.uploadFile<T>(url, file, onProgress)
 * - apiClient.uploadFileDirect(file, channelId, onProgress)
 * - apiClient.getBatchAnalytics(channelId, period)
 * - apiClient.healthCheck()
 *
 * Configuration:
 * - apiClient.setAuthStrategy(AuthStrategies.JWT)
 * - apiClient.isDemoUser()
 * - apiClient.initialize()
 */
