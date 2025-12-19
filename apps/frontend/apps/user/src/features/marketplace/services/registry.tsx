/**
 * Service Registry
 * 
 * Central registry for all marketplace services.
 * Developers add their services here after creating the config component.
 * 
 * @module features/marketplace/services/registry
 */

import React from 'react';
import {
  Security as SecurityIcon,
  DeleteSweep as DeleteIcon,
  Block as BlockIcon,
  EmojiPeople as WaveIcon,
  PersonAdd as InviteIcon,
  Warning as WarningIcon,
  Analytics as AnalyticsIcon,
  Extension as ExtensionIcon,
  // MTProto icons
  History as HistoryIcon,
  Schedule as ScheduleIcon,
  CloudDownload as DownloadIcon,
  ImportExport as ExportIcon,
  // AI icons
  AutoFixHigh as OptimizeIcon,
  SentimentSatisfied as SentimentIcon,
  QuickreplyRounded as ReplyIcon,
  Shield as ModerationIcon,
} from '@mui/icons-material';

import type { ServiceMetadata, ServiceConfigProps } from '../types';

// Import all service config components
// TODO: Move configs to ./configs/ directory during full migration
import { AntiSpamConfig } from '@/pages/services/configs/AntiSpamConfig';
import { AutoDeleteConfig } from '@/pages/services/configs/AutoDeleteConfig';
import { BannedWordsConfig } from '@/pages/services/configs/BannedWordsConfig';
import { WelcomeMessagesConfig } from '@/pages/services/configs/WelcomeMessagesConfig';
import { InviteTrackingConfig } from '@/pages/services/configs/InviteTrackingConfig';
import { WarningSystemConfig } from '@/pages/services/configs/WarningSystemConfig';
import { AdvancedAnalyticsConfig } from '@/pages/services/configs/AdvancedAnalyticsConfig';

// MTProto service config components
import { 
  HistoryAccessConfig,
  AutoCollectConfig,
  MediaDownloadConfig,
  BulkExportConfig,
} from '@/pages/services/configs/mtproto';

// AI service config components
import {
  ContentOptimizerConfig,
  SentimentAnalyzerConfig,
  SmartRepliesConfig,
  ContentModerationConfig,
} from '@/pages/services/configs/ai';

// =============================================================================
// SERVICE REGISTRY
// =============================================================================

/**
 * Service registration entry
 */
export interface ServiceRegistryEntry {
  metadata: ServiceMetadata;
  configComponent: React.ComponentType<ServiceConfigProps>;
  icon: React.ReactNode;
}

/**
 * Central registry of all marketplace services
 * 
 * To add a new service:
 * 1. Create config component in pages/services/configs/
 * 2. Import it above
 * 3. Add entry to this registry
 */
export const SERVICE_REGISTRY: Record<string, ServiceRegistryEntry> = {
  // =========================================================================
  // BOT SERVICES
  // =========================================================================
  
  bot_anti_spam: {
    metadata: {
      service_key: 'bot_anti_spam',
      name: 'Anti-Spam Protection',
      description: 'Protect your chat from spam messages, malicious links, and bot attacks with advanced AI-powered detection.',
      features: [
        'Real-time spam detection',
        'Malicious link blocking',
        'Bot behavior detection',
        'Flood prevention',
        'Customizable sensitivity levels',
        'Automatic user warnings',
      ],
      icon: 'Security',
      color: '#667eea',
      per_chat_config: true,
      has_quotas: false,
    },
    configComponent: AntiSpamConfig,
    icon: <SecurityIcon fontSize="small" />,
  },

  bot_auto_delete_joins: {
    metadata: {
      service_key: 'bot_auto_delete_joins',
      name: 'Auto-Delete Join/Leave',
      description: 'Keep your chat clean by automatically removing "User joined" and "User left" system messages.',
      features: [
        'Auto-delete join messages',
        'Auto-delete leave messages',
        'Configurable delay before deletion',
        'Per-chat settings',
        'Bulk cleanup of old messages',
      ],
      icon: 'DeleteSweep',
      color: '#10b981',
      per_chat_config: true,
      has_quotas: false,
    },
    configComponent: AutoDeleteConfig,
    icon: <DeleteIcon fontSize="small" />,
  },

  bot_banned_words: {
    metadata: {
      service_key: 'bot_banned_words',
      name: 'Banned Words Filter',
      description: 'Create custom lists of banned words and phrases. Automatically moderate messages containing forbidden content.',
      features: [
        'Custom word lists',
        'Regex pattern support',
        'Auto-delete matching messages',
        'Warning system integration',
        'Case-insensitive matching',
        'Multi-language support',
      ],
      icon: 'Block',
      color: '#ef4444',
      per_chat_config: true,
      has_quotas: false,
    },
    configComponent: BannedWordsConfig,
    icon: <BlockIcon fontSize="small" />,
  },

  bot_welcome_messages: {
    metadata: {
      service_key: 'bot_welcome_messages',
      name: 'Welcome Messages',
      description: 'Greet new members with customizable welcome messages including text, images, and buttons.',
      features: [
        'Custom welcome messages',
        'Media attachments support',
        'Inline buttons/keyboards',
        'Variable substitution (username, chat name)',
        'Per-chat customization',
        'Schedule-based messages',
      ],
      icon: 'EmojiPeople',
      color: '#8b5cf6',
      per_chat_config: true,
      has_quotas: false,
    },
    configComponent: WelcomeMessagesConfig,
    icon: <WaveIcon fontSize="small" />,
  },

  bot_invite_tracking: {
    metadata: {
      service_key: 'bot_invite_tracking',
      name: 'Invite Link Tracking',
      description: 'Track who invited each member to your chat with unique invite links and detailed statistics.',
      features: [
        'Unique invite links per user',
        'Member source tracking',
        'Invite statistics dashboard',
        'Leaderboards',
        'CSV export',
        'Referral rewards integration',
      ],
      icon: 'PersonAdd',
      color: '#3b82f6',
      per_chat_config: true,
      has_quotas: false,
    },
    configComponent: InviteTrackingConfig,
    icon: <InviteIcon fontSize="small" />,
  },

  bot_warning_system: {
    metadata: {
      service_key: 'bot_warning_system',
      name: 'Warning System',
      description: 'Issue warnings to members who violate rules with automatic escalation and ban system.',
      features: [
        'Manual warnings',
        'Auto-warnings on violations',
        'Configurable escalation rules',
        'Warning history tracking',
        'Automatic bans after threshold',
        'Custom warning messages',
      ],
      icon: 'Warning',
      color: '#f59e0b',
      per_chat_config: true,
      has_quotas: false,
    },
    configComponent: WarningSystemConfig,
    icon: <WarningIcon fontSize="small" />,
  },

  bot_analytics_advanced: {
    metadata: {
      service_key: 'bot_analytics_advanced',
      name: 'Advanced Analytics',
      description: 'Comprehensive analytics dashboard for your Telegram bot with engagement metrics and growth tracking.',
      features: [
        'User engagement metrics',
        'Command usage analytics',
        'Growth tracking over time',
        'Retention analysis',
        'Custom dashboards',
        'PDF report generation',
      ],
      icon: 'Analytics',
      color: '#14b8a6',
      per_chat_config: true,
      has_quotas: true,
    },
    configComponent: AdvancedAnalyticsConfig,
    icon: <AnalyticsIcon fontSize="small" />,
  },

  // =========================================================================
  // MTPROTO SERVICES
  // =========================================================================
  
  mtproto_history_access: {
    metadata: {
      service_key: 'mtproto_history_access',
      name: 'MTProto History Access',
      description: 'Fetch and analyze full message history from your channels via MTProto API with configurable limits.',
      features: [
        'Full message history access',
        'Configurable date ranges',
        'Media metadata extraction',
        'Reaction data collection',
        'Reply thread tracking',
        'Export to JSON/CSV',
      ],
      icon: 'History',
      color: '#2196F3',
      per_chat_config: false,
      has_quotas: true,
    },
    configComponent: HistoryAccessConfig,
    icon: <HistoryIcon fontSize="small" />,
  },

  mtproto_auto_collect: {
    metadata: {
      service_key: 'mtproto_auto_collect',
      name: 'MTProto Auto-Collect',
      description: 'Automatically collect messages from your channels on a schedule with smart prioritization.',
      features: [
        'Scheduled collection runs',
        'Activity-based prioritization',
        'Worker status monitoring',
        'Error handling & retries',
        'Per-channel quotas',
        'Collection history',
      ],
      icon: 'Schedule',
      color: '#FF9800',
      per_chat_config: false,
      has_quotas: true,
    },
    configComponent: AutoCollectConfig,
    icon: <ScheduleIcon fontSize="small" />,
  },

  mtproto_media_download: {
    metadata: {
      service_key: 'mtproto_media_download',
      name: 'MTProto Media Download',
      description: 'Download photos, videos, and documents from your channels in bulk with quality controls.',
      features: [
        'Bulk media downloads',
        'Photo/video/document support',
        'Quality & size controls',
        'Smart file organization',
        'Duplicate detection',
        'Resume interrupted downloads',
      ],
      icon: 'CloudDownload',
      color: '#4CAF50',
      per_chat_config: false,
      has_quotas: true,
    },
    configComponent: MediaDownloadConfig,
    icon: <DownloadIcon fontSize="small" />,
  },

  mtproto_bulk_export: {
    metadata: {
      service_key: 'mtproto_bulk_export',
      name: 'MTProto Bulk Export',
      description: 'Export all your channel data in bulk with multiple format options and delivery methods.',
      features: [
        'JSON/CSV/HTML export',
        'Messages & media export',
        'Member list export',
        'Statistics inclusion',
        'Compressed archives',
        'Email notifications',
      ],
      icon: 'ImportExport',
      color: '#9C27B0',
      per_chat_config: false,
      has_quotas: true,
    },
    configComponent: BulkExportConfig,
    icon: <ExportIcon fontSize="small" />,
  },

  // =========================================================================
  // AI SERVICES
  // =========================================================================
  
  ai_content_optimizer: {
    metadata: {
      service_key: 'ai_content_optimizer',
      name: 'AI Content Optimizer',
      description: 'Get AI-powered suggestions to improve your posts for better engagement, reach, and clarity.',
      features: [
        'Engagement optimization',
        'Tone & style suggestions',
        'Hashtag recommendations',
        'Emoji suggestions',
        'Call-to-action tips',
        'Length optimization',
      ],
      icon: 'AutoFixHigh',
      color: '#6366F1',
      per_chat_config: false,
      has_quotas: true,
    },
    configComponent: ContentOptimizerConfig,
    icon: <OptimizeIcon fontSize="small" />,
  },

  ai_sentiment_analyzer: {
    metadata: {
      service_key: 'ai_sentiment_analyzer',
      name: 'AI Sentiment Analyzer',
      description: 'Understand your audience mood and reactions with AI-powered sentiment analysis.',
      features: [
        'Real-time sentiment tracking',
        'Comment & reaction analysis',
        'Trend detection',
        'Alert on sentiment spikes',
        'Multi-language support',
        'Detailed reports',
      ],
      icon: 'SentimentSatisfied',
      color: '#EC4899',
      per_chat_config: false,
      has_quotas: true,
    },
    configComponent: SentimentAnalyzerConfig,
    icon: <SentimentIcon fontSize="small" />,
  },

  ai_smart_replies: {
    metadata: {
      service_key: 'ai_smart_replies',
      name: 'AI Smart Replies',
      description: 'Generate intelligent, context-aware reply suggestions powered by AI.',
      features: [
        'Context-aware suggestions',
        'Tone customization',
        'Auto-reply triggers',
        'Response timing control',
        'Signature support',
        'Learning from history',
      ],
      icon: 'QuickreplyRounded',
      color: '#14B8A6',
      per_chat_config: false,
      has_quotas: true,
    },
    configComponent: SmartRepliesConfig,
    icon: <ReplyIcon fontSize="small" />,
  },

  ai_content_moderation: {
    metadata: {
      service_key: 'ai_content_moderation',
      name: 'AI Content Moderation',
      description: 'Automatically detect and moderate harmful content using advanced AI.',
      features: [
        'Spam detection',
        'Hate speech filtering',
        'Adult content detection',
        'Violence detection',
        'Auto-moderation actions',
        'Appeal workflow',
      ],
      icon: 'Shield',
      color: '#EF4444',
      per_chat_config: false,
      has_quotas: true,
    },
    configComponent: ContentModerationConfig,
    icon: <ModerationIcon fontSize="small" />,
  },
};

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Get service entry by key
 */
export function getServiceEntry(serviceKey: string): ServiceRegistryEntry | undefined {
  return SERVICE_REGISTRY[serviceKey];
}

/**
 * Get service config component by key
 */
export function getServiceConfigComponent(
  serviceKey: string
): React.ComponentType<ServiceConfigProps> | undefined {
  return SERVICE_REGISTRY[serviceKey]?.configComponent;
}

/**
 * Get service metadata by key
 */
export function getServiceMetadata(serviceKey: string): ServiceMetadata | undefined {
  return SERVICE_REGISTRY[serviceKey]?.metadata;
}

/**
 * Get service icon by key
 */
export function getServiceIcon(serviceKey: string): React.ReactNode {
  return SERVICE_REGISTRY[serviceKey]?.icon || <ExtensionIcon fontSize="small" />;
}

/**
 * Get all registered service keys
 */
export function getAllServiceKeys(): string[] {
  return Object.keys(SERVICE_REGISTRY);
}

/**
 * Get services by category prefix
 */
export function getServicesByCategory(prefix: 'bot' | 'mtproto' | 'ai'): ServiceRegistryEntry[] {
  return Object.entries(SERVICE_REGISTRY)
    .filter(([key]) => key.startsWith(`${prefix}_`))
    .map(([, entry]) => entry);
}

/**
 * Check if a service is registered
 */
export function isServiceRegistered(serviceKey: string): boolean {
  return serviceKey in SERVICE_REGISTRY;
}

// =============================================================================
// CONFIG MAP (for ServiceConfigPage backward compatibility)
// =============================================================================

/**
 * Map of service keys to config components
 * @deprecated Use SERVICE_REGISTRY instead
 */
export const SERVICE_CONFIG_MAP: Record<string, React.ComponentType<ServiceConfigProps>> = 
  Object.fromEntries(
    Object.entries(SERVICE_REGISTRY).map(([key, entry]) => [key, entry.configComponent])
  );

/**
 * Map of service keys to icons
 * @deprecated Use getServiceIcon() instead
 */
export const SERVICE_ICON_MAP: Record<string, React.ReactNode> = 
  Object.fromEntries(
    Object.entries(SERVICE_REGISTRY).map(([key, entry]) => [key, entry.icon])
  );

/**
 * Map of service keys to details
 * @deprecated Use getServiceMetadata() instead
 */
export const SERVICE_DETAILS: Record<string, { features: string[]; description: string }> = 
  Object.fromEntries(
    Object.entries(SERVICE_REGISTRY).map(([key, entry]) => [
      key,
      {
        features: entry.metadata.features,
        description: entry.metadata.description,
      },
    ])
  );

export default SERVICE_REGISTRY;
