import React, { useState, useCallback } from 'react';
import {
    Box,
    IconButton,
    Tooltip,
    Chip,
    Typography,
    useMediaQuery,
    useTheme
} from '@mui/material';
import {
    Search as SearchIcon
} from '@mui/icons-material';
import GlobalSearchDialog from '../../../../components/common/GlobalSearchDialog';

/**
 * GlobalSearchBar Component
 *
 * Handles global search functionality including:
 * - Desktop search bar with keyboard shortcut hint
 * - Mobile search button
 * - Search dialog management
 * - Recent search history integration
 * - Quick actions integration
 * - Keyboard shortcuts (Ctrl+K)
 */
const GlobalSearchBar = ({ className, ...props }) => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));

    // Local state for search dialog
    const [searchDialogOpen, setSearchDialogOpen] = useState(false);

    // Handle search dialog open/close
    const handleSearchOpen = useCallback(() => {
        setSearchDialogOpen(true);
    }, []);

    const handleSearchClose = useCallback(() => {
        setSearchDialogOpen(false);
    }, []);

    // Keyboard shortcut handler
    const handleKeyDown = useCallback((event) => {
        // Open search with Ctrl+K or Cmd+K
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            handleSearchOpen();
        }
    }, [handleSearchOpen]);

    // Set up keyboard event listener
    React.useEffect(() => {
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);

    return (
        <>
            {/* Desktop Search Bar */}
            {!isMobile && (
                <Tooltip title="Search (Ctrl+K)" placement="bottom">
                    <Box
                        onClick={handleSearchOpen}
                        className={className}
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                            px: 2,
                            py: 0.5,
                            border: '1px solid',
                            borderColor: 'divider',
                            borderRadius: 1,
                            cursor: 'pointer',
                            minWidth: 200,
                            backgroundColor: 'background.paper',
                            '&:hover': {
                                backgroundColor: 'action.hover',
                                borderColor: 'primary.main'
                            },
                            '&:focus-within': {
                                borderColor: 'primary.main',
                                boxShadow: `0 0 0 1px ${theme.palette.primary.main}25`
                            }
                        }}
                        {...props}
                    >
                        <SearchIcon fontSize="small" color="action" />
                        <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ flexGrow: 1, textAlign: 'left' }}
                        >
                            Search...
                        </Typography>
                        <Chip
                            label="⌘K"
                            size="small"
                            variant="outlined"
                            sx={{
                                height: 20,
                                fontSize: '0.7rem',
                                '& .MuiChip-label': {
                                    px: 0.5
                                }
                            }}
                        />
                    </Box>
                </Tooltip>
            )}

            {/* Mobile Search Button */}
            {isMobile && (
                <Tooltip title="Search" placement="bottom">
                    <IconButton
                        onClick={handleSearchOpen}
                        aria-label="Search"
                        className={className}
                        {...props}
                    >
                        <SearchIcon />
                    </IconButton>
                </Tooltip>
            )}

            {/* Global Search Dialog */}
            <GlobalSearchDialog
                open={searchDialogOpen}
                onClose={handleSearchClose}
            />
        </>
    );
};

export default GlobalSearchBar;
