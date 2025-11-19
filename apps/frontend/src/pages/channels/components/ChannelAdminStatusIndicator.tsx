/**
 * Channel Admin Status Indicator
 *
 * Visual indicator showing bot/MTProto admin status for a channel.
 * Helps users understand if their bot or MTProto session has admin access.
 *
 * Status Colors:
 * - Green (success): At least one worker (bot or MTProto) has admin access
 * - Yellow (warning): Only partial access or one worker missing admin
 * - Red/Gray (error): No admin access - data collection disabled
 */

import React from 'react';
import {
    Box,
    Chip,
    Tooltip,
    Typography,
    Alert,
    Stack
} from '@mui/material';
import {
    CheckCircle as CheckCircleIcon,
    Warning as WarningIcon,
    Error as ErrorIcon,
    SmartToy as BotIcon,
    SettingsInputAntenna as MTProtoIcon
} from '@mui/icons-material';

interface AdminStatusProps {
    botIsAdmin: boolean | null;
    mtprotoIsAdmin: boolean | null;
    compact?: boolean;
    message?: string;
}

export const ChannelAdminStatusIndicator: React.FC<AdminStatusProps> = ({
    botIsAdmin,
    mtprotoIsAdmin,
    compact = false,
    message
}) => {
    // Determine overall status
    const hasAtLeastOneAdmin = botIsAdmin === true || mtprotoIsAdmin === true;
    const hasBothAdmin = botIsAdmin === true && mtprotoIsAdmin === true;
    const hasNoAdmin = botIsAdmin === false && mtprotoIsAdmin === false;
    const isChecking = botIsAdmin === null && mtprotoIsAdmin === null;

    // Status for the main indicator
    const getStatus = () => {
        if (isChecking) return { color: 'default', icon: <WarningIcon />, text: 'Checking...' };
        if (hasBothAdmin) return { color: 'success', icon: <CheckCircleIcon />, text: 'Fully Configured' };
        if (hasAtLeastOneAdmin) return { color: 'warning', icon: <WarningIcon />, text: 'Partial Access' };
        return { color: 'error', icon: <ErrorIcon />, text: 'No Admin Access' };
    };

    const status = getStatus();

    // Get detailed message
    const getDetailedMessage = () => {
        if (message) return message;

        if (hasBothAdmin) {
            return '✅ Both Bot and MTProto have admin access. Data collection is fully operational.';
        }
        if (botIsAdmin && !mtprotoIsAdmin) {
            return '⚠️ Bot has admin access, but MTProto doesn\'t. Some features may be limited.';
        }
        if (!botIsAdmin && mtprotoIsAdmin) {
            return '⚠️ MTProto has admin access, but Bot doesn\'t. Some features may be limited.';
        }
        if (hasNoAdmin) {
            return '🚫 Neither Bot nor MTProto has admin access. Please add your bot/MTProto as an admin to this channel in Telegram.';
        }
        return '⏳ Admin status pending - Add your bot/MTProto as admin to enable full data collection';
    };

    if (compact) {
        // Compact version - TWO separate dots for bot and MTProto
        return (
            <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.5 }}>
                {/* Bot Status Dot */}
                <Tooltip title={`Bot: ${botIsAdmin === true ? '✅ Admin' : botIsAdmin === false ? '❌ No Access' : '⏳ Pending - Add bot as admin'}`} arrow>
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.3
                        }}
                    >
                        <BotIcon sx={{ fontSize: 12, color: 'text.secondary' }} />
                        <Box
                            sx={{
                                width: 8,
                                height: 8,
                                borderRadius: '50%',
                                bgcolor:
                                    botIsAdmin === true ? 'success.main' :
                                    botIsAdmin === false ? 'error.main' :
                                    'grey.400',
                                boxShadow: 1,
                                border: '1px solid',
                                borderColor:
                                    botIsAdmin === true ? 'success.dark' :
                                    botIsAdmin === false ? 'error.dark' :
                                    'grey.600'
                            }}
                        />
                    </Box>
                </Tooltip>

                {/* MTProto Status Dot */}
                <Tooltip title={`MTProto: ${mtprotoIsAdmin === true ? '✅ Admin' : mtprotoIsAdmin === false ? '❌ No Access' : '⏳ Pending - Connect MTProto session'}`} arrow>
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.3
                        }}
                    >
                        <MTProtoIcon sx={{ fontSize: 12, color: 'text.secondary' }} />
                        <Box
                            sx={{
                                width: 8,
                                height: 8,
                                borderRadius: '50%',
                                bgcolor:
                                    mtprotoIsAdmin === true ? 'success.main' :
                                    mtprotoIsAdmin === false ? 'error.main' :
                                    'grey.400',
                                boxShadow: 1,
                                border: '1px solid',
                                borderColor:
                                    mtprotoIsAdmin === true ? 'success.dark' :
                                    mtprotoIsAdmin === false ? 'error.dark' :
                                    'grey.600'
                            }}
                        />
                    </Box>
                </Tooltip>
            </Box>
        );
    }

    // Full version - detailed status card
    return (
        <Box sx={{ width: '100%' }}>
            <Alert
                severity={hasNoAdmin ? 'error' : hasAtLeastOneAdmin ? (hasBothAdmin ? 'success' : 'warning') : 'info'}
                icon={status.icon}
                sx={{ mb: 1 }}
            >
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                    Admin Status: {status.text}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                    {getDetailedMessage()}
                </Typography>

                {/* Individual worker status */}
                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                    <Chip
                        icon={<BotIcon />}
                        label={botIsAdmin === true ? 'Bot: Admin ✓' : botIsAdmin === false ? 'Bot: No Access' : 'Bot: Checking...'}
                        size="small"
                        color={botIsAdmin === true ? 'success' : botIsAdmin === false ? 'error' : 'default'}
                        variant={botIsAdmin === true ? 'filled' : 'outlined'}
                    />
                    <Chip
                        icon={<MTProtoIcon />}
                        label={mtprotoIsAdmin === true ? 'MTProto: Admin ✓' : mtprotoIsAdmin === false ? 'MTProto: No Access' : 'MTProto: Checking...'}
                        size="small"
                        color={mtprotoIsAdmin === true ? 'success' : mtprotoIsAdmin === false ? 'error' : 'default'}
                        variant={mtprotoIsAdmin === true ? 'filled' : 'outlined'}
                    />
                </Stack>

                {hasNoAdmin && (
                    <Box sx={{ mt: 1.5, p: 1, bgcolor: 'background.paper', borderRadius: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                            <strong>How to fix:</strong>
                        </Typography>
                        <Typography variant="caption" component="div" color="text.secondary">
                            1. Open Telegram and go to your channel<br />
                            2. Add your bot as an admin with required permissions, OR<br />
                            3. Connect your MTProto session with admin access
                        </Typography>
                    </Box>
                )}
            </Alert>
        </Box>
    );
};

export default ChannelAdminStatusIndicator;
