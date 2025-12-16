/**
 * Moderation Log Tab Component
 * Display history of moderation actions
 */

import React, { useState } from 'react';
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
  TablePagination,
  CircularProgress,
  Chip,
  Button,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Warning as WarningIcon,
  Block as BlockIcon,
  VolumeOff as MuteIcon,
  ExitToApp as KickIcon,
} from '@mui/icons-material';

import { useModerationStore } from '@/store';
import type { ModerationAction } from '@/types';

interface ModerationLogTabProps {
  chatId: number;
}

const getActionIcon = (action: ModerationAction) => {
  switch (action) {
    case 'delete':
      return <DeleteIcon fontSize="small" />;
    case 'warn':
      return <WarningIcon fontSize="small" />;
    case 'mute':
      return <MuteIcon fontSize="small" />;
    case 'kick':
      return <KickIcon fontSize="small" />;
    case 'ban':
      return <BlockIcon fontSize="small" />;
    default:
      return undefined;
  }
};

const getActionColor = (action: ModerationAction): 'default' | 'warning' | 'error' | 'info' => {
  switch (action) {
    case 'delete':
      return 'default';
    case 'warn':
      return 'warning';
    case 'mute':
      return 'info';
    case 'kick':
      return 'warning';
    case 'ban':
      return 'error';
    default:
      return 'default';
  }
};

export const ModerationLogTab: React.FC<ModerationLogTabProps> = ({ chatId }) => {
  const {
    moderationLog,
    isLoadingLog,
    fetchModerationLog,
  } = useModerationStore();

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
    fetchModerationLog(chatId, newPage + 1);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const truncateText = (text: string | null, maxLength: number = 50) => {
    if (!text) return '-';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Moderation Activity Log</Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => fetchModerationLog(chatId, page + 1)}
          disabled={isLoadingLog}
        >
          Refresh
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        {isLoadingLog ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : !moderationLog?.logs || moderationLog.logs.length === 0 ? (
          <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
            No moderation actions recorded yet.
          </Typography>
        ) : (
          <>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell>Action</TableCell>
                    <TableCell>Target User</TableCell>
                    <TableCell>Reason</TableCell>
                    <TableCell>Message Content</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {moderationLog.logs.map((entry) => (
                    <TableRow key={entry.id} hover>
                      <TableCell>
                        <Typography variant="caption">
                          {formatDate(entry.created_at)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getActionIcon(entry.action)}
                          label={entry.action.toUpperCase()}
                          size="small"
                          color={getActionColor(entry.action)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">
                            {entry.target_name || 'Unknown'}
                          </Typography>
                          {entry.target_username && (
                            <Typography variant="caption" color="text.secondary">
                              @{entry.target_username}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Tooltip title={entry.reason || 'No reason specified'}>
                          <Typography variant="body2">
                            {truncateText(entry.reason, 30)}
                          </Typography>
                        </Tooltip>
                      </TableCell>
                      <TableCell>
                        <Tooltip title={entry.message_content || 'No content'}>
                          <Typography
                            variant="body2"
                            sx={{
                              maxWidth: 200,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {truncateText(entry.message_content, 40)}
                          </Typography>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              component="div"
              count={moderationLog.total}
              page={page}
              onPageChange={handleChangePage}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              rowsPerPageOptions={[10, 20, 50]}
            />
          </>
        )}
      </Paper>
    </Box>
  );
};

export default ModerationLogTab;
