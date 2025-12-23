/**
 * ExportButtons Component
 *
 * Provides PDF and CSV export functionality for analytics data.
 * Includes loading states and success feedback.
 *
 * Quick Win #5: Add Export Functionality
 */

import React, { useState } from 'react';
import {
    Box,
    Button,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    CircularProgress,
    Snackbar,
    Alert
} from '@mui/material';
import {
    FileDownload as DownloadIcon,
    PictureAsPdf as PdfIcon,
    TableChart as CsvIcon,
    Image as ImageIcon
} from '@mui/icons-material';

interface ExportButtonsProps {
    onExportPDF?: () => Promise<void>;
    onExportCSV?: () => Promise<void>;
    onExportImage?: () => Promise<void>;
    variant?: 'button' | 'menu';
}

const ExportButtons: React.FC<ExportButtonsProps> = ({
    onExportPDF,
    onExportCSV,
    onExportImage,
    variant = 'menu'
}) => {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [loading, setLoading] = useState(false);
    const [snackbar, setSnackbar] = useState<{
        open: boolean;
        message: string;
        severity: 'success' | 'error';
    }>({
        open: false,
        message: '',
        severity: 'success'
    });

    const handleOpenMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleCloseMenu = () => {
        setAnchorEl(null);
    };

    const handleExport = async (type: 'pdf' | 'csv' | 'image', exportFn?: () => Promise<void>) => {
        handleCloseMenu();

        if (!exportFn) {
            setSnackbar({
                open: true,
                message: 'Export functionality coming soon!',
                severity: 'error'
            });
            return;
        }

        setLoading(true);
        try {
            await exportFn();
            setSnackbar({
                open: true,
                message: `Successfully exported as ${type.toUpperCase()}`,
                severity: 'success'
            });
        } catch (error) {
            setSnackbar({
                open: true,
                message: `Failed to export ${type.toUpperCase()}`,
                severity: 'error'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleCloseSnackbar = () => {
        setSnackbar({ ...snackbar, open: false });
    };

    if (variant === 'button') {
        return (
            <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                    variant="outlined"
                    size="small"
                    startIcon={loading ? <CircularProgress size={16} /> : <PdfIcon />}
                    onClick={() => handleExport('pdf', onExportPDF)}
                    disabled={loading}
                >
                    PDF
                </Button>
                <Button
                    variant="outlined"
                    size="small"
                    startIcon={loading ? <CircularProgress size={16} /> : <CsvIcon />}
                    onClick={() => handleExport('csv', onExportCSV)}
                    disabled={loading}
                >
                    CSV
                </Button>
            </Box>
        );
    }

    return (
        <>
            <Button
                variant="outlined"
                size="small"
                startIcon={loading ? <CircularProgress size={16} /> : <DownloadIcon />}
                onClick={handleOpenMenu}
                disabled={loading}
            >
                Export
            </Button>

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleCloseMenu}
                PaperProps={{
                    sx: {
                        minWidth: 180
                    }
                }}
            >
                <MenuItem onClick={() => handleExport('pdf', onExportPDF)}>
                    <ListItemIcon>
                        <PdfIcon fontSize="small" color="error" />
                    </ListItemIcon>
                    <ListItemText>Export as PDF</ListItemText>
                </MenuItem>

                <MenuItem onClick={() => handleExport('csv', onExportCSV)}>
                    <ListItemIcon>
                        <CsvIcon fontSize="small" color="success" />
                    </ListItemIcon>
                    <ListItemText>Export as CSV</ListItemText>
                </MenuItem>

                <MenuItem onClick={() => handleExport('image', onExportImage)}>
                    <ListItemIcon>
                        <ImageIcon fontSize="small" color="primary" />
                    </ListItemIcon>
                    <ListItemText>Export as Image</ListItemText>
                </MenuItem>
            </Menu>

            <Snackbar
                open={snackbar.open}
                autoHideDuration={4000}
                onClose={handleCloseSnackbar}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert
                    onClose={handleCloseSnackbar}
                    severity={snackbar.severity}
                    variant="filled"
                    sx={{ width: '100%' }}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </>
    );
};

export default ExportButtons;
