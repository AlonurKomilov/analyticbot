/**
 * Optimization Settings Component
 * Configuration options for content optimization
 */

import React from 'react';
import {
  Box,
  CardContent,
  Typography,
  FormControlLabel,
  Switch,
  Divider
} from '@mui/material';

interface OptimizationSettingsProps {
  autoOptimization: boolean;
  onAutoOptimizationChange: (enabled: boolean) => void;
}

export const OptimizationSettings: React.FC<OptimizationSettingsProps> = ({
  autoOptimization,
  onAutoOptimizationChange
}) => {
  return (
    <CardContent>
      <Typography variant="h6" sx={{ mb: 3 }}>
        Optimization Settings
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <FormControlLabel
          control={
            <Switch
              checked={autoOptimization}
              onChange={(e) => onAutoOptimizationChange(e.target.checked)}
            />
          }
          label="Automatic Content Optimization"
        />

        <Divider />

        <Typography variant="subtitle1" fontWeight={600}>
          Optimization Targets
        </Typography>

        <FormControlLabel
          control={<Switch defaultChecked />}
          label="Engagement Rate"
        />
        <FormControlLabel
          control={<Switch defaultChecked />}
          label="Readability Score"
        />
        <FormControlLabel
          control={<Switch />}
          label="SEO Optimization"
        />
        <FormControlLabel
          control={<Switch defaultChecked />}
          label="Sentiment Analysis"
        />
      </Box>
    </CardContent>
  );
};

export default OptimizationSettings;
