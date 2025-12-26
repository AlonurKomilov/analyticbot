/**
 * PostsViewControls Component
 * View mode toggle (table/grid) and column management menu
 */

import React, { useState } from 'react';
import {
  Box,
  IconButton,
  Menu,
  MenuItem,
  Checkbox,
  ListItemText,
  Divider,
  Typography,
} from '@mui/material';
import { ViewColumn, ViewModule, TableRows, Visibility } from '@mui/icons-material';
import type { VisibleColumns, ViewMode } from '../types/Post';

interface PostsViewControlsProps {
  viewMode: ViewMode;
  visibleColumns: VisibleColumns;
  visibleCount: number;
  totalCount: number;
  onViewModeChange: (mode: ViewMode) => void;
  onColumnToggle: (column: keyof VisibleColumns) => void;
  onShowAllColumns: () => void;
  onHideAllColumns: () => void;
}

export const PostsViewControls: React.FC<PostsViewControlsProps> = ({
  viewMode,
  visibleColumns,
  visibleCount,
  totalCount,
  onViewModeChange,
  onColumnToggle,
  onShowAllColumns,
  onHideAllColumns,
}) => {
  const [columnMenuAnchor, setColumnMenuAnchor] = useState<null | HTMLElement>(null);

  const handleColumnMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setColumnMenuAnchor(event.currentTarget);
  };

  const handleColumnMenuClose = () => {
    setColumnMenuAnchor(null);
  };

  return (
    <>
      <Box sx={{ display: 'flex', gap: 1 }}>
        {/* View Mode Toggle */}
        <Box sx={{ display: 'flex', border: 1, borderColor: 'divider', borderRadius: 1 }}>
          <IconButton
            onClick={() => onViewModeChange('table')}
            size="small"
            sx={{
              borderRadius: '4px 0 0 4px',
              bgcolor: viewMode === 'table' ? 'action.selected' : 'transparent'
            }}
            title="Table View"
          >
            <TableRows fontSize="small" />
          </IconButton>
          <IconButton
            onClick={() => onViewModeChange('grid')}
            size="small"
            sx={{
              borderRadius: '0 4px 4px 0',
              bgcolor: viewMode === 'grid' ? 'action.selected' : 'transparent'
            }}
            title="Grid View"
          >
            <ViewModule fontSize="small" />
          </IconButton>
        </Box>

        {/* Manage Columns Button */}
        <IconButton
          onClick={handleColumnMenuOpen}
          size="small"
          sx={{
            border: 1,
            borderColor: 'divider',
            borderRadius: 1
          }}
          title="Manage Columns"
        >
          <ViewColumn fontSize="small" />
        </IconButton>
      </Box>

      {/* Column Management Menu */}
      <Menu
        anchorEl={columnMenuAnchor}
        open={Boolean(columnMenuAnchor)}
        onClose={handleColumnMenuClose}
        PaperProps={{
          sx: { width: 220, maxHeight: 400 }
        }}
      >
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle2" color="text.secondary">
            Columns ({visibleCount}/{totalCount} visible)
          </Typography>
        </Box>
        <Divider />
        <MenuItem onClick={() => onColumnToggle('channel')}>
          <Checkbox checked={visibleColumns.channel} size="small" />
          <ListItemText primary="Channel" />
        </MenuItem>
        <MenuItem onClick={() => onColumnToggle('messageId')}>
          <Checkbox checked={visibleColumns.messageId} size="small" />
          <ListItemText primary="Message ID" />
        </MenuItem>
        <MenuItem onClick={() => onColumnToggle('content')}>
          <Checkbox checked={visibleColumns.content} size="small" />
          <ListItemText primary="Content" />
        </MenuItem>
        <MenuItem onClick={() => onColumnToggle('views')}>
          <Checkbox checked={visibleColumns.views} size="small" />
          <ListItemText primary="Views" />
        </MenuItem>
        <MenuItem onClick={() => onColumnToggle('forwards')}>
          <Checkbox checked={visibleColumns.forwards} size="small" />
          <ListItemText primary="Forwards" />
        </MenuItem>
        <MenuItem onClick={() => onColumnToggle('comments')}>
          <Checkbox checked={visibleColumns.comments} size="small" />
          <ListItemText primary="Comments" />
        </MenuItem>
        <MenuItem onClick={() => onColumnToggle('reactions')}>
          <Checkbox checked={visibleColumns.reactions} size="small" />
          <ListItemText primary="Reactions" />
        </MenuItem>
        <MenuItem onClick={() => onColumnToggle('telegram')}>
          <Checkbox checked={visibleColumns.telegram} size="small" />
          <ListItemText primary="Telegram" />
        </MenuItem>
        <MenuItem onClick={() => onColumnToggle('date')}>
          <Checkbox checked={visibleColumns.date} size="small" />
          <ListItemText primary="Date" />
        </MenuItem>
        <Divider />
        <MenuItem onClick={onShowAllColumns}>
          <Visibility fontSize="small" sx={{ mr: 1 }} />
          <ListItemText primary="Show All" />
        </MenuItem>
        <MenuItem onClick={onHideAllColumns}>
          <Typography variant="body2">Hide All</Typography>
        </MenuItem>
      </Menu>
    </>
  );
};
