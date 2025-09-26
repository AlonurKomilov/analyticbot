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
import { EnhancedDataTable } from '../../../../components/common/EnhancedDataTable';

const GenericTableDemo = () => {
    // Mock generic table data
    const mockGenericData = useMemo(() => [
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
            accessor: (row) => row.name,
            minWidth: 200
        },
        {
            id: 'type',
            header: 'Type',
            accessor: (row) => row.type,
            align: 'center',
            width: 120,
            Cell: ({ value }) => (
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
            accessor: (row) => row.status,
            align: 'center',
            width: 120,
            Cell: ({ value }) => (
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
            accessor: (row) => row.date,
            Cell: ({ value }) => value.toLocaleString(),
            width: 160
        },
        {
            id: 'size',
            header: 'File Size',
            accessor: (row) => row.size,
            align: 'right',
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
                columns={genericColumns}
                
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
                        onClick: (ids) => console.log('Download:', ids),
                        color: 'primary'
                    },
                    {
                        label: 'Delete Selected',
                        icon: <PeopleIcon />,
                        onClick: (ids) => console.log('Delete:', ids),
                        color: 'error'
                    }
                ]}
                
                rowActions={[
                    {
                        icon: <AnalyticsIcon />,
                        label: 'View Details',
                        onClick: (row) => console.log('View:', row.id),
                        color: 'primary'
                    }
                ]}
                
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