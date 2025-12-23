/**
 * Security Settings Component
 * Configuration options for security monitoring
 */

import React from 'react';
import {
  CardContent,
  Typography,
  Box,
  FormControlLabel,
  Switch
} from '@mui/material';

interface SecuritySettingsProps {
  realTimeMonitoring: boolean;
  onRealTimeMonitoringChange: (enabled: boolean) => void;
}

export const SecuritySettings: React.FC<SecuritySettingsProps> = ({
  realTimeMonitoring,
  onRealTimeMonitoringChange
}) => {
  return (
    <CardContent>
      <Typography variant="h6" sx={{ mb: 3 }}>
        Security Monitoring Settings
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <FormControlLabel
          control={
            <Switch
              checked={realTimeMonitoring}
              onChange={(e) => onRealTimeMonitoringChange(e.target.checked)}
            />
          }
          label="Real-time Threat Monitoring"
        />

        <FormControlLabel
          control={<Switch defaultChecked />}
          label="Email Alert Notifications"
        />

        <FormControlLabel
          control={<Switch defaultChecked />}
          label="Auto-block Suspicious IPs"
        />

        <FormControlLabel
          control={<Switch />}
          label="Advanced Threat Detection"
        />

        <FormControlLabel
          control={<Switch defaultChecked />}
          label="Security Audit Logging"
        />
      </Box>
    </CardContent>
  );
};

export default SecuritySettings;
