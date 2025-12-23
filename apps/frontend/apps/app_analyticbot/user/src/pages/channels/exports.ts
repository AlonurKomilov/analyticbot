/**
 * Public API Exports
 *
 * Clean interface for importing channels feature components.
 * Use this for external imports to avoid coupling to internal structure.
 */

// Main pages
export { default as ChannelsManagementPage } from './index';
export { default as AddChannelPage } from './AddChannelPage';
export { default as ChannelDetailsPage } from './ChannelDetailsPage';

// Microservice components
export { ChannelAdminStatusIndicator } from './components/ChannelAdminStatusIndicator';
export { ChannelCard } from './components/ChannelCard';
export { ChannelStatisticsOverview } from './components/ChannelStatisticsOverview';
export { ChannelsGrid } from './components/ChannelsGrid';
export { CreateChannelDialog, EditChannelDialog, DeleteChannelDialog } from './components/ChannelDialogs';

// Hooks
export { useChannelAdminStatus } from './hooks/useChannelAdminStatus';
export type { ChannelAdminStatus } from './hooks/useChannelAdminStatus';

// Types
export type { ChannelStats, ChannelAdminStatus as ChannelAdminStatusType } from './components/ChannelCard';
export type { AggregateStats } from './components/ChannelStatisticsOverview';
export type { ChannelFormData } from './components/ChannelDialogs';
