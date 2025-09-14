import React from 'react';
import { Button, ButtonGroup } from '@mui/material';

const ChartTypeSelector = React.memo(({ chartType, onChartTypeChange }) => {
    return (
        <ButtonGroup size="small" variant="outlined">
            <Button 
                variant={chartType === 'line' ? 'contained' : 'outlined'}
                onClick={() => onChartTypeChange('line')}
            >
                Line
            </Button>
            <Button 
                variant={chartType === 'area' ? 'contained' : 'outlined'}
                onClick={() => onChartTypeChange('area')}
            >
                Area
            </Button>
            <Button 
                variant={chartType === 'bar' ? 'contained' : 'outlined'}
                onClick={() => onChartTypeChange('bar')}
            >
                Bar
            </Button>
        </ButtonGroup>
    );
});

ChartTypeSelector.displayName = 'ChartTypeSelector';

export default ChartTypeSelector;