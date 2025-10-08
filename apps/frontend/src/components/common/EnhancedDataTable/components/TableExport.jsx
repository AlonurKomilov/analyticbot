import React, { useState } from 'react';
import {
    IconButton,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Divider,
    Typography,
    Tooltip
} from '@mui/material';
import {
    GetApp as ExportIcon,
    PictureAsPdf as PdfIcon,
    TableChart as CsvIcon,
    Assessment as ExcelIcon
} from '@mui/icons-material';
import { EXPORT_FORMATS } from '../utils/exportUtils';

/**
 * TableExport Component
 * Renders export functionality with format selection menu
 */
const TableExport = ({
    onExport,
    exportFilename = 'data-export'
}) => {
    const [exportMenuAnchor, setExportMenuAnchor] = useState(null);

    const handleExportClick = (format) => {
        onExport?.(format);
        setExportMenuAnchor(null);
    };

    const getFormatIcon = (format) => {
        switch (format.key) {
            case 'csv':
                return <CsvIcon fontSize="small" />;
            case 'excel':
                return <ExcelIcon fontSize="small" />;
            case 'pdf':
                return <PdfIcon fontSize="small" />;
            default:
                return <ExportIcon fontSize="small" />;
        }
    };

    return (
        <>
            <Tooltip title="Export Data">
                <IconButton
                    onClick={(e) => setExportMenuAnchor(e.currentTarget)}
                    aria-label="Export table data"
                >
                    <ExportIcon />
                </IconButton>
            </Tooltip>

            <Menu
                anchorEl={exportMenuAnchor}
                open={Boolean(exportMenuAnchor)}
                onClose={() => setExportMenuAnchor(null)}
            >
                <MenuItem disabled>
                    <Typography variant="subtitle2">Export As</Typography>
                </MenuItem>
                <Divider />
                {EXPORT_FORMATS.map(format => (
                    <MenuItem
                        key={format.key}
                        onClick={() => handleExportClick(format.key)}
                    >
                        <ListItemIcon>
                            {getFormatIcon(format)}
                        </ListItemIcon>
                        <ListItemText>{format.label}</ListItemText>
                    </MenuItem>
                ))}
            </Menu>
        </>
    );
};

export default TableExport;
