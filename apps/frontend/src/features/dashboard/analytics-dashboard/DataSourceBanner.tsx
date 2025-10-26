/**
 * DataSourceBanner Component
 *
 * Displays a prominent banner indicating whether users are viewing
 * real API data or demo/mock data.
 *
 * Quick Win #3: Data Source Indicator Banner
 */

import React from 'react';
import {
    Alert,
    AlertTitle,
    Box,
    Button,
    Collapse
} from '@mui/material';
import {
    Science as DemoIcon,
    CheckCircle as RealDataIcon,
    Close as CloseIcon
} from '@mui/icons-material';
import { useUIStore } from '@store';

interface DataSourceBannerProps {
    onSwitchToRealData?: () => void;
}

const DataSourceBanner: React.FC<DataSourceBannerProps> = ({ onSwitchToRealData }) => {
    const { dataSource } = useUIStore();
    const [dismissed, setDismissed] = React.useState(false);

    // Only show banner in demo/mock mode
    if (dataSource !== 'mock' || dismissed) {
        return null;
    }

    return (
        <Collapse in={!dismissed}>
            <Alert
                severity="info"
                icon={<DemoIcon />}
                sx={{
                    mb: 3,
                    bgcolor: 'info.50',
                    border: '2px solid',
                    borderColor: 'info.main',
                    '& .MuiAlert-icon': {
                        fontSize: 28
                    }
                }}
                action={
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        {onSwitchToRealData && (
                            <Button
                                size="small"
                                variant="contained"
                                startIcon={<RealDataIcon />}
                                onClick={onSwitchToRealData}
                                sx={{ whiteSpace: 'nowrap' }}
                            >
                                Connect Real Data
                            </Button>
                        )}
                        <Button
                            size="small"
                            startIcon={<CloseIcon />}
                            onClick={() => setDismissed(true)}
                            sx={{ minWidth: 'auto' }}
                        >
                            Dismiss
                        </Button>
                    </Box>
                }
            >
                <AlertTitle sx={{ fontWeight: 600 }}>
                    📊 Viewing Demo Data
                </AlertTitle>
                You're currently viewing sample analytics data for demonstration purposes.
                Connect your channel to see real performance metrics and insights.
            </Alert>
        </Collapse>
    );
};

export default DataSourceBanner;
