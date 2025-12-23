/**
 * CalendarHeader Component
 * Navigation controls for month switching
 */

import React from 'react';
import { Box, ButtonGroup, Button } from '@mui/material';
import {
    ChevronLeft,
    ChevronRight,
    Today
} from '@mui/icons-material';

interface CalendarHeaderProps {
    onNavigate: (direction: 'prev' | 'next') => void;
    onGoToToday: () => void;
}

export const CalendarHeader: React.FC<CalendarHeaderProps> = ({
    onNavigate,
    onGoToToday
}) => {
    return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ButtonGroup size="small" variant="outlined">
                <Button onClick={() => onNavigate('prev')}>
                    <ChevronLeft />
                </Button>
                <Button onClick={onGoToToday} sx={{ minWidth: 80 }}>
                    <Today fontSize="small" sx={{ mr: 0.5 }} />
                    Today
                </Button>
                <Button onClick={() => onNavigate('next')}>
                    <ChevronRight />
                </Button>
            </ButtonGroup>
        </Box>
    );
};
