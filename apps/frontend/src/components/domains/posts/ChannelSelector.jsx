/**
 * ChannelSelector - Channel selection component for post scheduling
 */

import React, { useMemo } from 'react';
import { FormControl, InputLabel, Select, MenuItem, Typography } from '@mui/material';

const ChannelSelector = ({
    channels = [],
    selectedChannel,
    onChange,
    error,
    disabled = false
}) => {
    // Memoized channel options
    const channelOptions = useMemo(() =>
        channels.map(channel => ({
            value: channel.id,
            label: channel.title || channel.username || 'Unknown Channel'
        })),
        [channels]
    );

    return (
        <FormControl fullWidth error={!!error} disabled={disabled}>
            <InputLabel
                id="channel-select-label"
                required
                aria-label="Select channel for posting"
            >
                Select Channel
            </InputLabel>
            <Select
                labelId="channel-select-label"
                value={selectedChannel || ''}
                onChange={(e) => onChange(e.target.value)}
                label="Select Channel"
                aria-describedby={error ? "channel-error" : "channel-help"}
                id="channel-select"
                autoComplete="off"
            >
                {channelOptions.length > 0 ? (
                    channelOptions.map((option) => (
                        <MenuItem
                            key={option.value}
                            value={option.value}
                            aria-label={`Select ${option.label}`}
                        >
                            {option.label}
                        </MenuItem>
                    ))
                ) : (
                    <MenuItem disabled>
                        No channels available
                    </MenuItem>
                )}
            </Select>

            {!error && channelOptions.length === 0 && (
                <Typography
                    variant="caption"
                    color="text.secondary"
                    id="channel-help"
                    sx={{ mt: 0.5 }}
                >
                    No channels available. Please add a channel first.
                </Typography>
            )}

            {error && (
                <Typography
                    variant="caption"
                    color="error"
                    id="channel-error"
                    role="alert"
                    sx={{ mt: 0.5, display: 'block' }}
                >
                    {error}
                </Typography>
            )}
        </FormControl>
    );
};

ChannelSelector.displayName = 'ChannelSelector';

export default ChannelSelector;
