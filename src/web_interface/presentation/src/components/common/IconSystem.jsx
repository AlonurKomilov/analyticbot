import React from 'react';
import { Chip } from '@mui/material';
import {
    // Navigation Icons
    Dashboard as DashboardIcon,
    Analytics as AnalyticsIcon,
    Psychology as AIIcon,
    Edit as PostIcon,
    
    // Service Icons
    TrendingUp as TrendingIcon,
    Security as SecurityIcon,
    AutoAwesome as OptimizeIcon,
    QueryStats as PredictIcon,
    
    // Status Icons
    CheckCircle as OnlineIcon,
    Shield as SecureIcon,
    FlashOn as RealtimeIcon,
    
    // Action Icons
    Refresh as RefreshIcon,
    Download as DownloadIcon,
    Share as ShareIcon,
    Settings as SettingsIcon,
    Add as CreateIcon,
    
    // Data Icons
    Visibility as ViewsIcon,
    ThumbUp as LikeIcon,
    Comment as CommentIcon,
    Star as StarIcon,
    
    // Tech Icons
    Code as TechIcon,
    Storage as DatabaseIcon,
    Api as APIIcon
} from '@mui/icons-material';

// Professional Icon Mapping System
export const ICON_COMPONENTS = {
    // Navigation
    dashboard: DashboardIcon,
    analytics: AnalyticsIcon,
    ai: AIIcon,
    posts: PostIcon,
    
    // Services  
    trending: TrendingIcon,
    security: SecurityIcon,
    optimize: OptimizeIcon,
    predict: PredictIcon,
    
    // Status
    online: OnlineIcon,
    secure: SecureIcon,
    realtime: RealtimeIcon,
    
    // Actions
    refresh: RefreshIcon,
    download: DownloadIcon,
    share: ShareIcon,
    settings: SettingsIcon,
    create: CreateIcon,
    
    // Data
    views: ViewsIcon,
    likes: LikeIcon,
    comments: CommentIcon,
    star: StarIcon,
    
    // Tech
    tech: TechIcon,
    database: DatabaseIcon,
    api: APIIcon
};

// Standardized Icon Sizes
export const ICON_SIZES = {
    xs: 12,  // Inline text
    sm: 16,  // Forms, chips  
    md: 24,  // Buttons, cards
    lg: 32,  // Headers
    xl: 48,  // Empty states
    xxl: 64  // Hero sections
};

/**
 * Professional Icon Component
 * Replaces emoji usage with consistent Material-UI icons
 */
export const Icon = ({ 
    name, 
    size = 'md', 
    color = 'inherit', 
    className,
    ...props 
}) => {
    const IconComponent = ICON_COMPONENTS[name];
    
    if (!IconComponent) {
        console.warn(`Icon '${name}' not found in ICON_COMPONENTS`);
        return null;
    }
    
    const iconSize = typeof size === 'string' ? ICON_SIZES[size] : size;
    
    return (
        <IconComponent 
            sx={{ fontSize: iconSize, color }}
            className={className}
            {...props}
        />
    );
};

/**
 * Status Chip with Professional Icons
 */
export const StatusChip = ({ 
    status, 
    label, 
    color = 'primary', 
    size = 'medium',
    ...props 
}) => {
    const statusIcons = {
        online: 'online',
        analytics: 'analytics', 
        secure: 'secure',
        ai: 'ai',
        realtime: 'realtime',
        success: 'secure',
        info: 'analytics',
        warning: 'optimize',
        error: 'security'
    };
    
    return (
        <Chip
            icon={<Icon name={statusIcons[status]} size="sm" />}
            label={label}
            color={color}
            size={size}
            sx={{ fontSize: '0.9rem' }}
            {...props}
        />
    );
};

export default Icon;