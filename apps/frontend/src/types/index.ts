/**
 * Type Definitions Index
 * Central export point for all TypeScript types
 */

// API Types
export type {
  ApiResponse,
  PaginatedResponse,
  ApiError,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  RefreshTokenRequest,
  CreateChannelRequest,
  UpdateChannelRequest,
  ChannelValidationResponse,
  CreatePostRequest,
  UpdatePostRequest,
  SchedulePostRequest,
  RealTimeMetrics,
  RealTimeDataPoint,
  BatchAnalyticsResponse,
  UploadResponse,
  StorageFilesResponse,
  HealthCheckResponse,
  InitialDataResponse,
  RequestConfig,
  ApiClientConfig,
  AuthStrategy,
  ExportType,
  ExportFormat,
  ExportRequest,
  ExportResponse,
} from './api';

// Domain Models from API
export type {
  User,
  UserRole,
  UserStatus,
  UserPreferences,
  Channel,
  ChannelMetrics,
  Post,
  PostStatus,
  BackendPostStatus,
  AnalyticsOverview,
  GrowthMetrics,
  GrowthDataPoint,
  ReachMetrics,
  TopPost,
  PostDynamics,
  MediaFile,
  MediaType,
  UploadProgress,
  Alert,
  AnalyticsPeriod,
} from './api';

// Functions from API types
export {
  mapBackendPostStatus,
} from './api';

// Payment & Subscription Types
export type {
  PaymentStatus,
  LegacyPaymentStatus,
  SubscriptionStatus,
  LegacySubscriptionStatus,
} from './payment';

// Functions from payment types
export {
  normalizePaymentStatus,
  normalizeSubscriptionStatus,
  isPaymentSuccessful,
  isPaymentTerminal,
  isSubscriptionActive,
} from './payment';

// Subscription & Tier Types
export type {
  UserTier,
  TierLimits,
  TierDisplayInfo,
} from './subscription';

// Functions from subscription types
export {
  getTierLimits,
  hasFeatureAccess,
  hasTierAccess,
  getTierUpgradeRecommendation,
  isValidTier,
  getTierByName,
  compareTiers,
  getAllTiers,
  getTierBenefits,
  TIER_DISPLAY_INFO,
} from './subscription';

// Utility Models
export type {
  PendingMedia,
  DataSource,
  ValidationResult,
  ChurnPrediction,
  NotificationType,
  Notification,
  LoadingState,
  SortOrder,
  Theme,
  Nullable,
  Optional,
  TimePeriod,
  ChartConfig,
  BestTimeRecommendation,
  ScheduledPost,
  EngagementMetrics,
} from './models';

// Component Props
export type {
  BaseComponentProps,
  LoadingProps,
  PaginationProps,
  HeaderProps,
  SidebarProps,
  PageContainerProps,
  DashboardPageProps,
  MetricsCardProps,
  AnalyticsDashboardProps,
  AddChannelProps,
  ChannelListProps,
  ChannelSelectorProps,
  ChannelCardProps,
  PostCreatorProps,
  ScheduledPostsListProps,
  PostCardProps,
  MediaUploaderProps,
  MediaPreviewProps,
  StorageFileBrowserProps,
  AnalyticsOverviewCardProps,
  GrowthChartProps,
  TopPostsTableProps,
  PostViewDynamicsChartProps,
  EngagementMetricsCardProps,
  BestTimeCardsProps,
  ChartVisualizationProps,
  ChartTypeSelectorProps,
  TimeRangeControlsProps,
  ButtonProps,
  InputProps,
  SelectProps,
  ModalProps,
  ToastProps,
  AlertBoxProps,
  LoadingSpinnerProps,
  EmptyStateProps,
  ErrorBoundaryProps,
  DataTableProps,
  StatsCardProps,
  ProgressBarProps,
  FormProps,
  FormFieldProps,
  SearchBarProps,
  FilterPanelProps,
  GlobalDataSourceSwitchProps,
  DataSourceBadgeProps,
  DiagnosticPanelProps,
  ContentOptimizerProps,
  SecurityMonitoringProps,
  ChurnPredictorProps,
} from './components';

// Store Types
export type {
  AuthState,
  ChannelState,
  PostState,
  AnalyticsState,
  MediaState,
  UIState,
  AppStores,
  AsyncAction,
  AsyncActionWithParam,
  StoreSelector,
  StoreCreator,
  PersistConfig,
  DevtoolsConfig,
  AsyncStateSlice,
  AsyncStateActions,
  UseAuthStore,
  UseChannelStore,
  UsePostStore,
  UseAnalyticsStore,
  UseMediaStore,
  UseUIStore,
  UseAuthSelector,
  UseChannelSelector,
  UsePostSelector,
  UseAnalyticsSelector,
  UseMediaSelector,
  UseUISelector,
} from './store';

// Note: All types are exported above via re-exports
// No need for convenience re-exports to avoid duplicates
