/**
 * ChannelSelector - Channel selection component for post scheduling
 */

import React, { useMemo } from 'react';
import { FormControl, InputLabel, Select, MenuItem, Typography, SelectChangeEvent } from '@mui/material';

interface Channel {
    id: string | number;
    title?: string;
    username?: string;
}

interface ChannelOption {
    value: string | number;
    label: string;
}

interface ChannelSelectorProps {
    channels?: Channel[];
    selectedChannel: string | number | null;
    onChange: (value: string | number) => void;
    error?: string;
    disabled?: boolean;
}

const ChannelSelector: React.FC<ChannelSelectorProps> = ({
    channels = [],
    selectedChannel,
    onChange,
    error,
    disabled = false
}) => {
    // Memoized channel options - convert ID to string for consistency
    const channelOptions = useMemo<ChannelOption[]>(() =>
        channels.map(channel => ({
            value: String(channel.id),
            label: channel.title || channel.username || 'Unknown Channel'
        })),
        [channels]
    );

    const handleChange = (e: SelectChangeEvent<string | number>): void => {
        onChange(e.target.value as string | number);
    };

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
                value={selectedChannel ? String(selectedChannel) : ''}
                onChange={handleChange}
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
