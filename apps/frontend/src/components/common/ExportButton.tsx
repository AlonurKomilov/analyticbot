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
// import { analyticsService } from '@services/analyticsService.js';
// import { useAnalyticsStore } from '@/stores'; // TODO: Use for real export functionality

/**
 * Export Button Component for Analytics Data
 * Updated to use new mock/real data source architecture
 *
 * @component
 * @example
 * ```tsx
 * <ExportButton
 *   channelId="my_channel"
 *   dataType="engagement"
 *   period="7d"
 * />
 * ```
 */

export type ExportFormat = 'csv' | 'png';

export interface ExportButtonProps {
  /** Channel ID for analytics data */
  channelId?: string;
  /** Type of analytics data to export */
  dataType?: string;
  /** Time period for data */
  period?: string;
  /** Whether button is disabled */
  disabled?: boolean;
  /** Button size */
  size?: 'small' | 'medium' | 'large';
  /** Additional props */
  [key: string]: any;
}

const ExportButton: React.FC<ExportButtonProps> = ({
    channelId = 'demo_channel',
    dataType = 'engagement',
    period = '7d',
    disabled = false,
    size = 'medium',
    ...props
}) => {
    // const analyticsStore = useAnalyticsStore(); // TODO: Use for real export functionality
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const open = Boolean(anchorEl);

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>): void => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = (): void => {
        setAnchorEl(null);
    };

    const downloadFile = (data: string | Blob, filename: string, type: ExportFormat = 'csv'): void => {
        try {
            let blob: Blob;
            let url: string;

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
            } else {
                throw new Error(`Unsupported export type: ${type}`);
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

    const handleExport = async (format: ExportFormat): Promise<void> => {
        setLoading(true);
        setError(null);
        handleClose();

        try {
            // TODO: Implement proper export functionality with analytics store
            // For now, create mock data to download
            let response: any;
            let filename: string;

            if (format === 'csv') {
                response = `Channel,Period,DataType\n${channelId},${period},${dataType}\n`;
                filename = `${dataType}_${channelId}_${period}.csv`;
            } else if (format === 'png') {
                // Create a simple canvas with text for demonstration
                const canvas = document.createElement('canvas');
                canvas.width = 400;
                canvas.height = 200;
                const ctx = canvas.getContext('2d');
                if (ctx) {
                    ctx.fillStyle = '#f0f0f0';
                    ctx.fillRect(0, 0, 400, 200);
                    ctx.fillStyle = '#000';
                    ctx.font = '20px Arial';
                    ctx.fillText(`${dataType} - ${channelId}`, 50, 100);
                }
                response = canvas.toDataURL('image/png');
                filename = `${dataType}_${channelId}_${period}.png`;
            } else {
                throw new Error(`Unsupported format: ${format}`);
            }

            // Handle different response formats
            if (typeof response === 'string') {
                downloadFile(response, filename, format);
            } else if (response.csv_data || response.png_data) {
                downloadFile(response.csv_data || response.png_data, filename, format);
            } else {
                throw new Error(`Invalid ${format.toUpperCase()} response format`);
            }

            setSuccess(`${format.toUpperCase()} exported successfully!`);
        } catch (err) {
            console.error('Export failed:', err);
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(`Failed to export ${format.toUpperCase()}: ${errorMessage}`);
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
