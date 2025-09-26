import React, { useState } from 'react';
import {
    IconButton,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Divider,
    Typography,
    Tooltip,
    FormControlLabel,
    Checkbox
} from '@mui/material';
import {
    ViewColumn as ColumnsIcon,
    SelectAll as SelectAllIcon,
    Visibility,
    VisibilityOff
} from '@mui/icons-material';

/**
 * TableColumns Component
 * Renders column visibility management menu
 */
const TableColumns = ({
    columns,
    columnVisibility,
    setColumnVisibility
}) => {
    const [columnsMenuAnchor, setColumnsMenuAnchor] = useState(null);
    
    const handleShowAll = () => {
        const allVisible = columns.reduce((acc, col) => ({ ...acc, [col.id]: true }), {});
        setColumnVisibility(allVisible);
    };
    
    const handleHideAll = () => {
        const allHidden = columns.reduce((acc, col) => ({ ...acc, [col.id]: false }), {});
        setColumnVisibility(allHidden);
    };
    
    const handleToggleColumn = (columnId, checked) => {
        setColumnVisibility({
            ...columnVisibility,
            [columnId]: checked
        });
    };
    
    const visibleCount = Object.values(columnVisibility).filter(Boolean).length;
    
    return (
        <>
            <Tooltip title="Manage Columns">
                <IconButton
                    onClick={(e) => setColumnsMenuAnchor(e.currentTarget)}
                    aria-label="Manage table columns"
                >
                    <ColumnsIcon />
                </IconButton>
            </Tooltip>
            
            <Menu
                anchorEl={columnsMenuAnchor}
                open={Boolean(columnsMenuAnchor)}
                onClose={() => setColumnsMenuAnchor(null)}
                PaperProps={{
                    style: {
                        maxHeight: 400,
                        width: 250
                    }
                }}
            >
                <MenuItem disabled>
                    <Typography variant="subtitle2">
                        Columns ({visibleCount}/{columns.length} visible)
                    </Typography>
                </MenuItem>
                <Divider />
                
                {/* Column toggles */}
                {columns.map(column => (
                    <MenuItem key={column.id} disableRipple>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    checked={columnVisibility[column.id] || false}
                                    onChange={(e) => handleToggleColumn(column.id, e.target.checked)}
                                    size="small"
                                />
                            }
                            label={column.header || column.id}
                            sx={{ width: '100%', m: 0 }}
                        />
                    </MenuItem>
                ))}
                
                <Divider />
                
                {/* Bulk actions */}
                <MenuItem onClick={handleShowAll}>
                    <ListItemIcon>
                        <Visibility fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Show All</ListItemText>
                </MenuItem>
                
                <MenuItem onClick={handleHideAll}>
                    <ListItemIcon>
                        <VisibilityOff fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Hide All</ListItemText>
                </MenuItem>
            </Menu>
        </>
    );
};

export default TableColumns;