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

    const formatDateForInput = (date: Date | null | string): string => {
        if (!date) return '';
        
        // If it's already a string in datetime-local format, return it directly
        if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(date)) {
            return date.slice(0, 16);
        }
        
        // If it's a Date object, format it to local timezone
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        const year = dateObj.getFullYear();
        const month = String(dateObj.getMonth() + 1).padStart(2, '0');
        const day = String(dateObj.getDate()).padStart(2, '0');
        const hours = String(dateObj.getHours()).padStart(2, '0');
        const minutes = String(dateObj.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
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
