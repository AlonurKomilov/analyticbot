/**
 * Invite Tracking Configuration
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Switch,
  Alert,
  Button,
  CircularProgress,
  Divider,
  alpha,
  Card,
  CardContent,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PersonAdd as InviteIcon,
  Save as SaveIcon,
  Link as LinkIcon,
  ContentCopy as CopyIcon,
  Refresh as RefreshIcon,
  EmojiEvents as TrophyIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface InviteTrackingSettings {
  invite_tracking_enabled: boolean;
}

interface InviteLink {
  id: number;
  link: string;
  user_id: number;
  user_name: string;
  invites_count: number;
  created_at: string;
}

interface InviteLeaderboard {
  inviter_tg_id: number;
  inviter_username: string | null;
  inviter_name: string | null;
  total_invited: number;
  still_members: number;
  left_count: number;
  retention_rate: number;
}

interface Props {
  chatId: number;
}

export const InviteTrackingConfig: React.FC<Props> = ({ chatId }) => {
  const [settings, setSettings] = useState<InviteTrackingSettings>({
    invite_tracking_enabled: false,
  });
  const [inviteLinks, setInviteLinks] = useState<InviteLink[]>([]);
  const [leaderboard, setLeaderboard] = useState<InviteLeaderboard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [isNewConfig, setIsNewConfig] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [copiedLink, setCopiedLink] = useState<number | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const settingsResponse = await apiClient.get(`/user-bot/service/settings/${chatId}`) as InviteTrackingSettings;
        if (settingsResponse) {
          setSettings({
            invite_tracking_enabled: settingsResponse.invite_tracking_enabled ?? false,
          });
        }

        // Fetch invite stats if enabled
        if (settingsResponse?.invite_tracking_enabled) {
          await fetchInviteStats();
        }
      } catch (err: any) {
        // 404 means settings don't exist yet - this is normal for new chats
        if (err.message?.includes('not found') || err.status === 404) {
          setIsNewConfig(true);
        } else {
          setError(err.message || 'Failed to load settings');
        }
      } finally {
        setIsLoading(false);
      }
    };

    if (chatId) {
      fetchData();
    }
  }, [chatId]);

  const fetchInviteStats = async () => {
    setIsLoadingStats(true);
    try {
      // Invite links endpoint not available - feature coming soon
      // The backend only has invite stats/leaderboard endpoint
      setInviteLinks([]);

      // Fetch invite stats (leaderboard)
      try {
        const statsResponse = await apiClient.get(`/user-bot/service/invites/${chatId}`) as InviteLeaderboard[];
        if (Array.isArray(statsResponse)) {
          setLeaderboard(statsResponse);
        }
      } catch {
        setLeaderboard([]);
      }
    } finally {
      setIsLoadingStats(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);
    try {
      await apiClient.post(`/user-bot/service/settings/${chatId}`, settings);
      setSuccess(true);
      setIsNewConfig(false); // No longer new after first save
      setTimeout(() => setSuccess(false), 3000);
      
      if (settings.invite_tracking_enabled) {
        await fetchInviteStats();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCopyLink = (link: InviteLink) => {
    navigator.clipboard.writeText(link.link);
    setCopiedLink(link.id);
    setTimeout(() => setCopiedLink(null), 2000);
  };

  const handleExportCSV = () => {
    // Generate CSV content
    const headers = ['Rank', 'User', 'Invites', 'Still Members', 'Retention'];
    const rows = leaderboard.map((item, index) => [
      index + 1,
      item.inviter_username || item.inviter_name || `User ${item.inviter_tg_id}`,
      item.total_invited,
      item.still_members,
      `${(item.retention_rate * 100).toFixed(1)}%`
    ]);
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    
    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `invite-leaderboard-${chatId}.csv`;
    a.click();
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return rank;
    }
  };

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}
      {isNewConfig && !success && (
        <Alert severity="info" sx={{ mb: 3 }}>
          This chat hasn't been configured yet. Customize your settings and save to get started!
        </Alert>
      )}

      {/* Main Toggle */}
      <Card sx={{ mb: 3, bgcolor: alpha('#3b82f6', 0.05), border: '1px solid', borderColor: alpha('#3b82f6', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <Box
                sx={{
                  width: 50,
                  height: 50,
                  borderRadius: 2,
                  bgcolor: alpha('#3b82f6', 0.2),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <InviteIcon sx={{ color: '#3b82f6', fontSize: 28 }} />
              </Box>
              <Box>
                <Typography variant="h6">Invite Tracking</Typography>
                <Typography variant="body2" color="text.secondary">
                  Track who invited each member with unique invite links and statistics
                </Typography>
              </Box>
            </Box>
            <Switch
              checked={settings.invite_tracking_enabled}
              onChange={(e) => setSettings(prev => ({ ...prev, invite_tracking_enabled: e.target.checked }))}
              color="primary"
              size="medium"
            />
          </Box>
        </CardContent>
      </Card>

      {settings.invite_tracking_enabled && (
        <>
          {/* Leaderboard */}
          <Box mb={4}>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Typography variant="h6">
                <TrophyIcon sx={{ mr: 1, verticalAlign: 'middle', color: '#f59e0b' }} />
                Invite Leaderboard
              </Typography>
              <Box display="flex" gap={1}>
                <Button
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={fetchInviteStats}
                  disabled={isLoadingStats}
                >
                  Refresh
                </Button>
                <Button
                  size="small"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportCSV}
                  disabled={leaderboard.length === 0}
                >
                  Export CSV
                </Button>
              </Box>
            </Box>

            {isLoadingStats ? (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress size={24} />
              </Box>
            ) : leaderboard.length === 0 ? (
              <Alert severity="info">
                No invite data yet. Members will appear here as they invite new users.
              </Alert>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell width={80}>Rank</TableCell>
                      <TableCell>Member</TableCell>
                      <TableCell align="right">Invites</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {leaderboard.slice(0, 10).map((item, index) => (
                      <TableRow
                        key={item.inviter_tg_id}
                        sx={{
                          bgcolor: index < 3 ? alpha('#f59e0b', 0.05) : 'transparent',
                        }}
                      >
                        <TableCell>
                          <Typography variant="body1" fontWeight={index < 3 ? 600 : 400}>
                            {getRankIcon(index + 1)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {item.inviter_username || item.inviter_name || `User ${item.inviter_tg_id}`}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={item.total_invited}
                            size="small"
                            color={index === 0 ? 'warning' : 'default'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Active Invite Links */}
          <Box mb={4}>
            <Typography variant="h6" mb={2}>
              <LinkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Active Invite Links
            </Typography>

            {inviteLinks.length === 0 ? (
              <Alert severity="info">
                No invite links created yet. Users can create their personal invite links via the bot.
              </Alert>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Created By</TableCell>
                      <TableCell>Link</TableCell>
                      <TableCell align="center">Invites</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {inviteLinks.map((link) => (
                      <TableRow key={link.id}>
                        <TableCell>
                          <Typography variant="body2">{link.user_name}</Typography>
                        </TableCell>
                        <TableCell>
                          <Typography
                            variant="body2"
                            sx={{
                              fontFamily: 'monospace',
                              maxWidth: 200,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                            }}
                          >
                            {link.link}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Chip label={link.invites_count} size="small" />
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title={copiedLink === link.id ? 'Copied!' : 'Copy Link'}>
                            <IconButton size="small" onClick={() => handleCopyLink(link)}>
                              <CopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        </>
      )}

      {/* Save Button */}
      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
          size="large"
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};
