import React from 'react';
import { Chip, Box, Tooltip, CircularProgress } from '@mui/material';
import { useDataSource } from '../../hooks/useDataSource';

/**
 * Global Data Source Switch Component
 * 
 * Provides a consistent, reusable switch for toggling between real API and demo data.
 * Can be placed in navigation headers, component headers, or anywhere users need
 * to see and control the current data source.
 */
const GlobalDataSourceSwitch = ({ 
  size = 'small', 
  showLabel = true, 
  variant = 'filled',
  sx = {}
}) => {
  const { isUsingRealAPI, switchDataSource, dataSource } = useDataSource();
  
  const [switching, setSwitching] = React.useState(false);
  
  const handleSwitch = async () => {
    setSwitching(true);
    
    try {
      // Switch data source
      await switchDataSource(isUsingRealAPI ? 'mock' : 'api');
      
      // Brief delay to show feedback
      setTimeout(() => setSwitching(false), 300);
      
    } catch (error) {
      console.error('Failed to switch data source:', error);
      setSwitching(false);
    }
  };
  
  if (switching) {
    return (
      <Chip
        icon={<CircularProgress size={14} />}
        label="Switching..."
        size={size}
        variant={variant}
        sx={{ ...sx, cursor: 'wait' }}
      />
    );
  }
  
  return (
    <Tooltip 
      title={`Currently using ${isUsingRealAPI ? 'real API data from your channels' : 'professional demo data'}. Click to switch to ${isUsingRealAPI ? 'demo' : 'real API'} data.`}
      arrow
    >
      <Chip
        label={showLabel ? (isUsingRealAPI ? '🔴 Real API' : '🟡 Demo Data') : (isUsingRealAPI ? '🔴' : '🟡')}
        color={isUsingRealAPI ? 'success' : 'warning'}
        size={size}
        variant={variant}
        onClick={handleSwitch}
        sx={{ 
          cursor: 'pointer', 
          fontWeight: 'medium',
          '&:hover': {
            transform: 'scale(1.02)',
            transition: 'transform 0.1s ease'
          },
          ...sx 
        }}
      />
    </Tooltip>
  );
};

/**
 * Compact data source indicator (no click functionality)
 * Useful for showing status without switching capability
 */
export const DataSourceBadge = ({ size = 'small', sx = {} }) => {
  const { isUsingRealAPI } = useDataSource();
  
  return (
    <Tooltip title={`Using ${isUsingRealAPI ? 'real API' : 'demo'} data`}>
      <Chip
        label={isUsingRealAPI ? '🔴 Live' : '🟡 Demo'} 
        size={size}
        color={isUsingRealAPI ? 'success' : 'warning'}
        variant="outlined"
        sx={{ 
          fontSize: '0.7rem',
          height: '20px',
          ...sx 
        }}
      />
    </Tooltip>
  );
};

export default GlobalDataSourceSwitch;