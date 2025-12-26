/**
 * PostsFilters Component
 * Channel filter, search input, and stats display
 */

import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  InputAdornment,
  IconButton,
  Typography,
} from '@mui/material';
import { Search, Clear } from '@mui/icons-material';

interface PostsFiltersProps {
  selectedChannel: number | 'all';
  searchQuery: string;
  total: number;
  channels: any[]; // Use any[] to accept channels from store
  onChannelChange: (channel: number | 'all') => void;
  onSearchChange: (query: string) => void;
  onSearchClear: () => void;
}

export const PostsFilters: React.FC<PostsFiltersProps> = ({
  selectedChannel,
  searchQuery,
  total,
  channels,
  onChannelChange,
  onSearchChange,
  onSearchClear,
}) => {
  return (
    <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'space-between' }}>
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
        {/* Channel Filter */}
        <FormControl sx={{ minWidth: 250 }}>
          <InputLabel>Filter by Channel</InputLabel>
          <Select
            value={selectedChannel}
            label="Filter by Channel"
            onChange={(e) => onChannelChange(e.target.value as number | 'all')}
          >
            <MenuItem value="all">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography>All Channels</Typography>
                {channels.length > 0 && (
                  <Typography variant="caption" color="text.secondary">
                    ({channels.length} channels)
                  </Typography>
                )}
              </Box>
            </MenuItem>
            {channels.map((channel) => (
              <MenuItem key={channel.id} value={channel.id}>
                {channel.title || channel.username || channel.name || `Channel ${channel.id}`}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Stats */}
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Total:</strong> {total} posts
          </Typography>
          {(selectedChannel !== 'all' || searchQuery) && (
            <Typography variant="body2" color="primary.main">
              (Filtered)
            </Typography>
          )}
        </Box>
      </Box>

      {/* Search Input - Right Side */}
      <TextField
        placeholder="Search by message ID or content..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        sx={{ minWidth: 300 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search />
            </InputAdornment>
          ),
          endAdornment: searchQuery && (
            <InputAdornment position="end">
              <IconButton size="small" onClick={onSearchClear}>
                <Clear />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
    </Box>
  );
};
