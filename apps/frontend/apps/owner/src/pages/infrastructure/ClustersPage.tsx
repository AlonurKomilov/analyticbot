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
import { Refresh, CheckCircle, Warning, Settings } from '@mui/icons-material';
import { ownerApi } from '@api/ownerApi';

interface Cluster {
  id: string;
  name: string;
  provider: string;
  region: string;
  version: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  nodes_count: number;
  pods_count: number;
  cpu_usage: number;
  memory_usage: number;
  created_at: string;
}

const ClustersPage: React.FC = () => {
  const theme = useTheme();
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchClusters = async () => {
    setLoading(true);
    try {
      const response = await ownerApi.getClusters();
      setClusters(response.data);
    } catch (err) {
      // Mock data
      setClusters([
        {
          id: 'prod-eu-1',
          name: 'Production EU',
          provider: 'Hetzner',
          region: 'eu-central',
          version: '1.28.4',
          status: 'healthy',
          nodes_count: 4,
          pods_count: 18,
          cpu_usage: 45,
          memory_usage: 62,
          created_at: '2024-01-15',
        },
        {
          id: 'staging-1',
          name: 'Staging',
          provider: 'Hetzner',
          region: 'eu-central',
          version: '1.28.4',
          status: 'healthy',
          nodes_count: 2,
          pods_count: 6,
          cpu_usage: 25,
          memory_usage: 38,
          created_at: '2024-02-20',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClusters();
  }, []);

  const getStatusChip = (status: string) => {
    const config = {
      healthy: { color: 'success', icon: <CheckCircle /> },
      degraded: { color: 'warning', icon: <Warning /> },
      unhealthy: { color: 'error', icon: <Warning /> },
    }[status] || { color: 'default', icon: null };

    return (
      <Chip
        size="small"
        icon={config.icon as React.ReactElement}
        label={status}
        color={config.color as any}
        sx={{ textTransform: 'capitalize' }}
      />
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
            Clusters
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage Kubernetes clusters
          </Typography>
        </Box>
        <IconButton onClick={fetchClusters} color="primary">
          <Refresh />
        </IconButton>
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Cluster</TableCell>
                <TableCell>Provider</TableCell>
                <TableCell>Region</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Nodes</TableCell>
                <TableCell align="center">Pods</TableCell>
                <TableCell>CPU</TableCell>
                <TableCell>Memory</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clusters.map((cluster) => (
                <TableRow key={cluster.id} hover>
                  <TableCell>
                    <Typography fontWeight={600}>{cluster.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {cluster.id}
                    </Typography>
                  </TableCell>
                  <TableCell>{cluster.provider}</TableCell>
                  <TableCell>{cluster.region}</TableCell>
                  <TableCell>
                    <Chip size="small" label={`v${cluster.version}`} variant="outlined" />
                  </TableCell>
                  <TableCell>{getStatusChip(cluster.status)}</TableCell>
                  <TableCell align="center">{cluster.nodes_count}</TableCell>
                  <TableCell align="center">{cluster.pods_count}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: 60,
                          height: 6,
                          borderRadius: 1,
                          bgcolor: alpha(theme.palette.primary.main, 0.2),
                          overflow: 'hidden',
                        }}
                      >
                        <Box
                          sx={{
                            width: `${cluster.cpu_usage}%`,
                            height: '100%',
                            bgcolor: cluster.cpu_usage > 80 ? 'error.main' : 'primary.main',
                          }}
                        />
                      </Box>
                      <Typography variant="caption">{cluster.cpu_usage}%</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: 60,
                          height: 6,
                          borderRadius: 1,
                          bgcolor: alpha(theme.palette.secondary.main, 0.2),
                          overflow: 'hidden',
                        }}
                      >
                        <Box
                          sx={{
                            width: `${cluster.memory_usage}%`,
                            height: '100%',
                            bgcolor: cluster.memory_usage > 80 ? 'error.main' : 'secondary.main',
                          }}
                        />
                      </Box>
                      <Typography variant="caption">{cluster.memory_usage}%</Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small">
                      <Settings />
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

export default ClustersPage;
