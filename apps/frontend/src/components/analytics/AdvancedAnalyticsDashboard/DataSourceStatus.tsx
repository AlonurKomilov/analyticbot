/**
 * DataSourceStatus Component
 *
 * Displays the current data source status with loading state,
 * error handling, and optional header with actions.
 */

import React, { ReactNode } from 'react';
import {
    Box,
    Paper,
    Typography,
    LinearProgress,
    Alert,
    Button,
    Chip
} from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';

interface DataSourceStatusProps {
    isLoading: boolean;
    hasError: boolean;
    errors: Record<string, string>;
    actions?: ReactNode;
    isUsingRealAPI?: boolean;
    dataSource?: string;
    switchDataSource?: () => void;
    onRefresh?: () => void;
}

const DataSourceStatus: React.FC<DataSourceStatusProps> = ({
    isLoading,
    hasError,
    errors,
    actions,
    isUsingRealAPI = false,
    dataSource = 'Unknown',
    switchDataSource,
    onRefresh
}) => {
    if (isLoading) {
        return (
            <Box sx={{ width: '100%', mb: 2 }}>
                <LinearProgress />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
                    Loading data...
                </Typography>
            </Box>
        );
    }

    if (hasError) {
        return (
            <Alert severity="error" sx={{ mb: 2 }}>
                <Typography variant="body2" fontWeight={600} gutterBottom>
                    Error Loading Data
                </Typography>
                {Object.entries(errors).map(([key, message]) => (
                    <Typography key={key} variant="body2">
                        {key}: {message}
                    </Typography>
                ))}
            </Alert>
        );
    }

    return (
        <Paper
            elevation={2}
            sx={{
                p: 2,
                mb: 3,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                bgcolor: 'background.paper'
            }}
        >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="h6" fontWeight={600}>
                    Data Source Status
                </Typography>
                <Chip
                    label={isUsingRealAPI ? 'Real API' : 'Mock Data'}
                    color={isUsingRealAPI ? 'success' : 'warning'}
                    size="small"
                />
                <Typography variant="body2" color="text.secondary">
                    Source: {dataSource}
                </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
                {onRefresh && (
                    <Button
                        variant="outlined"
                        size="small"
                        startIcon={<RefreshIcon />}
                        onClick={onRefresh}
                    >
                        Refresh
                    </Button>
                )}
                {switchDataSource && (
                    <Button
                        variant="contained"
                        size="small"
                        onClick={switchDataSource}
                    >
                        Switch to {isUsingRealAPI ? 'Mock' : 'Real'} Data
                    </Button>
                )}
                {actions}
            </Box>
        </Paper>
    );
};

export default DataSourceStatus;
