import React from 'react';
import {
    TextField,
    IconButton
} from '@mui/material';
import {
    Search as SearchIcon,
    Clear as ClearIcon
} from '@mui/icons-material';

/**
 * TableSearch Component
 * Renders search input with clear functionality
 */
const TableSearch = ({
    searchQuery,
    setSearchQuery,
    searchPlaceholder = 'Search all columns...'
}) => {
    return (
        <TextField
            size="small"
            placeholder={searchPlaceholder}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
                startAdornment: <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />,
                endAdornment: searchQuery && (
                    <IconButton
                        size="small"
                        onClick={() => setSearchQuery('')}
                        aria-label="Clear search"
                    >
                        <ClearIcon fontSize="small" />
                    </IconButton>
                )
            }}
            sx={{ minWidth: 240 }}
        />
    );
};

export default TableSearch;
