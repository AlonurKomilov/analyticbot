import React from 'react';
import { Box } from '@mui/material';
import { Button } from '../../common';

const ChartTypeSelector = React.memo(({ chartType, onChartTypeChange }) => {
    return (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Button
                variant={chartType === 'line' ? 'primary' : 'secondary'}
                size="small"
                onClick={() => onChartTypeChange('line')}
            >
                Line
            </Button>
            <Button
                variant={chartType === 'area' ? 'primary' : 'secondary'}
                size="small"
                onClick={() => onChartTypeChange('area')}
            >
                Area
            </Button>
            <Button
                variant={chartType === 'bar' ? 'primary' : 'secondary'}
                size="small"
                onClick={() => onChartTypeChange('bar')}
            >
                Bar
            </Button>
        </Box>
    );
});

ChartTypeSelector.displayName = 'ChartTypeSelector';

export default ChartTypeSelector;
