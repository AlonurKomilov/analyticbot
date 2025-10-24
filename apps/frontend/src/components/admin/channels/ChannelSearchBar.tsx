/**
 * ChannelSearchBar Component
 * 
 * Search and filter bar for channel management.
 * Follows the same pattern as UserSearchBar for consistency.
 * 
 * Features:
 * - Search input with icon
 * - Search button
 * - Refresh button
 * - Loading states
 */

import React from 'react';
import { Paper, TextField, Button, Box, InputAdornment } from '@mui/material';
import { Search as SearchIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { spacing, colors, radius } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface ChannelSearchBarProps {
    searchTerm: string;
    onSearchChange: (value: string) => void;
    onSearch: () => void;
    onRefresh: () => void;
    loading: boolean;
}

// =============================================================================
// Component
// =============================================================================

const ChannelSearchBar: React.FC<ChannelSearchBarProps> = ({
    searchTerm,
    onSearchChange,
    onSearch,
    onRefresh,
    loading,
}) => {
    const handleKeyPress = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            onSearch();
        }
    };

    return (
        <Paper
            sx={{
                p: spacing.md,
                mb: spacing.md,
                borderRadius: radius.lg,
                border: `1px solid ${colors.border.default}`,
            }}
            elevation={0}
        >
            <Box sx={{ display: 'flex', gap: spacing.sm, alignItems: 'center' }}>
                <TextField
                    fullWidth
                    size="small"
                    placeholder="Search channels by title, username, or ID..."
                    value={searchTerm}
                    onChange={(e) => onSearchChange(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={loading}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon color="action" />
                            </InputAdornment>
                        ),
                    }}
                    sx={{
                        '& .MuiOutlinedInput-root': {
                            borderRadius: radius.md,
                        },
                    }}
                />
                <Button
                    variant="contained"
                    onClick={onSearch}
                    disabled={loading}
                    startIcon={<SearchIcon />}
                    sx={{
                        minWidth: '120px',
                        borderRadius: radius.md,
                    }}
                >
                    Search
                </Button>
                <Button
                    variant="outlined"
                    onClick={onRefresh}
                    disabled={loading}
                    startIcon={<RefreshIcon />}
                    sx={{
                        minWidth: '120px',
                        borderRadius: radius.md,
                    }}
                >
                    Refresh
                </Button>
            </Box>
        </Paper>
    );
};

export default ChannelSearchBar;
