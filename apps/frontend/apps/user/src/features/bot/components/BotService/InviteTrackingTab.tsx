/**
 * Invite Tracking Tab Component
 * Display invite statistics and leaderboard
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Divider,
  Chip,
  Grid,
  Card,
  CardContent,
  Avatar,
  Button,
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  Person as PersonIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

import { useModerationStore } from '@/store';

interface InviteTrackingTabProps {
  chatId: number;
}

export const InviteTrackingTab: React.FC<InviteTrackingTabProps> = ({ chatId }) => {
  const {
    settings,
    inviteStats,
    isLoadingInvites,
    fetchInviteStats,
  } = useModerationStore();

  if (!settings?.invite_tracking_enabled) {
    return (
      <Alert severity="warning">
        <Typography variant="body1">
          <strong>Invite Tracking is disabled.</strong>
        </Typography>
        <Typography variant="body2">
          Enable "Invite Tracking" in the Settings tab to use this feature.
        </Typography>
      </Alert>
    );
  }

  if (isLoadingInvites) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  const getRankColor = (index: number) => {
    switch (index) {
      case 0:
        return '#FFD700'; // Gold
      case 1:
        return '#C0C0C0'; // Silver
      case 2:
        return '#CD7F32'; // Bronze
      default:
        return 'inherit';
    }
  };

  const getRankEmoji = (index: number) => {
    switch (index) {
      case 0:
        return '🥇';
      case 1:
        return '🥈';
      case 2:
        return '🥉';
      default:
        return `#${index + 1}`;
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Invite Tracking Statistics</Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => fetchInviteStats(chatId)}
          disabled={isLoadingInvites}
        >
          Refresh
        </Button>
      </Box>

      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <PersonIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">
                    {inviteStats?.total_invites || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Invites
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <TrendingUpIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">
                    {inviteStats?.active_members_invited || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Still Members
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <TrendingDownIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">
                    {(inviteStats?.total_invites || 0) - (inviteStats?.active_members_invited || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Left Chat
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Leaderboard */}
      <Paper sx={{ p: 3 }}>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <TrophyIcon color="primary" />
          <Typography variant="h6">Invite Leaderboard</Typography>
        </Box>
        <Divider sx={{ mb: 2 }} />

        {!inviteStats?.leaderboard || inviteStats.leaderboard.length === 0 ? (
          <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
            No invite data yet. When users invite others, they'll appear here.
          </Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell width={60}>Rank</TableCell>
                  <TableCell>Inviter</TableCell>
                  <TableCell align="center">Total Invited</TableCell>
                  <TableCell align="center">Still Members</TableCell>
                  <TableCell align="center">Left</TableCell>
                  <TableCell align="center">Retention</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {inviteStats.leaderboard.map((inviter, index) => {
                  const retention = inviter.total_invited > 0
                    ? Math.round((inviter.still_members / inviter.total_invited) * 100)
                    : 0;

                  return (
                    <TableRow
                      key={inviter.inviter_tg_id}
                      sx={{
                        backgroundColor: index < 3 ? `${getRankColor(index)}10` : 'inherit',
                      }}
                    >
                      <TableCell>
                        <Typography
                          variant="h6"
                          sx={{ color: getRankColor(index) }}
                        >
                          {getRankEmoji(index)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body1">
                            {inviter.inviter_name || 'Unknown'}
                          </Typography>
                          {inviter.inviter_username && (
                            <Typography variant="caption" color="text.secondary">
                              @{inviter.inviter_username}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={inviter.total_invited}
                          color="primary"
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={inviter.still_members}
                          color="success"
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={inviter.left_members}
                          color="error"
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={`${retention}%`}
                          color={retention >= 70 ? 'success' : retention >= 40 ? 'warning' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
};

export default InviteTrackingTab;
