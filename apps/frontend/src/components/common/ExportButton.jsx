import React, { useState } from 'react';
import {
    Button,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    CircularProgress,
    Alert,
    Snackbar
} from '@mui/material';
import {
    FileDownload as DownloadIcon,
    TableChart as CsvIcon,
    Image as PngIcon,
    ExpandMore as ExpandIcon
} from '@mui/icons-material';
import { apiClient } from '../../utils/apiClient.js';

/**
 * Export Button Component for Analytics Data
 * Week 1-2 Quick Win Implementation
 */
const ExportButton = ({ 
    channelId = 'demo_channel', 
    dataType = 'engagement', 
    period = '7d',
    disabled = false,
    size = 'medium',
    ...props 
}) => {
    const [anchorEl, setAnchorEl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const open = Boolean(anchorEl);

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const downloadFile = (data, filename, type = 'csv') => {
        try {
            let blob;
            let url;

            if (type === 'csv') {
                blob = new Blob([data], { type: 'text/csv;charset=utf-8;' });
            } else if (type === 'png') {
                // Handle PNG data (base64 or blob)
                if (typeof data === 'string' && data.startsWith('data:image')) {
                    // Base64 data URL
                    const link = document.createElement('a');
                    link.href = data;
                    link.download = filename;
                    link.click();
                    return;
                } else {
                    blob = new Blob([data], { type: 'image/png' });
                }
            }

            url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Download failed:', err);
            setError('Failed to download file');
        }
    };

    const handleExport = async (format) => {
        setLoading(true);
        setError(null);
        handleClose();

        try {
            let response;
            let filename;

            if (format === 'csv') {
                response = await apiClient.exportToCsv(dataType, channelId, period);
                filename = `${dataType}_${channelId}_${period}.csv`;
                
                // Handle different response formats
                if (typeof response === 'string') {
                    downloadFile(response, filename, 'csv');
                } else if (response.csv_data) {
                    downloadFile(response.csv_data, filename, 'csv');
                } else {
                    throw new Error('Invalid CSV response format');
                }
            } else if (format === 'png') {
                response = await apiClient.exportToPng(dataType, channelId, period);
                filename = `${dataType}_${channelId}_${period}.png`;
                
                // Handle different response formats
                if (typeof response === 'string') {
                    downloadFile(response, filename, 'png');
                } else if (response.png_data) {
                    downloadFile(response.png_data, filename, 'png');
                } else {
                    throw new Error('Invalid PNG response format');
                }
            }

            setSuccess(`${format.toUpperCase()} exported successfully!`);
        } catch (err) {
            console.error('Export failed:', err);
            setError(`Failed to export ${format.toUpperCase()}: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <Button
                variant="outlined"
                startIcon={loading ? <CircularProgress size={16} /> : <DownloadIcon />}
                endIcon={!loading && <ExpandIcon />}
                onClick={handleClick}
                disabled={disabled || loading}
                size={size}
                aria-haspopup="true"
                aria-expanded={open ? 'true' : 'false'}
                aria-label="Export analytics data"
                {...props}
            >
                {loading ? 'Exporting...' : 'Export'}
            </Button>

            <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'left',
                }}
                transformOrigin={{
                    vertical: 'top',
                    horizontal: 'left',
                }}
            >
                <MenuItem onClick={() => handleExport('csv')} disabled={loading}>
                    <ListItemIcon>
                        <CsvIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                        primary="Export as CSV"
                        secondary="Spreadsheet format"
                    />
                </MenuItem>

                <MenuItem onClick={() => handleExport('png')} disabled={loading}>
                    <ListItemIcon>
                        <PngIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                        primary="Export as PNG"
                        secondary="Chart image"
                    />
                </MenuItem>
            </Menu>

            {/* Success Notification */}
            <Snackbar
                open={!!success}
                autoHideDuration={4000}
                onClose={() => setSuccess(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert 
                    onClose={() => setSuccess(null)} 
                    severity="success"
                    variant="filled"
                >
                    {success}
                </Alert>
            </Snackbar>

            {/* Error Notification */}
            <Snackbar
                open={!!error}
                autoHideDuration={6000}
                onClose={() => setError(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert 
                    onClose={() => setError(null)} 
                    severity="error"
                    variant="filled"
                >
                    {error}
                </Alert>
            </Snackbar>
        </>
    );
};

export default ExportButton;
