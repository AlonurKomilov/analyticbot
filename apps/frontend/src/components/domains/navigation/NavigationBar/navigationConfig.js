import {
    Dashboard as DashboardIcon,
    Analytics as AnalyticsIcon,
    Build as ServicesIcon,
    TableChart as TablesIcon,
    Add as AddIcon,
    Download as DownloadIcon,
    Share as ShareIcon,
    Help as HelpIcon
} from '@mui/icons-material';

// Navigation configuration
export const NAVIGATION_CONFIG = {
    routes: [
        {
            id: 'dashboard',
            label: 'Dashboard',
            path: '/',
            icon: DashboardIcon,
            description: 'Main analytics dashboard',
            keywords: ['home', 'main', 'overview', 'dashboard'],
            category: 'Core'
        },
        {
            id: 'create',
            label: 'Create Post',
            path: '/create',
            icon: AddIcon,
            description: 'Create and schedule posts',
            keywords: ['create', 'post', 'compose', 'new'],
            category: 'Core'
        },
        {
            id: 'analytics',
            label: 'Analytics',
            path: '/analytics',
            icon: AnalyticsIcon,
            description: 'Detailed analytics and reports',
            keywords: ['analytics', 'reports', 'data', 'metrics'],
            category: 'Analytics'
        },
        {
            id: 'services',
            label: 'AI Services',
            path: '/services',
            icon: ServicesIcon,
            description: 'AI-powered automation services',
            keywords: ['ai', 'services', 'automation', 'ml'],
            category: 'AI',
            children: [
                {
                    id: 'content-optimizer',
                    label: 'Content Optimizer',
                    path: '/services/content-optimizer',
                    description: 'AI content enhancement',
                    keywords: ['content', 'optimize', 'ai', 'enhance']
                },
                {
                    id: 'predictive-analytics',
                    label: 'Predictive Analytics',
                    path: '/services/predictive-analytics',
                    description: 'Future predictions and trends',
                    keywords: ['predict', 'forecast', 'trends', 'future']
                },
                {
                    id: 'churn-predictor',
                    label: 'Churn Predictor',
                    path: '/services/churn-predictor',
                    description: 'Customer retention insights',
                    keywords: ['churn', 'retention', 'customers', 'risk']
                },
                {
                    id: 'security-monitoring',
                    label: 'Security Monitoring',
                    path: '/services/security-monitoring',
                    description: 'Security analysis and monitoring',
                    keywords: ['security', 'monitor', 'threats', 'analysis']
                }
            ]
        },
        {
            id: 'tables',
            label: 'Data Tables',
            path: '/tables',
            icon: TablesIcon,
            description: 'Enhanced data table showcase',
            keywords: ['tables', 'data', 'grid', 'export'],
            category: 'Tools'
        }
    ],
    quickActions: [
        {
            id: 'create-post',
            label: 'Create Post',
            icon: AddIcon,
            action: 'navigate',
            target: '/create',
            shortcut: 'Ctrl+N'
        },
        {
            id: 'export-data',
            label: 'Export Data',
            icon: DownloadIcon,
            action: 'function',
            shortcut: 'Ctrl+E'
        },
        {
            id: 'share-dashboard',
            label: 'Share Dashboard',
            icon: ShareIcon,
            action: 'function',
            shortcut: 'Ctrl+S'
        },
        {
            id: 'help-support',
            label: 'Help & Support',
            icon: HelpIcon,
            action: 'navigate',
            target: '/help'
        }
    ]
};

export default NAVIGATION_CONFIG;
