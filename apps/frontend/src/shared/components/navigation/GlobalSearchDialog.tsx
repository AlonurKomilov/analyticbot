import React, { useState, useMemo } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    TextField,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Typography,
    Box,
    Chip,
    InputAdornment,
    Divider
} from '@mui/material';
import {
    Search as SearchIcon,
    Dashboard as DashboardIcon,
    AutoFixHigh as ContentIcon,
    TrendingUp as PredictiveIcon,
    PersonRemove as ChurnIcon,
    Security as SecurityIcon,
    TableChart as TablesIcon,
    Analytics as AnalyticsIcon,
    AdminPanelSettings as AdminIcon,
    Settings as SettingsIcon,
    Help as HelpIcon,
    History as HistoryIcon,
    Bookmark as BookmarkIcon,
    Launch as LaunchIcon,
    SvgIconComponent
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useNavigation } from './NavigationProvider';

/**
 * Type definitions
 */
export interface SearchRoute {
    id: string;
    title: string;
    path: string;
    icon: SvgIconComponent;
    description: string;
    keywords: string[];
}

export interface RecentPage {
    title: string;
    path: string;
    timestamp?: number;
}

export interface SearchHistoryItem {
    query: string;
    timestamp?: number;
}

export interface Bookmark {
    title: string;
    path: string;
    timestamp?: number;
}

export interface FilteredResults {
    routes: SearchRoute[];
    recent: RecentPage[];
    bookmarks: Bookmark[];
    history: SearchHistoryItem[];
}

export interface GlobalSearchDialogProps {
    open: boolean;
    onClose: () => void;
}

interface ResultSectionProps {
    title: string;
    items: any[];
    icon: SvgIconComponent;
    type: 'routes' | 'recent' | 'bookmarks' | 'history';
}

/**
 * Global Search Dialog Component
 *
 * Provides comprehensive search across:
 * - Navigation routes
 * - Recent pages
 * - Bookmarks
 * - Quick actions
 */
const GlobalSearchDialog: React.FC<GlobalSearchDialogProps> = ({ open, onClose }) => {
    const navigate = useNavigate();
    const {
        recentPages,
        bookmarks,
        searchHistory,
        addSearchHistory,
        addBookmark
    } = useNavigation();

    const [query, setQuery] = useState<string>('');

    // Define all searchable routes and actions
    const allRoutes: SearchRoute[] = [
        {
            id: 'dashboard',
            title: 'Dashboard',
            path: '/',
            icon: DashboardIcon,
            description: 'Main dashboard with system overview',
            keywords: ['dashboard', 'home', 'main', 'overview']
        },
        {
            id: 'services',
            title: 'AI Services',
            path: '/services',
            icon: LaunchIcon,
            description: 'All AI services overview',
            keywords: ['services', 'ai', 'overview']
        },
        {
            id: 'content-optimizer',
            title: 'Content Optimizer',
            path: '/services/content-optimizer',
            icon: ContentIcon,
            description: 'AI-powered content enhancement',
            keywords: ['content', 'optimizer', 'ai', 'enhancement', 'improve']
        },
        {
            id: 'predictive-analytics',
            title: 'Predictive Analytics',
            path: '/services/predictive-analytics',
            icon: PredictiveIcon,
            description: 'Future performance predictions',
            keywords: ['predictive', 'analytics', 'predictions', 'trends', 'forecast']
        },
        {
            id: 'churn-predictor',
            title: 'Churn Predictor',
            path: '/services/churn-predictor',
            icon: ChurnIcon,
            description: 'Customer retention insights',
            keywords: ['churn', 'retention', 'customers', 'predict']
        },
        {
            id: 'security-monitoring',
            title: 'Security Monitoring',
            path: '/services/security-monitoring',
            icon: SecurityIcon,
            description: 'Real-time security analysis',
            keywords: ['security', 'monitoring', 'threats', 'analysis']
        },
        {
            id: 'tables',
            title: 'Data Tables',
            path: '/tables',
            icon: TablesIcon,
            description: 'Enhanced data tables showcase',
            keywords: ['tables', 'data', 'showcase', 'enhanced']
        },
        {
            id: 'analytics',
            title: 'Analytics Dashboard',
            path: '/analytics',
            icon: AnalyticsIcon,
            description: 'Advanced analytics and reporting',
            keywords: ['analytics', 'reporting', 'charts', 'metrics']
        },
        {
            id: 'admin',
            title: 'Super Admin',
            path: '/admin',
            icon: AdminIcon,
            description: 'Administrative controls',
            keywords: ['admin', 'administration', 'control', 'manage']
        },
        {
            id: 'settings',
            title: 'Settings',
            path: '/settings',
            icon: SettingsIcon,
            description: 'Configure preferences',
            keywords: ['settings', 'preferences', 'configure', 'options']
        },
        {
            id: 'help',
            title: 'Help & Support',
            path: '/help',
            icon: HelpIcon,
            description: 'Documentation and support',
            keywords: ['help', 'support', 'documentation', 'faq']
        }
    ];

    // Filter results based on query
    const filteredResults = useMemo((): FilteredResults => {
        if (!query.trim()) {
            return {
                routes: allRoutes.slice(0, 5),
                recent: recentPages.slice(0, 3),
                bookmarks: bookmarks.slice(0, 3),
                history: searchHistory.slice(0, 2)
            };
        }

        const lowerQuery = query.toLowerCase();

        const matchingRoutes = allRoutes.filter(route =>
            route.title.toLowerCase().includes(lowerQuery) ||
            route.description.toLowerCase().includes(lowerQuery) ||
            route.keywords.some(keyword => keyword.toLowerCase().includes(lowerQuery))
        );

        const matchingRecent = recentPages.filter(page =>
            page.title.toLowerCase().includes(lowerQuery) ||
            page.path.toLowerCase().includes(lowerQuery)
        );

        const matchingBookmarks = bookmarks.filter(bookmark =>
            bookmark.title.toLowerCase().includes(lowerQuery) ||
            bookmark.path.toLowerCase().includes(lowerQuery)
        );

        const matchingHistory = searchHistory.filter(item =>
            item.query.toLowerCase().includes(lowerQuery)
        );

        return {
            routes: matchingRoutes,
            recent: matchingRecent,
            bookmarks: matchingBookmarks,
            history: matchingHistory
        };
    }, [query, recentPages, bookmarks, searchHistory, allRoutes]);

    const handleSelect = (item: SearchRoute | RecentPage | Bookmark | SearchHistoryItem) => {
        if (addSearchHistory && query.trim()) {
            addSearchHistory(query);
        }

        if ('path' in item && item.path) {
            navigate(item.path);
        } else if ('query' in item && item.query) {
            setQuery(item.query);
            return; // Don't close dialog for history items
        }

        onClose();
        setQuery('');
    };

    const handleBookmarkToggle = (item: SearchRoute, event: React.MouseEvent) => {
        event.stopPropagation();
        addBookmark({
            title: item.title,
            path: item.path,
            timestamp: Date.now()
        });
    };

    const ResultSection: React.FC<ResultSectionProps> = ({ title, items, icon: SectionIcon, type }) => {
        if (items.length === 0) return null;

        return (
            <Box sx={{ mb: 2 }}>
                <Typography
                    variant="caption"
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        mb: 1,
                        color: 'text.secondary',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        fontSize: '0.75rem'
                    }}
                >
                    <SectionIcon fontSize="small" />
                    {title}
                </Typography>

                <List dense>
                    {items.map((item, index) => {
                        const ItemIcon = item.icon || (type === 'history' ? HistoryIcon : LaunchIcon);

                        return (
                            <ListItem key={`${type}-${index}`} disablePadding>
                                <ListItemButton
                                    onClick={() => handleSelect(item)}
                                    sx={{
                                        borderRadius: 1,
                                        '&:hover': {
                                            backgroundColor: 'action.hover'
                                        }
                                    }}
                                >
                                    <ListItemIcon sx={{ minWidth: 36 }}>
                                        <ItemIcon fontSize="small" />
                                    </ListItemIcon>

                                    <ListItemText
                                        primary={item.title || item.query}
                                        secondary={item.description || item.path}
                                        primaryTypographyProps={{
                                            fontSize: '0.9rem',
                                            fontWeight: 500
                                        }}
                                        secondaryTypographyProps={{
                                            fontSize: '0.8rem',
                                            color: 'text.secondary'
                                        }}
                                    />

                                    {type === 'routes' && (
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <BookmarkIcon
                                                fontSize="small"
                                                sx={{
                                                    cursor: 'pointer',
                                                    color: 'text.secondary',
                                                    '&:hover': { color: 'primary.main' }
                                                }}
                                                onClick={(e) => handleBookmarkToggle(item as SearchRoute, e)}
                                            />
                                        </Box>
                                    )}

                                    {item.timestamp && (
                                        <Chip
                                            label="Recent"
                                            size="small"
                                            variant="outlined"
                                            sx={{ fontSize: '0.7rem' }}
                                        />
                                    )}
                                </ListItemButton>
                            </ListItem>
                        );
                    })}
                </List>
            </Box>
        );
    };

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="md"
            fullWidth
            PaperProps={{
                sx: {
                    borderRadius: 2,
                    maxHeight: '80vh'
                }
            }}
        >
            <DialogTitle sx={{ pb: 1, fontWeight: 600 }}>
                Search Navigation
            </DialogTitle>

            <DialogContent>
                <TextField
                    fullWidth
                    placeholder="Search pages, services, or actions..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    variant="outlined"
                    sx={{ mb: 3 }}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon />
                            </InputAdornment>
                        ),
                    }}
                    autoFocus
                />

                <Box sx={{ maxHeight: '60vh', overflow: 'auto' }}>
                    <ResultSection
                        title="Pages & Services"
                        items={filteredResults.routes}
                        icon={LaunchIcon}
                        type="routes"
                    />

                    {filteredResults.recent.length > 0 && <Divider sx={{ my: 2 }} />}

                    <ResultSection
                        title="Recent Pages"
                        items={filteredResults.recent}
                        icon={HistoryIcon}
                        type="recent"
                    />

                    {filteredResults.bookmarks.length > 0 && <Divider sx={{ my: 2 }} />}

                    <ResultSection
                        title="Bookmarks"
                        items={filteredResults.bookmarks}
                        icon={BookmarkIcon}
                        type="bookmarks"
                    />

                    {filteredResults.history.length > 0 && <Divider sx={{ my: 2 }} />}

                    <ResultSection
                        title="Search History"
                        items={filteredResults.history}
                        icon={HistoryIcon}
                        type="history"
                    />

                    {query && Object.values(filteredResults).every(arr => arr.length === 0) && (
                        <Box sx={{ textAlign: 'center', py: 4 }}>
                            <Typography color="text.secondary">
                                No results found for "{query}"
                            </Typography>
                        </Box>
                    )}
                </Box>
            </DialogContent>
        </Dialog>
    );
};

export default GlobalSearchDialog;
