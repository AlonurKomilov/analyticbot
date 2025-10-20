import React, { useState, MouseEvent } from 'react';
import {
    IconButton,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Tooltip
} from '@mui/material';
import {
    Analytics as AnalyticsIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    GetApp as DownloadIcon,
    MoreVert as MoreVertIcon,
    Share as ShareIcon,
    Visibility as VisibilityIcon
} from '@mui/icons-material';

type PostAction = 'view' | 'analytics' | 'edit' | 'share' | 'download' | 'delete';

interface PostActionsProps {
    row: any;
    onAction?: (action: PostAction, row: any) => void;
}

/**
 * Row actions menu for posts
 */
export const PostActions: React.FC<PostActionsProps> = ({ row, onAction }) => {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);

    const handleClick = (event: MouseEvent<HTMLElement>): void => {
        event.stopPropagation();
        setAnchorEl(event.currentTarget);
    };

    const handleClose = (): void => {
        setAnchorEl(null);
    };

    const handleAction = (action: PostAction): void => {
        handleClose();
        onAction?.(action, row);
    };

    return (
        <>
            <Tooltip title="Post Actions">
                <IconButton
                    size="small"
                    onClick={handleClick}
                    aria-label="post actions"
                >
                    <MoreVertIcon fontSize="small" />
                </IconButton>
            </Tooltip>
            <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
                onClick={(e) => e.stopPropagation()}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
                <MenuItem onClick={() => handleAction('view')}>
                    <ListItemIcon>
                        <VisibilityIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="View Details" />
                </MenuItem>
                <MenuItem onClick={() => handleAction('analytics')}>
                    <ListItemIcon>
                        <AnalyticsIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="View Analytics" />
                </MenuItem>
                <MenuItem onClick={() => handleAction('edit')}>
                    <ListItemIcon>
                        <EditIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Edit Post" />
                </MenuItem>
                <MenuItem onClick={() => handleAction('share')}>
                    <ListItemIcon>
                        <ShareIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Share Post" />
                </MenuItem>
                <MenuItem onClick={() => handleAction('download')}>
                    <ListItemIcon>
                        <DownloadIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Download Report" />
                </MenuItem>
                <MenuItem
                    onClick={() => handleAction('delete')}
                    sx={{ color: 'error.main' }}
                >
                    <ListItemIcon>
                        <DeleteIcon fontSize="small" color="error" />
                    </ListItemIcon>
                    <ListItemText primary="Delete Post" />
                </MenuItem>
            </Menu>
        </>
    );
};

interface PostBulkActionsProps {
    selectedRows: any[];
    onBulkAction?: (action: PostAction, selectedRows: any[]) => void;
}

/**
 * Bulk actions for selected posts
 */
export const PostBulkActions: React.FC<PostBulkActionsProps> = ({ selectedRows, onBulkAction }) => {
    const handleBulkAction = (action: PostAction): void => {
        onBulkAction?.(action, selectedRows);
    };

    if (selectedRows.length === 0) {
        return null;
    }

    return (
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <Tooltip title="Download Selected Reports">
                <IconButton
                    size="small"
                    onClick={() => handleBulkAction('download')}
                >
                    <DownloadIcon fontSize="small" />
                </IconButton>
            </Tooltip>
            <Tooltip title="View Analytics for Selected">
                <IconButton
                    size="small"
                    onClick={() => handleBulkAction('analytics')}
                >
                    <AnalyticsIcon fontSize="small" />
                </IconButton>
            </Tooltip>
            <Tooltip title="Delete Selected Posts">
                <IconButton
                    size="small"
                    onClick={() => handleBulkAction('delete')}
                    sx={{ color: 'error.main' }}
                >
                    <DeleteIcon fontSize="small" />
                </IconButton>
            </Tooltip>
        </div>
    );
};
