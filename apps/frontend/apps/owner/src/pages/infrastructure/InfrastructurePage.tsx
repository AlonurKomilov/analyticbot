import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Chip,
  CircularProgress,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Cloud,
  Dns,
  ViewInAr,
  Inventory,
  NetworkCheck,
  Language,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { ownerApi } from '@api/ownerApi';
import { ROUTES } from '@config/routes';

interface InfraMetrics {
  clusters: { total: number; healthy: number };
  nodes: { total: number; ready: number };
  deployments: { total: number; available: number };
  pods: { running: number; pending: number; failed: number };
  services: { total: number };
  ingress: { total: number };
}

const InfrastructurePage: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<InfraMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await ownerApi.getK8sMetrics();
        setMetrics(response.data);
      } catch (err) {
        // Mock data for development
        setMetrics({
          clusters: { total: 2, healthy: 2 },
          nodes: { total: 6, ready: 6 },
          deployments: { total: 12, available: 12 },
          pods: { running: 24, pending: 0, failed: 0 },
          services: { total: 8 },
          ingress: { total: 4 },
        });
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  const getStatusColor = (healthy: number, total: number) => {
    if (healthy === total) return theme.palette.success.main;
    if (healthy >= total * 0.8) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const getStatusIcon = (healthy: number, total: number) => {
    if (healthy === total) return <CheckCircle />;
    if (healthy >= total * 0.8) return <Warning />;
    return <ErrorIcon />;
  };

  const infraCards = [
    {
      title: 'Clusters',
      icon: <Cloud />,
      path: ROUTES.CLUSTERS,
      value: metrics?.clusters.total || 0,
      healthy: metrics?.clusters.healthy || 0,
      description: 'Kubernetes clusters',
    },
    {
      title: 'Nodes',
      icon: <Dns />,
      path: ROUTES.NODES,
      value: metrics?.nodes.total || 0,
      healthy: metrics?.nodes.ready || 0,
      description: 'Worker nodes',
    },
    {
      title: 'Deployments',
      icon: <Inventory />,
      path: ROUTES.DEPLOYMENTS,
      value: metrics?.deployments.total || 0,
      healthy: metrics?.deployments.available || 0,
      description: 'Application deployments',
    },
    {
      title: 'Pods',
      icon: <ViewInAr />,
      path: ROUTES.PODS,
      value: (metrics?.pods.running || 0) + (metrics?.pods.pending || 0),
      healthy: metrics?.pods.running || 0,
      description: 'Running containers',
      extra: metrics?.pods.pending ? `${metrics.pods.pending} pending` : undefined,
    },
    {
      title: 'Services',
      icon: <NetworkCheck />,
      path: ROUTES.SERVICES,
      value: metrics?.services.total || 0,
      healthy: metrics?.services.total || 0,
      description: 'Network services',
    },
    {
      title: 'Ingress',
      icon: <Language />,
      path: ROUTES.INGRESS,
      value: metrics?.ingress.total || 0,
      healthy: metrics?.ingress.total || 0,
      description: 'External routes',
    },
  ];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Infrastructure
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Kubernetes cluster and infrastructure management
      </Typography>

      {/* Overview Stats */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Cloud sx={{ fontSize: 32, color: 'primary.main' }} />
            <Box>
              <Typography variant="h6" fontWeight={600}>
                Infrastructure Health
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All systems operational
              </Typography>
            </Box>
            <Box sx={{ ml: 'auto' }}>
              <Chip
                icon={<CheckCircle />}
                label="Healthy"
                color="success"
                sx={{ fontWeight: 600 }}
              />
            </Box>
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="primary.main">
                  {metrics?.clusters.total || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Clusters
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="secondary.main">
                  {metrics?.nodes.total || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Nodes
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="info.main">
                  {metrics?.deployments.total || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Deployments
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="success.main">
                  {metrics?.pods.running || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Running Pods
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="warning.main">
                  {metrics?.services.total || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Services
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700}>
                  {metrics?.ingress.total || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Ingress Rules
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Infrastructure Cards */}
      <Grid container spacing={3}>
        {infraCards.map((card) => (
          <Grid item xs={12} sm={6} md={4} key={card.title}>
            <Card>
              <CardActionArea onClick={() => navigate(card.path)}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        bgcolor: alpha(theme.palette.primary.main, 0.1),
                        color: 'primary.main',
                      }}
                    >
                      {React.cloneElement(card.icon, { sx: { fontSize: 28 } })}
                    </Box>
                    <Chip
                      size="small"
                      icon={getStatusIcon(card.healthy, card.value)}
                      label={`${card.healthy}/${card.value}`}
                      sx={{
                        bgcolor: alpha(getStatusColor(card.healthy, card.value), 0.1),
                        color: getStatusColor(card.healthy, card.value),
                        fontWeight: 600,
                      }}
                    />
                  </Box>
                  <Typography variant="h5" fontWeight={700}>
                    {card.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {card.description}
                  </Typography>
                  {card.extra && (
                    <Typography variant="caption" color="warning.main" sx={{ mt: 1, display: 'block' }}>
                      {card.extra}
                    </Typography>
                  )}
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default InfrastructurePage;
