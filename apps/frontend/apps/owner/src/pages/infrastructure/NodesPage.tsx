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
  alpha,
  useTheme,
} from '@mui/material';
import { Refresh, CheckCircle, Warning, Terminal } from '@mui/icons-material';
import { ownerApi } from '@api/ownerApi';

interface Node {
  name: string;
  cluster: string;
  status: 'Ready' | 'NotReady' | 'Unknown';
  roles: string[];
  version: string;
  os: string;
  cpu_capacity: string;
  memory_capacity: string;
  cpu_usage: number;
  memory_usage: number;
  pods_count: number;
  age: string;
}

const NodesPage: React.FC = () => {
  const theme = useTheme();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNodes = async () => {
    setLoading(true);
    try {
      const response = await ownerApi.getNodes();
      setNodes(response.data);
    } catch (err) {
      // Mock data
      setNodes([
        { name: 'node-prod-1', cluster: 'Production EU', status: 'Ready', roles: ['master', 'control-plane'], version: 'v1.28.4', os: 'Ubuntu 22.04', cpu_capacity: '4 cores', memory_capacity: '16 GB', cpu_usage: 42, memory_usage: 58, pods_count: 8, age: '45d' },
        { name: 'node-prod-2', cluster: 'Production EU', status: 'Ready', roles: ['worker'], version: 'v1.28.4', os: 'Ubuntu 22.04', cpu_capacity: '8 cores', memory_capacity: '32 GB', cpu_usage: 55, memory_usage: 72, pods_count: 12, age: '45d' },
        { name: 'node-prod-3', cluster: 'Production EU', status: 'Ready', roles: ['worker'], version: 'v1.28.4', os: 'Ubuntu 22.04', cpu_capacity: '8 cores', memory_capacity: '32 GB', cpu_usage: 38, memory_usage: 45, pods_count: 10, age: '30d' },
        { name: 'node-staging-1', cluster: 'Staging', status: 'Ready', roles: ['master', 'worker'], version: 'v1.28.4', os: 'Ubuntu 22.04', cpu_capacity: '4 cores', memory_capacity: '8 GB', cpu_usage: 28, memory_usage: 42, pods_count: 6, age: '60d' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNodes();
  }, []);

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
            Nodes
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Kubernetes worker nodes across all clusters
          </Typography>
        </Box>
        <IconButton onClick={fetchNodes} color="primary">
          <Refresh />
        </IconButton>
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Node</TableCell>
                <TableCell>Cluster</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Roles</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>CPU</TableCell>
                <TableCell>Memory</TableCell>
                <TableCell align="center">Pods</TableCell>
                <TableCell>Age</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {nodes.map((node) => (
                <TableRow key={node.name} hover>
                  <TableCell>
                    <Typography fontWeight={600}>{node.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {node.os}
                    </Typography>
                  </TableCell>
                  <TableCell>{node.cluster}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      icon={node.status === 'Ready' ? <CheckCircle /> : <Warning />}
                      label={node.status}
                      color={node.status === 'Ready' ? 'success' : 'error'}
                    />
                  </TableCell>
                  <TableCell>
                    {node.roles.map((role) => (
                      <Chip key={role} size="small" label={role} variant="outlined" sx={{ mr: 0.5 }} />
                    ))}
                  </TableCell>
                  <TableCell>{node.version}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 50, height: 6, borderRadius: 1, bgcolor: alpha(theme.palette.primary.main, 0.2), overflow: 'hidden' }}>
                        <Box sx={{ width: `${node.cpu_usage}%`, height: '100%', bgcolor: node.cpu_usage > 80 ? 'error.main' : 'primary.main' }} />
                      </Box>
                      <Typography variant="caption">{node.cpu_usage}%</Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">{node.cpu_capacity}</Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 50, height: 6, borderRadius: 1, bgcolor: alpha(theme.palette.secondary.main, 0.2), overflow: 'hidden' }}>
                        <Box sx={{ width: `${node.memory_usage}%`, height: '100%', bgcolor: node.memory_usage > 80 ? 'error.main' : 'secondary.main' }} />
                      </Box>
                      <Typography variant="caption">{node.memory_usage}%</Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">{node.memory_capacity}</Typography>
                  </TableCell>
                  <TableCell align="center">{node.pods_count}</TableCell>
                  <TableCell>{node.age}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" title="SSH Terminal">
                      <Terminal />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
};

export default NodesPage;
