/**
 * GenericTableDemo Component
 *
 * Extracted from DataTablesShowcase - showcases the Generic Enhanced Data Table
 * with flexible configuration and custom column renderers
 */

import React, { useMemo } from 'react';
import { Box, Typography } from '@mui/material';
import {
    Analytics as AnalyticsIcon,
    People as PeopleIcon
} from '@mui/icons-material';
import { EnhancedDataTable } from '@components/common/EnhancedDataTable';

interface GenericTableRow {
    id: number;
    name: string;
    type: 'Report' | 'Export' | 'Metrics' | 'Backup';
    status: 'completed' | 'processing' | 'failed';
    date: Date;
    size: string;
}

interface CellProps {
    value: any;
}

const GenericTableDemo: React.FC = () => {
    // Mock generic table data
    const mockGenericData = useMemo<GenericTableRow[]>(() => [
        { id: 1, name: 'Analytics Report', type: 'Report', status: 'completed', date: new Date(), size: '2.5 MB' },
        { id: 2, name: 'User Export', type: 'Export', status: 'processing', date: new Date(Date.now() - 60000), size: '1.2 MB' },
        { id: 3, name: 'Performance Metrics', type: 'Metrics', status: 'failed', date: new Date(Date.now() - 120000), size: '850 KB' },
        { id: 4, name: 'Channel Overview', type: 'Report', status: 'completed', date: new Date(Date.now() - 300000), size: '3.1 MB' },
        { id: 5, name: 'Backup Archive', type: 'Backup', status: 'completed', date: new Date(Date.now() - 3600000), size: '15.7 MB' }
    ], []);

    // Column configuration with custom renderers
    const genericColumns = [
        {
            id: 'name',
            header: 'Name',
            accessor: (row: GenericTableRow) => row.name,
            minWidth: 200
        },
        {
            id: 'type',
            header: 'Type',
            accessor: (row: GenericTableRow) => row.type,
            align: 'center' as const,
            width: 120,
            Cell: ({ value }: CellProps) => (
                <Typography variant="body2" sx={{
                    px: 1,
                    py: 0.5,
                    borderRadius: 1,
                    bgcolor: value === 'Report' ? 'primary.light' :
                            value === 'Export' ? 'success.light' :
                            value === 'Metrics' ? 'info.light' : 'grey.200',
                    color: value === 'Report' ? 'primary.contrastText' :
                           value === 'Export' ? 'success.contrastText' :
                           value === 'Metrics' ? 'info.contrastText' : 'text.primary'
                }}>
                    {value}
                </Typography>
            )
        },
        {
            id: 'status',
            header: 'Status',
            accessor: (row: GenericTableRow) => row.status,
            align: 'center' as const,
            width: 120,
            Cell: ({ value }: CellProps) => (
                <Typography variant="body2" sx={{
                    px: 1,
                    py: 0.5,
                    borderRadius: 1,
                    bgcolor: value === 'completed' ? 'success.light' :
                            value === 'processing' ? 'warning.light' : 'error.light',
                    color: value === 'completed' ? 'success.contrastText' :
                           value === 'processing' ? 'warning.contrastText' : 'error.contrastText'
                }}>
                    {value}
                </Typography>
            )
        },
        {
            id: 'date',
            header: 'Date',
            accessor: (row: GenericTableRow) => row.date,
            Cell: ({ value }: CellProps) => value.toLocaleString(),
            width: 160
        },
        {
            id: 'size',
            header: 'File Size',
            accessor: (row: GenericTableRow) => row.size,
            align: 'right' as const,
            width: 100
        }
    ];

    return (
        <>
            <Box sx={{ mb: 2 }}>
                <Typography variant="h5" gutterBottom>
                    Generic Enhanced Data Table
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                    Flexible, reusable data table component that can be configured for any data structure.
                    Demonstrates the core enhanced table functionality with custom columns and renderers.
                </Typography>
            </Box>
            <EnhancedDataTable
                title="System Files & Reports"
                subtitle="File management system with advanced table features"
                data={mockGenericData}
                columns={genericColumns as any}

                enablePagination={true}
                defaultPageSize={10}
                enableSorting={true}
                defaultSortBy="date"
                defaultSortDirection="desc"

                enableSearch={true}
                enableFiltering={true}
                searchPlaceholder="Search files and reports..."

                enableColumnVisibility={true}
                enableSelection={true}
                enableBulkActions={true}

                bulkActions={[
                    {
                        label: 'Download Selected',
                        icon: <AnalyticsIcon />,
                        onClick: (ids: (string | number)[]) => console.log('Download:', ids),
                        color: 'primary' as const
                    },
                    {
                        label: 'Delete Selected',
                        icon: <PeopleIcon />,
                        onClick: (ids: (string | number)[]) => console.log('Delete:', ids),
                        color: 'error' as const
                    }
                ] as any}

                rowActions={[
                    {
                        icon: <AnalyticsIcon />,
                        label: 'View Details',
                        onClick: (row: GenericTableRow) => console.log('View:', row.id),
                        color: 'primary' as const
                    }
                ] as any}

                enableExport={true}
                exportFilename="system-files-report"

                enableRefresh={true}
                onRefresh={() => console.log('Refreshing data...')}

                tableAriaLabel="System files and reports data table"
            />
        </>
    );
};

export default GenericTableDemo;
