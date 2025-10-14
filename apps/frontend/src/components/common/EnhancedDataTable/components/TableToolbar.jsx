import React from 'react';
import {
    Toolbar,
    Typography,
    Box,
    IconButton,
    Tooltip
} from '@mui/material';
import {
    Refresh as RefreshIcon
} from '@mui/icons-material';
import TableSearch from './TableSearch.jsx';
import TableExport from './TableExport.jsx';
import TableColumns from './TableColumns.jsx';
import TableDensity from './TableDensity.jsx';

/**
 * TableToolbar Component
 * Renders the main toolbar with title, subtitle, and action controls
 */
const TableToolbar = ({
    // Content
    title,
    subtitle,

    // Search props
    enableSearch,
    searchQuery,
    setSearchQuery,
    searchPlaceholder,

    // Export props
    enableExport,
    onExport,
    exportFilename,

    // Column management props
    enableColumnVisibility,
    columns,
    columnVisibility,
    setColumnVisibility,

    // Density props
    enableDensityToggle,
    density,
    setDensity,

    // Refresh props
    enableRefresh,
    onRefresh,
    loading
}) => {
    return (
        <Toolbar sx={{ px: 2, py: 1 }}>
            <Box sx={{ flex: 1 }}>
                {title && (
                    <Typography variant="h6" component="h2">
                        {title}
                    </Typography>
                )}
                {subtitle && (
                    <Typography variant="body2" color="text.secondary">
                        {subtitle}
                    </Typography>
                )}
            </Box>

            {/* Action buttons */}
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                {/* Search */}
                {enableSearch && (
                    <TableSearch
                        searchQuery={searchQuery}
                        setSearchQuery={setSearchQuery}
                        searchPlaceholder={searchPlaceholder}
                    />
                )}

                {/* Export */}
                {enableExport && (
                    <TableExport
                        onExport={onExport}
                        exportFilename={exportFilename}
                    />
                )}

                {/* Column Visibility */}
                {enableColumnVisibility && (
                    <TableColumns
                        columns={columns}
                        columnVisibility={columnVisibility}
                        setColumnVisibility={setColumnVisibility}
                    />
                )}

                {/* Density Toggle */}
                {enableDensityToggle && (
                    <TableDensity
                        density={density}
                        setDensity={setDensity}
                    />
                )}

                {/* Refresh */}
                {enableRefresh && onRefresh && (
                    <Tooltip title="Refresh Data">
                        <span>
                            <IconButton
                                onClick={onRefresh}
                                disabled={loading}
                                aria-label="Refresh table data"
                            >
                                <RefreshIcon />
                            </IconButton>
                        </span>
                    </Tooltip>
                )}
            </Box>
        </Toolbar>
    );
};

export default TableToolbar;
