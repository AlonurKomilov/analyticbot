import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  CircularProgress,
  Menu,
  MenuItem,
} from '@mui/material';
import { Refresh, MoreVert, Delete, Article, Terminal, CheckCircle, Warning, Schedule, Error as ErrorIcon } from '@mui/icons-material';
import { ownerApi } from '@api/ownerApi';
import toast from 'react-hot-toast';

interface Pod {
  name: string;
  namespace: string;
  node: string;
  status: 'Running' | 'Pending' | 'Failed' | 'Succeeded' | 'Unknown';
  restarts: number;
  cpu: string;
  memory: string;
  age: string;
  ip: string;
}

const PodsPage: React.FC = () => {
  const [pods, setPods] = useState<Pod[]>([]);
  const [loading, setLoading] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedPod, setSelectedPod] = useState<Pod | null>(null);

  const fetchPods = async () => {
    setLoading(true);
    try {
      const response = await ownerApi.getPods();
      setPods(response.data);
    } catch (err) {
      // Mock data
      setPods([
        { name: 'api-server-7d8f9b6c5d-abc12', namespace: 'analyticbot', node: 'node-prod-2', status: 'Running', restarts: 0, cpu: '125m', memory: '256Mi', age: '2d', ip: '10.244.1.15' },
        { name: 'api-server-7d8f9b6c5d-def34', namespace: 'analyticbot', node: 'node-prod-3', status: 'Running', restarts: 0, cpu: '118m', memory: '248Mi', age: '2d', ip: '10.244.2.22' },
        { name: 'bot-worker-5f7d8c9b4e-ghi56', namespace: 'analyticbot', node: 'node-prod-2', status: 'Running', restarts: 1, cpu: '85m', memory: '192Mi', age: '5d', ip: '10.244.1.18' },
        { name: 'celery-worker-6c8d9e7f5a-jkl78', namespace: 'analyticbot', node: 'node-prod-2', status: 'Running', restarts: 0, cpu: '200m', memory: '512Mi', age: '3d', ip: '10.244.1.25' },
        { name: 'celery-worker-6c8d9e7f5a-mno90', namespace: 'analyticbot', node: 'node-prod-3', status: 'Running', restarts: 0, cpu: '195m', memory: '498Mi', age: '3d', ip: '10.244.2.30' },
        { name: 'mtproto-service-4b6c7d8e9f-pqr12', namespace: 'analyticbot', node: 'node-prod-2', status: 'Running', restarts: 0, cpu: '150m', memory: '384Mi', age: '10d', ip: '10.244.1.35' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPods();
  }, []);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, pod: Pod) => {
    setAnchorEl(event.currentTarget);
    setSelectedPod(pod);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleDelete = async () => {
    if (selectedPod) {
      try {
        await ownerApi.deletePod(selectedPod.namespace, selectedPod.name);
        toast.success(`Pod ${selectedPod.name} deleted`);
        fetchPods();
      } catch (err) {
        toast.error('Failed to delete pod');
      }
    }
    handleMenuClose();
  };

  const getStatusChip = (status: string, restarts: number) => {
    const config: Record<string, { color: any; icon: React.ReactElement }> = {
      Running: { color: 'success', icon: <CheckCircle /> },
      Pending: { color: 'warning', icon: <Schedule /> },
      Failed: { color: 'error', icon: <ErrorIcon /> },
      Succeeded: { color: 'info', icon: <CheckCircle /> },
      Unknown: { color: 'default', icon: <Warning /> },
    };
    const c = config[status] || config.Unknown;
    
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Chip size="small" icon={c.icon} label={status} color={c.color} />
        {restarts > 0 && (
          <Chip size="small" label={`${restarts} restarts`} color="warning" variant="outlined" />
        )}
      </Box>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Pods
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Running container instances
          </Typography>
        </Box>
        <IconButton onClick={fetchPods} color="primary">
          <Refresh />
        </IconButton>
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Namespace</TableCell>
                <TableCell>Node</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>CPU</TableCell>
                <TableCell>Memory</TableCell>
                <TableCell>IP</TableCell>
                <TableCell>Age</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pods.map((pod) => (
                <TableRow key={pod.name} hover>
                  <TableCell>
                    <Typography fontWeight={600} sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                      {pod.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip size="small" label={pod.namespace} variant="outlined" />
                  </TableCell>
                  <TableCell>{pod.node}</TableCell>
                  <TableCell>{getStatusChip(pod.status, pod.restarts)}</TableCell>
                  <TableCell>{pod.cpu}</TableCell>
                  <TableCell>{pod.memory}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{pod.ip}</TableCell>
                  <TableCell>{pod.age}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={(e) => handleMenuOpen(e, pod)}>
                      <MoreVert />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Actions Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleMenuClose}>
          <Article sx={{ mr: 1 }} /> View Logs
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <Terminal sx={{ mr: 1 }} /> Exec Shell
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <Delete sx={{ mr: 1 }} /> Delete
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default PodsPage;
