import React from 'react';
import { Chip, SxProps, Theme } from '@mui/material';
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

/**
 * IconSystem - Professional icon mapping with Material-UI icons
 *
 * @component
 * @example
 * ```tsx
 * <Icon name="dashboard" size="lg" color="primary" />
 * <StatusChip status="online" label="Active" color="success" />
 * ```
 */

export type IconName = keyof typeof ICON_COMPONENTS;
export type IconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl';
export type StatusType = 'online' | 'analytics' | 'secure' | 'ai' | 'realtime' | 'success' | 'info' | 'warning' | 'error';

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
export interface IconProps {
  /** Icon name from ICON_COMPONENTS */
  name: IconName;
  /** Icon size (preset or custom number) */
  size?: IconSize | number;
  /** Icon color */
  color?: string;
  /** Additional CSS class */
  className?: string;
  /** Additional props */
  [key: string]: any;
}

export const Icon: React.FC<IconProps> = ({
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
export interface StatusChipProps {
  /** Status type */
  status: StatusType;
  /** Chip label */
  label: string;
  /** Chip color */
  color?: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** Chip size */
  size?: 'small' | 'medium';
  /** Custom styles */
  sx?: SxProps<Theme>;
  /** Additional props */
  [key: string]: any;
}

export const StatusChip = React.forwardRef<HTMLDivElement, StatusChipProps>(({
    status,
    label,
    color = 'primary',
    size = 'medium',
    sx,
    ...props
}, ref) => {
    const statusIcons: Record<StatusType, IconName> = {
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

    const iconName = statusIcons[status as StatusType];

    return (
        <Chip
            ref={ref}
            icon={<Icon name={iconName} size="sm" />}
            label={label}
            color={color}
            size={size}
            sx={{ fontSize: '0.9rem', ...sx }}
            {...props}
        />
    );
});

StatusChip.displayName = 'StatusChip';

export default Icon;
