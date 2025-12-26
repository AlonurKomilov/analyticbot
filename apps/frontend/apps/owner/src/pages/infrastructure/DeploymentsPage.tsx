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
  Button,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { Refresh, MoreVert, ScaleOutlined, RestartAlt, CheckCircle, Schedule } from '@mui/icons-material';
import { ownerApi } from '@api/ownerApi';
import toast from 'react-hot-toast';

interface Deployment {
  name: string;
  namespace: string;
  replicas: { desired: number; ready: number; available: number };
  image: string;
  status: 'Available' | 'Progressing' | 'Degraded';
  age: string;
  last_updated: string;
}

const DeploymentsPage: React.FC = () => {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedDeployment, setSelectedDeployment] = useState<Deployment | null>(null);
  const [scaleDialogOpen, setScaleDialogOpen] = useState(false);
  const [newReplicas, setNewReplicas] = useState(1);

  const fetchDeployments = async () => {
    setLoading(true);
    try {
      const response = await ownerApi.getDeployments();
      setDeployments(response.data);
    } catch (err) {
      // Mock data
      setDeployments([
        { name: 'api-server', namespace: 'analyticbot', replicas: { desired: 3, ready: 3, available: 3 }, image: 'analyticbot/api:v2.1.0', status: 'Available', age: '15d', last_updated: '2h ago' },
        { name: 'bot-worker', namespace: 'analyticbot', replicas: { desired: 2, ready: 2, available: 2 }, image: 'analyticbot/bot:v2.1.0', status: 'Available', age: '15d', last_updated: '2h ago' },
        { name: 'celery-worker', namespace: 'analyticbot', replicas: { desired: 4, ready: 4, available: 4 }, image: 'analyticbot/celery:v2.1.0', status: 'Available', age: '15d', last_updated: '6h ago' },
        { name: 'mtproto-service', namespace: 'analyticbot', replicas: { desired: 2, ready: 2, available: 2 }, image: 'analyticbot/mtproto:v2.1.0', status: 'Available', age: '10d', last_updated: '1d ago' },
        { name: 'frontend-user', namespace: 'analyticbot', replicas: { desired: 2, ready: 2, available: 2 }, image: 'analyticbot/frontend:v2.1.0', status: 'Available', age: '5d', last_updated: '3h ago' },
        { name: 'frontend-admin', namespace: 'analyticbot', replicas: { desired: 1, ready: 1, available: 1 }, image: 'analyticbot/admin:v2.1.0', status: 'Available', age: '5d', last_updated: '3h ago' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeployments();
  }, []);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, deployment: Deployment) => {
    setAnchorEl(event.currentTarget);
    setSelectedDeployment(deployment);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleScale = () => {
    if (selectedDeployment) {
      setNewReplicas(selectedDeployment.replicas.desired);
      setScaleDialogOpen(true);
    }
    handleMenuClose();
  };

  const handleScaleSubmit = async () => {
    if (selectedDeployment) {
      try {
        await ownerApi.scaleDeployment(selectedDeployment.namespace, selectedDeployment.name, newReplicas);
        toast.success(`Scaled ${selectedDeployment.name} to ${newReplicas} replicas`);
        fetchDeployments();
      } catch (err) {
        toast.error('Failed to scale deployment');
      }
    }
    setScaleDialogOpen(false);
  };

  const handleRestart = async () => {
    if (selectedDeployment) {
      try {
        await ownerApi.restartDeployment(selectedDeployment.namespace, selectedDeployment.name);
        toast.success(`Restarting ${selectedDeployment.name}`);
        fetchDeployments();
      } catch (err) {
        toast.error('Failed to restart deployment');
      }
    }
    handleMenuClose();
  };

  const getStatusChip = (_status: string, replicas: { desired: number; ready: number }) => {
    if (replicas.ready < replicas.desired) {
      return <Chip size="small" icon={<Schedule />} label="Progressing" color="warning" />;
    }
    return <Chip size="small" icon={<CheckCircle />} label="Available" color="success" />;
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
            Deployments
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Kubernetes deployments and scaling
          </Typography>
        </Box>
        <IconButton onClick={fetchDeployments} color="primary">
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
                <TableCell>Status</TableCell>
                <TableCell align="center">Replicas</TableCell>
                <TableCell>Image</TableCell>
                <TableCell>Age</TableCell>
                <TableCell>Updated</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {deployments.map((deployment) => (
                <TableRow key={`${deployment.namespace}-${deployment.name}`} hover>
                  <TableCell>
                    <Typography fontWeight={600}>{deployment.name}</Typography>
                  </TableCell>
                  <TableCell>
                    <Chip size="small" label={deployment.namespace} variant="outlined" />
                  </TableCell>
                  <TableCell>{getStatusChip(deployment.status, deployment.replicas)}</TableCell>
                  <TableCell align="center">
                    <Typography fontWeight={600}>
                      {deployment.replicas.ready}/{deployment.replicas.desired}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {deployment.image}
                    </Typography>
                  </TableCell>
                  <TableCell>{deployment.age}</TableCell>
                  <TableCell>{deployment.last_updated}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={(e) => handleMenuOpen(e, deployment)}>
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
        <MenuItem onClick={handleScale}>
          <ScaleOutlined sx={{ mr: 1 }} /> Scale
        </MenuItem>
        <MenuItem onClick={handleRestart}>
          <RestartAlt sx={{ mr: 1 }} /> Restart
        </MenuItem>
      </Menu>

      {/* Scale Dialog */}
      <Dialog open={scaleDialogOpen} onClose={() => setScaleDialogOpen(false)}>
        <DialogTitle>Scale Deployment</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Scale {selectedDeployment?.name} to a new replica count
          </Typography>
          <TextField
            fullWidth
            type="number"
            label="Replicas"
            value={newReplicas}
            onChange={(e) => setNewReplicas(parseInt(e.target.value) || 0)}
            inputProps={{ min: 0, max: 20 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScaleDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleScaleSubmit} variant="contained">
            Scale
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DeploymentsPage;
