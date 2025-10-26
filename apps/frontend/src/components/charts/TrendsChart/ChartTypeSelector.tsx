import React from 'react';
import { Box } from '@mui/material';
import { Button } from '@shared/components';

/**
 * Props for the ChartTypeSelector component
 */
interface ChartTypeSelectorProps {
    /** Current chart type */
    chartType: 'line' | 'area' | 'bar';
    /** Callback when chart type changes */
    onChartTypeChange: (type: 'line' | 'area' | 'bar') => void;
}

const ChartTypeSelector: React.FC<ChartTypeSelectorProps> = React.memo(({ chartType, onChartTypeChange }) => {
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
