/**
 * SchedulePostButton Component
 *
 * Quick action button to schedule a post at the recommended time
 * Integrates with the post scheduling system
 */

import React, { useState } from 'react';
import {
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Typography,
    Box,
    Alert
} from '@mui/material';
import {
    Event as EventIcon,
    CheckCircle as CheckIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface SchedulePostButtonProps {
    recommendedHour: number;
    recommendedDay: number; // 0=Sunday, 1=Monday, etc.
    channelId: string;
}

const SchedulePostButton: React.FC<SchedulePostButtonProps> = ({
    recommendedHour,
    recommendedDay,
    channelId
}) => {
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);

    const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    const formatHour = (hour: number): string => {
        if (hour === 0) return '12:00 AM';
        if (hour < 12) return `${hour}:00 AM`;
        if (hour === 12) return '12:00 PM';
        return `${hour - 12}:00 PM`;
    };

    // Calculate next occurrence of recommended day/time
    const getNextRecommendedDateTime = (): Date => {
        const now = new Date();
        const currentDay = now.getDay();
        const currentHour = now.getHours();

        // Calculate days until next occurrence
        let daysUntil = recommendedDay - currentDay;
        if (daysUntil < 0 || (daysUntil === 0 && currentHour >= recommendedHour)) {
            daysUntil += 7; // Next week
        }

        const nextDate = new Date(now);
        nextDate.setDate(now.getDate() + daysUntil);
        nextDate.setHours(recommendedHour, 0, 0, 0);

        return nextDate;
    };

    const handleScheduleClick = () => {
        setOpen(true);
    };

    const handleConfirmSchedule = () => {
        const scheduledTime = getNextRecommendedDateTime();

        // Navigate to create post page with pre-filled schedule time
        navigate('/posts/create', {
            state: {
                channelId,
                scheduledTime: scheduledTime.toISOString(),
                fromRecommendation: true
            }
        });
    };

    const nextDateTime = getNextRecommendedDateTime();
    const dayName = daysOfWeek[recommendedDay];
    const timeStr = formatHour(recommendedHour);

    return (
        <>
            <Button
                variant="contained"
                color="success"
                startIcon={<EventIcon />}
                onClick={handleScheduleClick}
                size="large"
                fullWidth
                sx={{ mt: 2 }}
            >
                📅 Schedule Post for {dayName} {timeStr}
            </Button>

            <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <EventIcon color="primary" />
                        Schedule Post at Best Time
                    </Box>
                </DialogTitle>
                <DialogContent>
                    <Alert severity="info" sx={{ mb: 2 }}>
                        <Typography variant="body2">
                            Based on performance analysis, this is the optimal time for your channel
                        </Typography>
                    </Alert>

                    <Box sx={{ my: 2, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            Recommended Time:
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                            {dayName}, {timeStr}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            Next occurrence: {nextDateTime.toLocaleString()}
                        </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
                        <CheckIcon color="success" fontSize="small" />
                        <Typography variant="body2">
                            You'll be redirected to create your post with this time pre-selected
                        </Typography>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)} color="inherit">
                        Cancel
                    </Button>
                    <Button
                        onClick={handleConfirmSchedule}
                        variant="contained"
                        color="success"
                        startIcon={<EventIcon />}
                    >
                        Continue to Create Post
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

export default SchedulePostButton;
