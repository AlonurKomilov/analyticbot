import React from 'react';
import {
    Breadcrumbs,
    Link,
    Typography,
    Box,
    useMediaQuery,
    useTheme,
    BreadcrumbsProps
} from '@mui/material';
import {
    NavigateNext as NavigateNextIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useBreadcrumbs, shouldShowBreadcrumbs } from './breadcrumbUtils';

interface SmartBreadcrumbsProps extends Omit<BreadcrumbsProps, 'separator' | 'maxItems'> {
    className?: string;
    maxItems?: number;
    showOnMobile?: boolean;
}

/**
 * SmartBreadcrumbs Component
 *
 * Provides intelligent breadcrumb navigation including:
 * - Automatic breadcrumb generation from routes
 * - Icon integration for each breadcrumb level
 * - Click navigation to parent routes
 * - Responsive behavior (desktop vs mobile)
 * - Semantic HTML structure for accessibility
 */
const SmartBreadcrumbs: React.FC<SmartBreadcrumbsProps> = ({
    className,
    maxItems = 3,
    showOnMobile = false,
    ...props
}) => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const navigate = useNavigate();
    const location = useLocation();
    const breadcrumbs = useBreadcrumbs();

    // Don't show breadcrumbs on mobile by default unless explicitly requested
    if (isMobile && !showOnMobile) {
        return null;
    }

    // Don't show breadcrumbs on certain pages
    if (!shouldShowBreadcrumbs(location.pathname)) {
        return null;
    }

    // Don't show breadcrumbs if only home breadcrumb exists
    if (breadcrumbs.length <= 1) {
        return null;
    }

    const handleBreadcrumbClick = (event: React.MouseEvent<HTMLAnchorElement>, path: string) => {
        event.preventDefault();
        navigate(path);
    };

    return (
        <Breadcrumbs
            separator={<NavigateNextIcon fontSize="small" />}
            maxItems={maxItems}
            className={className}
            sx={{
                flexGrow: 1,
                '& .MuiBreadcrumbs-ol': {
                    flexWrap: 'nowrap'
                },
                '& .MuiBreadcrumbs-li': {
                    display: 'flex',
                    alignItems: 'center'
                }
            }}
            {...props}
        >
            {breadcrumbs.map((crumb, index) => {
                const isLast = index === breadcrumbs.length - 1;
                const IconComponent = crumb.icon;

                return isLast ? (
                    // Current page - not clickable
                    <Box
                        key={crumb.path}
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.5,
                            color: 'text.primary'
                        }}
                    >
                        {IconComponent && (
                            <IconComponent
                                fontSize="small"
                                sx={{ color: 'primary.main' }}
                            />
                        )}
                        <Typography
                            variant="body2"
                            color="text.primary"
                            sx={{ fontWeight: 500 }}
                        >
                            {crumb.label}
                        </Typography>
                    </Box>
                ) : (
                    // Parent pages - clickable links
                    <Link
                        key={crumb.path}
                        href={crumb.path}
                        onClick={(e) => handleBreadcrumbClick(e, crumb.path)}
                        underline="hover"
                        color="text.secondary"
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.5,
                            cursor: 'pointer',
                            '&:hover': {
                                color: 'primary.main'
                            }
                        }}
                    >
                        {IconComponent && (
                            <IconComponent
                                fontSize="small"
                                sx={{ color: 'inherit' }}
                            />
                        )}
                        <Typography
                            variant="body2"
                            color="inherit"
                        >
                            {crumb.label}
                        </Typography>
                    </Link>
                );
            })}
        </Breadcrumbs>
    );
};

export default SmartBreadcrumbs;
