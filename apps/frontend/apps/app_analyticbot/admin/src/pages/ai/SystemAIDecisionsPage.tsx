/**
 * System AI Decisions Page
 * 
 * Review and approve AI decisions:
 * - Pending decisions
 * - Decision history
 * - Approval workflow
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid2 as Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  alpha,
  useTheme,
  IconButton,
  Tooltip,
  Divider,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Skeleton,
  Alert,
  Tab,
  Tabs,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Visibility as ViewIcon,
  History as HistoryIcon,
  Warning as PendingIcon,
  PlayArrow as ExecuteIcon,
  Undo as RollbackIcon,
  Info as InfoIcon,
  TrendingUp as ScaleIcon,
  Settings as ConfigIcon,
  Security as SecurityIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';

interface Decision {
  id: string;
  type: 'scale_up' | 'scale_down' | 'config_change' | 'health_action' | 'security_action';
  priority: 'high' | 'medium' | 'low';
  target_worker: string;
  description: string;
  reasoning: string;
  parameters: Record<string, any>;
  status: 'pending' | 'approved' | 'rejected' | 'executed' | 'rolled_back';
  created_at: string;
  decided_at?: string;
  decided_by?: string;
  execution_result?: string;
  can_rollback: boolean;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div role="tabpanel" hidden={value !== index}>
    {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
  </div>
);

const SystemAIDecisionsPage: React.FC = () => {
  const theme = useTheme();
  
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDecisions = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setDecisions([
          {
            id: '1',
            type: 'scale_up',
            priority: 'high',
            target_worker: 'MTProto Pool',
            description: 'Scale MTProto workers from 3 to 5 instances',
            reasoning: 'Current load at 85%, projected to exceed capacity in 30 minutes based on traffic patterns.',
            parameters: { current_instances: 3, target_instances: 5, trigger: 'high_load' },
            status: 'pending',
            created_at: new Date().toISOString(),
            can_rollback: true,
          },
          {
            id: '2',
            type: 'config_change',
            priority: 'medium',
            target_worker: 'API Server',
            description: 'Increase rate limit from 100 to 150 requests/minute',
            reasoning: 'Several legitimate users hitting rate limits. No abuse pattern detected.',
            parameters: { old_limit: 100, new_limit: 150, affected_endpoints: ['/api/v1/*'] },
            status: 'pending',
            created_at: new Date(Date.now() - 1800000).toISOString(),
            can_rollback: true,
          },
          {
            id: '3',
            type: 'health_action',
            priority: 'low',
            target_worker: 'Celery Workers',
            description: 'Clear stale tasks from queue',
            reasoning: 'Detected 47 tasks older than 1 hour in queue. Likely stuck or abandoned.',
            parameters: { task_count: 47, age_threshold_minutes: 60 },
            status: 'approved',
            created_at: new Date(Date.now() - 3600000).toISOString(),
            decided_at: new Date(Date.now() - 3300000).toISOString(),
            decided_by: 'admin@example.com',
            can_rollback: false,
          },
          {
            id: '4',
            type: 'scale_down',
            priority: 'low',
            target_worker: 'Bot Handler',
            description: 'Scale down from 4 to 2 instances',
            reasoning: 'Low traffic period detected. Average utilization below 20% for past 2 hours.',
            parameters: { current_instances: 4, target_instances: 2, trigger: 'low_load' },
            status: 'executed',
            created_at: new Date(Date.now() - 7200000).toISOString(),
            decided_at: new Date(Date.now() - 7000000).toISOString(),
            decided_by: 'auto',
            execution_result: 'Successfully scaled down. Saved $0.50/hour.',
            can_rollback: true,
          },
          {
            id: '5',
            type: 'security_action',
            priority: 'high',
            target_worker: 'API Server',
            description: 'Block suspicious IP range',
            reasoning: 'Detected potential DDoS pattern from 192.168.1.0/24. 500+ requests in 1 minute.',
            parameters: { ip_range: '192.168.1.0/24', duration_hours: 24 },
            status: 'rejected',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            decided_at: new Date(Date.now() - 85000000).toISOString(),
            decided_by: 'admin@example.com',
            can_rollback: false,
          },
        ]);
      } catch (err) {
        setError('Failed to load decisions');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDecisions();
  }, []);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'scale_up':
      case 'scale_down':
        return <ScaleIcon />;
      case 'config_change':
        return <ConfigIcon />;
      case 'health_action':
        return <ScheduleIcon />;
      case 'security_action':
        return <SecurityIcon />;
      default:
        return <InfoIcon />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'approved': return 'info';
      case 'rejected': return 'error';
      case 'executed': return 'success';
      case 'rolled_back': return 'default';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const handleApprove = async (decisionId: string) => {
    // TODO: API call
    setDecisions(prev => prev.map(d => 
      d.id === decisionId ? { ...d, status: 'approved' as const, decided_at: new Date().toISOString(), decided_by: 'admin' } : d
    ));
  };

  const handleReject = async (decisionId: string) => {
    // TODO: API call
    setDecisions(prev => prev.map(d => 
      d.id === decisionId ? { ...d, status: 'rejected' as const, decided_at: new Date().toISOString(), decided_by: 'admin' } : d
    ));
    setDetailsDialogOpen(false);
    setRejectReason('');
  };

  const handleExecute = async (decisionId: string) => {
    // TODO: API call
    setDecisions(prev => prev.map(d => 
      d.id === decisionId ? { ...d, status: 'executed' as const } : d
    ));
  };

  const handleRollback = async (decisionId: string) => {
    // TODO: API call
    setDecisions(prev => prev.map(d => 
      d.id === decisionId ? { ...d, status: 'rolled_back' as const } : d
    ));
  };

  const pendingDecisions = decisions.filter(d => d.status === 'pending');
  const historyDecisions = decisions.filter(d => d.status !== 'pending');

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="text" width={300} height={40} />
        <Skeleton variant="rounded" height={400} sx={{ mt: 3 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" fontWeight={700} gutterBottom>
          AI Decisions
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Review, approve, and track AI system decisions
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Summary */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[
          { label: 'Pending Review', value: pendingDecisions.length, color: theme.palette.warning.main },
          { label: 'Approved Today', value: decisions.filter(d => d.status === 'approved').length, color: theme.palette.info.main },
          { label: 'Executed', value: decisions.filter(d => d.status === 'executed').length, color: theme.palette.success.main },
          { label: 'Rejected', value: decisions.filter(d => d.status === 'rejected').length, color: theme.palette.error.main },
        ].map((stat) => (
          <Grid size={{ xs: 6, md: 3 }} key={stat.label}>
            <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h3" fontWeight={700} sx={{ color: stat.color }}>
                  {stat.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {stat.label}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Tabs */}
      <Paper sx={{ border: `1px solid ${theme.palette.divider}` }}>
        <Tabs
          value={activeTab}
          onChange={(_, v) => setActiveTab(v)}
          sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
        >
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                Pending Review
                {pendingDecisions.length > 0 && (
                  <Chip label={pendingDecisions.length} size="small" color="warning" />
                )}
              </Box>
            }
          />
          <Tab label="History" />
        </Tabs>

        {/* Pending Tab */}
        <TabPanel value={activeTab} index={0}>
          {pendingDecisions.length === 0 ? (
            <Box sx={{ p: 6, textAlign: 'center' }}>
              <ApproveIcon sx={{ fontSize: 64, color: theme.palette.success.main, mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                No pending decisions
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All AI decisions have been reviewed
              </Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Decision</TableCell>
                    <TableCell>Target</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {pendingDecisions.map((decision) => (
                    <TableRow key={decision.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Box
                            sx={{
                              p: 1,
                              borderRadius: 1,
                              bgcolor: alpha(theme.palette.primary.main, 0.1),
                              color: theme.palette.primary.main,
                            }}
                          >
                            {getTypeIcon(decision.type)}
                          </Box>
                          <Box>
                            <Typography variant="subtitle2" fontWeight={600}>
                              {decision.description}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {decision.type.replace('_', ' ')}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>{decision.target_worker}</TableCell>
                      <TableCell>
                        <Chip
                          label={decision.priority}
                          size="small"
                          color={getPriorityColor(decision.priority) as any}
                        />
                      </TableCell>
                      <TableCell>{formatDate(decision.created_at)}</TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedDecision(decision);
                                setDetailsDialogOpen(true);
                              }}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Approve">
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => handleApprove(decision.id)}
                            >
                              <ApproveIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Reject">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => {
                                setSelectedDecision(decision);
                                setDetailsDialogOpen(true);
                              }}
                            >
                              <RejectIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </TabPanel>

        {/* History Tab */}
        <TabPanel value={activeTab} index={1}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Decision</TableCell>
                  <TableCell>Target</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Decided By</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {historyDecisions.map((decision) => (
                  <TableRow key={decision.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Box
                          sx={{
                            p: 1,
                            borderRadius: 1,
                            bgcolor: alpha(theme.palette.grey[500], 0.1),
                          }}
                        >
                          {getTypeIcon(decision.type)}
                        </Box>
                        <Typography variant="body2">
                          {decision.description}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{decision.target_worker}</TableCell>
                    <TableCell>
                      <Chip
                        label={decision.status}
                        size="small"
                        color={getStatusColor(decision.status) as any}
                      />
                    </TableCell>
                    <TableCell>{decision.decided_by || '-'}</TableCell>
                    <TableCell>{decision.decided_at ? formatDate(decision.decided_at) : '-'}</TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedDecision(decision);
                              setDetailsDialogOpen(true);
                            }}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        {decision.status === 'approved' && (
                          <Tooltip title="Execute Now">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleExecute(decision.id)}
                            >
                              <ExecuteIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        {decision.status === 'executed' && decision.can_rollback && (
                          <Tooltip title="Rollback">
                            <IconButton
                              size="small"
                              color="warning"
                              onClick={() => handleRollback(decision.id)}
                            >
                              <RollbackIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Paper>

      {/* Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Decision Details</DialogTitle>
        <DialogContent>
          {selectedDecision && (
            <Box sx={{ pt: 1 }}>
              <Typography variant="h6" gutterBottom>
                {selectedDecision.description}
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip
                  label={selectedDecision.type.replace('_', ' ')}
                  size="small"
                  variant="outlined"
                />
                <Chip
                  label={selectedDecision.priority}
                  size="small"
                  color={getPriorityColor(selectedDecision.priority) as any}
                />
                <Chip
                  label={selectedDecision.status}
                  size="small"
                  color={getStatusColor(selectedDecision.status) as any}
                />
              </Box>
              
              <Typography variant="subtitle2" gutterBottom>
                AI Reasoning:
              </Typography>
              <Paper sx={{ p: 2, mb: 2, bgcolor: alpha(theme.palette.info.main, 0.05) }}>
                <Typography variant="body2">
                  {selectedDecision.reasoning}
                </Typography>
              </Paper>
              
              <Typography variant="subtitle2" gutterBottom>
                Parameters:
              </Typography>
              <Paper sx={{ p: 2, mb: 2, bgcolor: theme.palette.grey[50] }}>
                <pre style={{ margin: 0, fontSize: '0.85rem' }}>
                  {JSON.stringify(selectedDecision.parameters, null, 2)}
                </pre>
              </Paper>
              
              {selectedDecision.status === 'pending' && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    label="Rejection Reason (optional)"
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                    placeholder="Why are you rejecting this decision?"
                  />
                </>
              )}
              
              {selectedDecision.execution_result && (
                <>
                  <Typography variant="subtitle2" gutterBottom>
                    Execution Result:
                  </Typography>
                  <Alert severity="success">
                    {selectedDecision.execution_result}
                  </Alert>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>
            Close
          </Button>
          {selectedDecision?.status === 'pending' && (
            <>
              <Button
                color="error"
                onClick={() => handleReject(selectedDecision.id)}
              >
                Reject
              </Button>
              <Button
                variant="contained"
                color="success"
                onClick={() => {
                  handleApprove(selectedDecision.id);
                  setDetailsDialogOpen(false);
                }}
              >
                Approve
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SystemAIDecisionsPage;
