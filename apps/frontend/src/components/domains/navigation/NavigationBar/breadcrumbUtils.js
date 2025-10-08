import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import {
    Dashboard as DashboardIcon,
    Analytics as AnalyticsIcon,
    Build as ServicesIcon,
    TableChart as TablesIcon,
    Person as PersonIcon,
    Settings as SettingsIcon,
    Help as HelpIcon
} from '@mui/icons-material';

// Route to breadcrumb mapping
const ROUTE_BREADCRUMB_MAP = {
    '/': { label: 'Dashboard', icon: DashboardIcon },
    '/analytics': { label: 'Analytics', icon: AnalyticsIcon },
    '/services': { label: 'AI Services', icon: ServicesIcon },
    '/services/content-optimizer': { label: 'Content Optimizer', icon: ServicesIcon },
    '/services/predictive-analytics': { label: 'Predictive Analytics', icon: ServicesIcon },
    '/services/churn-predictor': { label: 'Churn Predictor', icon: ServicesIcon },
    '/services/security-monitoring': { label: 'Security Monitoring', icon: ServicesIcon },
    '/tables': { label: 'Data Tables', icon: TablesIcon },
    '/profile': { label: 'Profile', icon: PersonIcon },
    '/settings': { label: 'Settings', icon: SettingsIcon },
    '/help': { label: 'Help & Support', icon: HelpIcon }
};

/**
 * Generate breadcrumbs from pathname
 * @param {string} pathname - Current route pathname
 * @returns {Array} Array of breadcrumb objects
 */
export const generateBreadcrumbs = (pathname) => {
    const segments = pathname.split('/').filter(Boolean);
    const breadcrumbs = [];

    // Always start with home
    breadcrumbs.push({
        label: 'Dashboard',
        path: '/',
        icon: DashboardIcon
    });

    // If we're on the home page, return just the home breadcrumb
    if (pathname === '/') {
        return breadcrumbs;
    }

    // Build breadcrumbs from path segments
    let currentPath = '';
    segments.forEach((segment, index) => {
        currentPath += `/${segment}`;

        // Look up breadcrumb info from route map
        const routeInfo = ROUTE_BREADCRUMB_MAP[currentPath];

        if (routeInfo) {
            breadcrumbs.push({
                label: routeInfo.label,
                path: currentPath,
                icon: routeInfo.icon
            });
        } else {
            // Fallback: use segment name with title case
            const label = segment
                .split('-')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');

            breadcrumbs.push({
                label,
                path: currentPath,
                icon: null
            });
        }
    });

    return breadcrumbs;
};

/**
 * Custom hook for breadcrumb generation
 * @returns {Array} Array of breadcrumb objects for current route
 */
export const useBreadcrumbs = () => {
    const location = useLocation();
    return useMemo(() => generateBreadcrumbs(location.pathname), [location.pathname]);
};

/**
 * Check if a route should be included in breadcrumbs
 * @param {string} path - Route path to check
 * @returns {boolean} Whether the route should show breadcrumbs
 */
export const shouldShowBreadcrumbs = (path) => {
    // Hide breadcrumbs on login, error pages, etc.
    const hiddenPaths = ['/login', '/signup', '/404', '/500'];
    return !hiddenPaths.includes(path);
};

export default { generateBreadcrumbs, useBreadcrumbs, shouldShowBreadcrumbs };
