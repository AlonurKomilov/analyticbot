/**
 * 🎨 Category Configuration
 *
 * Defines visual and behavioral properties for each marketplace category
 */

import { CategoryConfig, MarketplaceCategory, ServiceSubcategory, ServiceSubcategoryConfig, ServiceUseCase, UseCaseConfig } from '../types';

export const CATEGORY_CONFIGS: Record<MarketplaceCategory, CategoryConfig> = {
    services: {
        key: 'services',
        label: 'Services',
        icon: 'Bolt',
        color: '#E91E63', // Pink
        description: 'Subscription services for moderation, MTProto, and analytics',
        pricingModel: 'subscription',
    },
    themes: {
        key: 'themes',
        label: 'Themes',
        icon: 'Palette',
        color: '#2196F3', // Blue
        description: 'Beautiful themes to customize your bot interface (Coming Soon)',
        pricingModel: 'one_time',
    },
    widgets: {
        key: 'widgets',
        label: 'Widgets',
        icon: 'Widgets',
        color: '#4CAF50', // Green
        description: 'Interactive widgets to enhance your bot features (Coming Soon)',
        pricingModel: 'one_time',
    },
    bundles: {
        key: 'bundles',
        label: 'Bundles',
        icon: 'CardGiftcard',
        color: '#FF9800', // Orange
        description: 'Value bundles with multiple items at discounted prices (Coming Soon)',
        pricingModel: 'one_time',
    },
};

/**
 * Get category config by key
 */
export const getCategoryConfig = (category: string): CategoryConfig => {
    return CATEGORY_CONFIGS[category as MarketplaceCategory] || CATEGORY_CONFIGS.services;
};

/**
 * Get all category keys
 */
export const getCategoryKeys = (): MarketplaceCategory[] => {
    return Object.keys(CATEGORY_CONFIGS) as MarketplaceCategory[];
};

/**
 * Map backend category names to frontend category keys
 */
export const mapBackendCategory = (backendCategory: string): MarketplaceCategory => {
    const mapping: Record<string, MarketplaceCategory> = {
        'themes': 'themes',
        'theme': 'themes',
        'bot_service': 'services',
        'bot_moderation': 'services',
        'mtproto_services': 'services',
        'mtproto_access': 'services',
        'services': 'services',
        'widgets': 'widgets',
        'widget': 'widgets',
        'bundles': 'bundles',
        'bundle': 'bundles',
    };
    return mapping[backendCategory.toLowerCase()] || 'services';
};

// ============================================
// Service Subcategory Configuration
// (Technical grouping for filtering)
// ============================================

export const SERVICE_SUBCATEGORY_CONFIGS: Record<ServiceSubcategory, ServiceSubcategoryConfig> = {
    all: {
        key: 'all',
        label: 'All Services',
        icon: 'Apps',
        color: '#757575',
        description: 'Browse all premium services',
        backendCategories: [],
    },
    bot: {
        key: 'bot',
        label: 'Bot Services',
        icon: 'SmartToy',
        color: '#E91E63',
        description: 'Bot moderation, engagement, and management',
        backendCategories: ['bot_service'],
    },
    mtproto: {
        key: 'mtproto',
        label: 'MTProto Tools',
        icon: 'Speed',
        color: '#2196F3',
        description: 'Data access, export, and automation',
        backendCategories: ['mtproto_services', 'mtproto_access'],
    },

    ai: {
        key: 'ai',
        label: 'AI Services',
        icon: 'Psychology',
        color: '#9C27B0',
        description: 'AI-powered features (Coming Soon)',
        backendCategories: ['ai_services'],
    },
};

/**
 * Get service subcategory config by key
 */
export const getServiceSubcategoryConfig = (subcategory: ServiceSubcategory): ServiceSubcategoryConfig => {
    return SERVICE_SUBCATEGORY_CONFIGS[subcategory] || SERVICE_SUBCATEGORY_CONFIGS.all;
};

/**
 * Map backend category to service subcategory
 */
export const mapBackendToServiceSubcategory = (backendCategory: string): ServiceSubcategory => {
    if (backendCategory.startsWith('bot_')) {
        return 'bot';
    }
    if (backendCategory.startsWith('mtproto_')) {
        return 'mtproto';
    }
    if (backendCategory.includes('ai_')) {
        return 'ai';
    }
    return 'all';
};

// ============================================
// Goal-Oriented Use Case Configuration
// (For discovery and "what's this good for?")
// ============================================

export const USE_CASE_CONFIGS: Record<ServiceUseCase, UseCaseConfig> = {
    grow_community: {
        key: 'grow_community',
        label: '🚀 Grow Your Community',
        icon: 'TrendingUp',
        color: '#4CAF50',
        description: 'Engage new members and track growth',
    },
    protect_chat: {
        key: 'protect_chat',
        label: '🛡️ Protect Your Chat',
        icon: 'Security',
        color: '#F44336',
        description: 'Security and moderation tools',
    },
    keep_clean: {
        key: 'keep_clean',
        label: '🧹 Keep Chats Clean',
        icon: 'CleaningServices',
        color: '#00BCD4',
        description: 'Automatic cleanup and maintenance',
    },
    understand_audience: {
        key: 'understand_audience',
        label: '📊 Understand Your Audience',
        icon: 'BarChart',
        color: '#FF9800',
        description: 'Analytics and insights',
    },
    power_tools: {
        key: 'power_tools',
        label: '⚡ Power User Tools',
        icon: 'Engineering',
        color: '#9C27B0',
        description: 'Advanced features for power users',
    },
};

/**
 * Get use case config by key
 */
export const getUseCaseConfig = (useCase: ServiceUseCase): UseCaseConfig => {
    return USE_CASE_CONFIGS[useCase];
};

/**
 * Map service_key to use cases (goal-oriented discovery)
 */
export const SERVICE_USE_CASE_MAP: Record<string, ServiceUseCase[]> = {
    // Grow Your Community
    'bot_welcome_messages': ['grow_community'],
    'bot_invite_tracking': ['grow_community', 'understand_audience'],
    
    // Protect Your Chat
    'bot_anti_spam': ['protect_chat'],
    'bot_banned_words': ['protect_chat'],
    'bot_warning_system': ['protect_chat'],
    
    // Keep Chats Clean
    'bot_auto_delete_joins': ['keep_clean'],
    
    // Understand Your Audience
    'mtproto_history_access': ['understand_audience', 'power_tools'],
    
    // Power User Tools
    'mtproto_bulk_export': ['power_tools'],
    'mtproto_auto_collect': ['power_tools'],
};

