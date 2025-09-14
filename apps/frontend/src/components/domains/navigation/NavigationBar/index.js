// Navigation components exports
export { default as NavigationBar } from './NavigationBar';
export { default as GlobalSearchBar } from './GlobalSearchBar';
export { default as ProfileMenu } from './ProfileMenu';
export { default as NotificationMenu } from './NotificationMenu';
export { default as SmartBreadcrumbs } from './SmartBreadcrumbs';
export { default as MobileNavigationDrawer } from './MobileNavigationDrawer';

// Utilities exports
export { NAVIGATION_CONFIG } from './navigationConfig';
export { 
    generateBreadcrumbs, 
    useBreadcrumbs, 
    shouldShowBreadcrumbs 
} from './breadcrumbUtils';

// Default export
export { default } from './NavigationBar';