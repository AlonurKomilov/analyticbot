/**
 * ScheduleTimeInput - Date/time scheduling component for posts
 */

import React from 'react';
import { TextField, Typography } from '@mui/material';

/**
 * Props for ScheduleTimeInput component
 */
interface ScheduleTimeInputProps {
    /** Current schedule date/time value */
    value: Date | null;
    /** Callback when date/time changes */
    onChange: (value: Date | null) => void;
    /** Error message */
    error?: string;
    /** Disabled state */
    disabled?: boolean;
}

/**
 * ScheduleTimeInput Component
 * Date and time picker for post scheduling
 */
const ScheduleTimeInput: React.FC<ScheduleTimeInputProps> = ({
    value,
    onChange,
    error,
    disabled = false
}) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value ? new Date(e.target.value) : null;
        onChange(newValue);
    };

    const formatDateForInput = (date: Date | null): string => {
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
