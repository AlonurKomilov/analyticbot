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
import TableSearch from './TableSearch';
import TableExport from './TableExport';
import TableColumns from './TableColumns';
import TableDensity from './TableDensity';

interface Column {
    id: string;
    header?: string;
    [key: string]: any;
}

interface ColumnVisibility {
    [key: string]: boolean;
}

interface TableToolbarProps {
    // Content
    title?: string;
    subtitle?: string;

    // Search props
    enableSearch?: boolean;
    searchQuery?: string;
    setSearchQuery?: (query: string) => void;
    searchPlaceholder?: string;

    // Export props
    enableExport?: boolean;
    onExport?: (format: string) => void;
    exportFilename?: string;

    // Column management props
    enableColumnVisibility?: boolean;
    columns?: Column[];
    columnVisibility?: ColumnVisibility;
    setColumnVisibility?: (visibility: ColumnVisibility) => void;

    // Density props
    enableDensityToggle?: boolean;
    density?: string;
    setDensity?: (density: string) => void;

    // Refresh props
    enableRefresh?: boolean;
    onRefresh?: () => void;
    loading?: boolean;
}

/**
 * TableToolbar Component
 * Renders the main toolbar with title, subtitle, and action controls
 */
const TableToolbar: React.FC<TableToolbarProps> = ({
    // Content
    title,
    subtitle,

    // Search props
    enableSearch,
    searchQuery = '',
    setSearchQuery = () => {},
    searchPlaceholder,

    // Export props
    enableExport,
    onExport,
    exportFilename,

    // Column management props
    enableColumnVisibility,
    columns = [],
    columnVisibility = {},
    setColumnVisibility = () => {},

    // Density props
    enableDensityToggle,
    density = 'standard',
    setDensity = () => {},

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
