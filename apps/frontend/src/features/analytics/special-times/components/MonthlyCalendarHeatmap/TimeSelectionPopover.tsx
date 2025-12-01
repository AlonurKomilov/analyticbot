/**
 * TimeSelectionPopover Component
 * Popover for selecting time slot when clicking on a future day
 */

import React from 'react';
import { 
    Popover, 
    Box, 
    Typography, 
    Button, 
    Divider,
    List,
    ListItemButton,
    ListItemIcon,
    ListItemText
} from '@mui/material';
import { 
    Schedule, 
    TrendingUp,
    Add
} from '@mui/icons-material';
import { DayPerformance } from './types';

const WEEK_DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

interface TimeSelectionPopoverProps {
    anchorEl: HTMLElement | null;
    selectedDay: DayPerformance | null;
    onClose: () => void;
    onTimeSelect: (time: string) => void;
    onCustomTime: () => void;
}

export const TimeSelectionPopover: React.FC<TimeSelectionPopoverProps> = ({
    anchorEl,
    selectedDay,
    onClose,
    onTimeSelect,
    onCustomTime
}) => {
    const isOpen = Boolean(anchorEl);

    return (
        <Popover
            open={isOpen}
            anchorEl={anchorEl}
            onClose={onClose}
            anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'center',
            }}
            transformOrigin={{
                vertical: 'top',
                horizontal: 'center',
            }}
        >
            <Box sx={{ p: 2, minWidth: 220 }}>
                <Typography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Schedule fontSize="small" color="primary" />
                    Schedule for {selectedDay && `${WEEK_DAYS[selectedDay.dayOfWeek]}, ${selectedDay.date}`}
                </Typography>
                <Divider sx={{ my: 1 }} />
                <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                    Select recommended time:
                </Typography>
                <List dense sx={{ py: 0 }}>
                    {selectedDay?.recommendedTimes?.map((time, idx) => (
                        <ListItemButton 
                            key={time} 
                            onClick={() => onTimeSelect(time)}
                            sx={{ 
                                borderRadius: 1,
                                mb: 0.5,
                                bgcolor: idx === 0 ? 'success.dark' : 'transparent',
                                '&:hover': {
                                    bgcolor: idx === 0 ? 'success.main' : 'action.hover'
                                }
                            }}
                        >
                            <ListItemIcon sx={{ minWidth: 36 }}>
                                {idx === 0 ? <TrendingUp fontSize="small" color="success" /> : <Schedule fontSize="small" />}
                            </ListItemIcon>
                            <ListItemText 
                                primary={time}
                                secondary={idx === 0 ? 'Best time' : null}
                                primaryTypographyProps={{ 
                                    fontWeight: idx === 0 ? 'bold' : 'normal',
                                    color: idx === 0 ? 'success.light' : 'text.primary'
                                }}
                            />
                        </ListItemButton>
                    ))}
                </List>
                <Divider sx={{ my: 1 }} />
                <Button
                    fullWidth
                    size="small"
                    startIcon={<Add />}
                    onClick={onCustomTime}
                    sx={{ mt: 1 }}
                >
                    Custom time...
                </Button>
            </Box>
        </Popover>
    );
};
