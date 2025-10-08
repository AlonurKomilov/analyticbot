/**
 * ScheduleTimeInput - Date/time scheduling component for posts
 */

import React from 'react';
import { TextField, Typography } from '@mui/material';

const ScheduleTimeInput = ({
    value,
    onChange,
    error,
    disabled = false
}) => {
    const handleChange = (e) => {
        const newValue = e.target.value ? new Date(e.target.value) : null;
        onChange(newValue);
    };

    const formatDateForInput = (date) => {
        if (!date) return '';
        return new Date(date).toISOString().slice(0, 16);
    };

    return (
        <>
            <TextField
                label="Schedule for"
                type="datetime-local"
                value={formatDateForInput(value)}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
                error={!!error}
                helperText={error}
                aria-describedby={error ? "schedule-error" : "schedule-help"}
                id="schedule-time"
                autoComplete="off"
                fullWidth
                disabled={disabled}
                inputProps={{
                    'aria-label': 'Schedule time for post',
                    'aria-required': 'true'
                }}
            />

            {!error && (
                <Typography
                    variant="caption"
                    color="text.secondary"
                    id="schedule-help"
                    sx={{ mt: 0.5, display: 'block' }}
                >
                    Choose when your post should be published
                </Typography>
            )}
        </>
    );
};

ScheduleTimeInput.displayName = 'ScheduleTimeInput';

export default ScheduleTimeInput;
