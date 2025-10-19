/**
 * Component Props Type Definitions
 * Type-safe props for all React components
 */

import type { ReactNode, CSSProperties } from 'react';
import type {
  User,
  Channel,
  Post,
  ScheduledPost,
  AnalyticsOverview,
  GrowthMetrics,
  TopPost,
  PostDynamics,
  MediaFile,
  PendingMedia,
  BestTimeRecommendation,
  EngagementMetrics,
  ChartConfig,
  DataSource,
  TimePeriod,
  Alert,
  NotificationType,
} from './models';

// ============================================================================
// Common Component Props
// ============================================================================

export interface BaseComponentProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

export interface LoadingProps {
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

export interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
}

// ============================================================================
// Layout Components
// ============================================================================

export interface HeaderProps extends BaseComponentProps {
  user?: User | null;
  onLogout?: () => void;
  showNotifications?: boolean;
  notificationCount?: number;
}

export interface SidebarProps extends BaseComponentProps {
  collapsed?: boolean;
  onToggle?: () => void;
  activeRoute?: string;
}

export interface PageContainerProps extends BaseComponentProps {
  title?: string;
  subtitle?: string;
  breadcrumbs?: Array<{ label: string; path?: string }>;
  actions?: ReactNode;
  loading?: boolean;
}

// ============================================================================
// Dashboard Components
// ============================================================================

export interface DashboardPageProps extends BaseComponentProps {
  channels?: Channel[];
  selectedChannel?: Channel | null;
  onChannelSelect?: (channel: Channel) => void;
}

export interface MetricsCardProps extends BaseComponentProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: ReactNode;
  loading?: boolean;
  trend?: 'up' | 'down' | 'stable';
  color?: string;
  onClick?: () => void;
}

export interface AnalyticsDashboardProps extends BaseComponentProps {
  channelId: string;
  period?: TimePeriod;
  dataSource?: DataSource;
  onPeriodChange?: (period: TimePeriod) => void;
  onDataSourceChange?: (source: DataSource) => void;
}

// ============================================================================
// Channel Components
// ============================================================================

export interface AddChannelProps extends BaseComponentProps {
  onAdd?: (channel: Channel) => void;
  loading?: boolean;
  disabled?: boolean;
}

export interface ChannelListProps extends BaseComponentProps {
  channels: Channel[];
  selectedChannel?: Channel | null;
  onSelect?: (channel: Channel) => void;
  onDelete?: (channelId: string) => void;
  onEdit?: (channel: Channel) => void;
  loading?: boolean;
}

export interface ChannelSelectorProps extends BaseComponentProps {
  channels: Channel[];
  selectedChannelId?: string | null;
  onChange: (channelId: string) => void;
  placeholder?: string;
  disabled?: boolean;
  allowClear?: boolean;
}

export interface ChannelCardProps extends BaseComponentProps {
  channel: Channel;
  selected?: boolean;
  onClick?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  showActions?: boolean;
}

// ============================================================================
// Post Components
// ============================================================================

export interface PostCreatorProps extends BaseComponentProps {
  channelId?: string;
  onSubmit?: (post: Partial<Post>) => Promise<void>;
  onCancel?: () => void;
  initialData?: Partial<Post>;
  loading?: boolean;
}

export interface ScheduledPostsListProps extends BaseComponentProps {
  posts: ScheduledPost[];
  onDelete?: (postId: string) => void;
  onEdit?: (post: ScheduledPost) => void;
  onPublishNow?: (postId: string) => void;
  loading?: boolean;
  emptyMessage?: string;
}

export interface PostCardProps extends BaseComponentProps {
  post: Post | ScheduledPost;
  showActions?: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
  onPublish?: () => void;
  compact?: boolean;
}

// ============================================================================
// Media Components
// ============================================================================

export interface MediaUploaderProps extends BaseComponentProps {
  onUpload: (files: File[]) => Promise<void>;
  onRemove?: (fileId: string) => void;
  accept?: string;
  maxSize?: number;
  maxFiles?: number;
  multiple?: boolean;
  disabled?: boolean;
  currentFiles?: PendingMedia[];
  uploadProgress?: { [key: string]: number };
}

export interface MediaPreviewProps extends BaseComponentProps {
  file: MediaFile | PendingMedia;
  onRemove?: () => void;
  onDownload?: () => void;
  showActions?: boolean;
  size?: 'small' | 'medium' | 'large';
}

export interface StorageFileBrowserProps extends BaseComponentProps {
  files: MediaFile[];
  onSelect?: (file: MediaFile) => void;
  onDelete?: (fileId: string) => void;
  selectedFiles?: string[];
  multiSelect?: boolean;
  loading?: boolean;
}

// ============================================================================
// Analytics Components
// ============================================================================

export interface AnalyticsOverviewCardProps extends BaseComponentProps {
  data: AnalyticsOverview;
  loading?: boolean;
  onRefresh?: () => void;
}

export interface GrowthChartProps extends BaseComponentProps {
  data: GrowthMetrics;
  loading?: boolean;
  height?: number;
  showLegend?: boolean;
}

export interface TopPostsTableProps extends BaseComponentProps {
  posts: TopPost[];
  loading?: boolean;
  onPostClick?: (post: TopPost) => void;
  pageSize?: number;
}

export interface PostViewDynamicsChartProps extends BaseComponentProps {
  data: PostDynamics;
  loading?: boolean;
  height?: number;
}

export interface EngagementMetricsCardProps extends BaseComponentProps {
  metrics: EngagementMetrics;
  loading?: boolean;
  period?: string;
}

export interface BestTimeCardsProps extends BaseComponentProps {
  recommendations: BestTimeRecommendation[];
  loading?: boolean;
  onSchedule?: (recommendation: BestTimeRecommendation) => void;
}

// ============================================================================
// Chart Components
// ============================================================================

export interface ChartVisualizationProps extends BaseComponentProps {
  config: ChartConfig;
  loading?: boolean;
  height?: number;
  responsive?: boolean;
  onDataPointClick?: (point: any) => void;
}

export interface ChartTypeSelectorProps extends BaseComponentProps {
  selectedType: string;
  types: Array<{ value: string; label: string; icon?: ReactNode }>;
  onChange: (type: string) => void;
}

export interface TimeRangeControlsProps extends BaseComponentProps {
  period: TimePeriod;
  onChange: (period: TimePeriod) => void;
  disabled?: boolean;
  customRange?: { from: Date; to: Date };
  onCustomRangeChange?: (range: { from: Date; to: Date }) => void;
}

// ============================================================================
// UI Components
// ============================================================================

export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'text' | 'danger';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export interface InputProps extends BaseComponentProps {
  type?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  label?: string;
  required?: boolean;
  maxLength?: number;
  autoFocus?: boolean;
}

export interface SelectProps<T = any> extends BaseComponentProps {
  value: T;
  options: Array<{ value: T; label: string; disabled?: boolean }>;
  onChange: (value: T) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  label?: string;
  searchable?: boolean;
  clearable?: boolean;
}

export interface ModalProps extends BaseComponentProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  size?: 'small' | 'medium' | 'large' | 'fullscreen';
  closeOnBackdrop?: boolean;
  showCloseButton?: boolean;
  footer?: ReactNode;
}

export interface ToastProps extends BaseComponentProps {
  message: string;
  type?: NotificationType;
  duration?: number;
  onClose?: () => void;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface AlertBoxProps extends BaseComponentProps {
  alert: Alert;
  onDismiss?: () => void;
  onResolve?: () => void;
  compact?: boolean;
}

export interface LoadingSpinnerProps extends BaseComponentProps {
  size?: 'small' | 'medium' | 'large';
  text?: string;
  centered?: boolean;
}

export interface EmptyStateProps extends BaseComponentProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface ErrorBoundaryProps extends BaseComponentProps {
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: any) => void;
}

// ============================================================================
// Data Display Components
// ============================================================================

export interface DataTableProps<T = any> extends BaseComponentProps {
  data: T[];
  columns: Array<{
    key: string;
    label: string;
    sortable?: boolean;
    render?: (value: any, row: T) => ReactNode;
    width?: string | number;
  }>;
  loading?: boolean;
  onRowClick?: (row: T) => void;
  selectedRows?: string[];
  onSelectionChange?: (selectedIds: string[]) => void;
  pagination?: PaginationProps;
  emptyMessage?: string;
}

export interface StatsCardProps extends BaseComponentProps {
  title: string;
  stats: Array<{
    label: string;
    value: string | number;
    change?: number;
    icon?: ReactNode;
  }>;
  loading?: boolean;
}

export interface ProgressBarProps extends BaseComponentProps {
  value: number;
  max?: number;
  label?: string;
  showPercentage?: boolean;
  color?: string;
  size?: 'small' | 'medium' | 'large';
}

// ============================================================================
// Form Components
// ============================================================================

export interface FormProps extends BaseComponentProps {
  onSubmit: (data: any) => void | Promise<void>;
  initialValues?: any;
  validationSchema?: any;
  loading?: boolean;
  disabled?: boolean;
}

export interface FormFieldProps extends BaseComponentProps {
  name: string;
  label?: string;
  required?: boolean;
  error?: string;
  helpText?: string;
}

// ============================================================================
// Filter & Search Components
// ============================================================================

export interface SearchBarProps extends BaseComponentProps {
  value: string;
  onChange: (value: string) => void;
  onSearch?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  autoFocus?: boolean;
  clearable?: boolean;
}

export interface FilterPanelProps extends BaseComponentProps {
  filters: Array<{
    name: string;
    label: string;
    type: 'select' | 'range' | 'date' | 'checkbox';
    options?: any[];
    value?: any;
  }>;
  onFilterChange: (filterName: string, value: any) => void;
  onReset?: () => void;
}

// ============================================================================
// Global Components
// ============================================================================

export interface GlobalDataSourceSwitchProps extends BaseComponentProps {
  dataSource: DataSource;
  onChange: (source: DataSource) => void;
  disabled?: boolean;
}

export interface DataSourceBadgeProps extends BaseComponentProps {
  dataSource: DataSource;
  showLabel?: boolean;
}

export interface DiagnosticPanelProps extends BaseComponentProps {
  open: boolean;
  onClose: () => void;
}

// ============================================================================
// AI Service Components
// ============================================================================

export interface ContentOptimizerProps extends BaseComponentProps {
  content: string;
  onOptimize?: (optimizedContent: string) => void;
  loading?: boolean;
}

export interface SecurityMonitoringProps extends BaseComponentProps {
  channelId: string;
  onThreatDetected?: (threat: any) => void;
  autoRefresh?: boolean;
}

export interface ChurnPredictorProps extends BaseComponentProps {
  channelId: string;
  onPrediction?: (prediction: any) => void;
}
