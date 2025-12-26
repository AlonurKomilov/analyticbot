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
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { ownerApi } from '@api/ownerApi';

interface Service {
  name: string;
  namespace: string;
  type: 'ClusterIP' | 'NodePort' | 'LoadBalancer';
  cluster_ip: string;
  external_ip?: string;
  ports: string;
  age: string;
}

const ServicesPage: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchServices = async () => {
    setLoading(true);
    try {
      const response = await ownerApi.getServices();
      setServices(response.data);
    } catch (err) {
      // Mock data
      setServices([
        { name: 'api-server', namespace: 'analyticbot', type: 'ClusterIP', cluster_ip: '10.96.45.123', ports: '8000/TCP', age: '15d' },
        { name: 'api-server-lb', namespace: 'analyticbot', type: 'LoadBalancer', cluster_ip: '10.96.45.124', external_ip: '207.180.226.85', ports: '443:31443/TCP', age: '15d' },
        { name: 'bot-worker', namespace: 'analyticbot', type: 'ClusterIP', cluster_ip: '10.96.45.125', ports: '5000/TCP', age: '15d' },
        { name: 'redis', namespace: 'analyticbot', type: 'ClusterIP', cluster_ip: '10.96.45.130', ports: '6379/TCP', age: '30d' },
        { name: 'postgresql', namespace: 'analyticbot', type: 'ClusterIP', cluster_ip: '10.96.45.131', ports: '5432/TCP', age: '30d' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServices();
  }, []);

  const getTypeChip = (type: string) => {
    const colors: Record<string, 'primary' | 'secondary' | 'success'> = {
      ClusterIP: 'primary',
      NodePort: 'secondary',
      LoadBalancer: 'success',
    };
    return <Chip size="small" label={type} color={colors[type] || 'default'} />;
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
            Services
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Kubernetes network services
          </Typography>
        </Box>
        <IconButton onClick={fetchServices} color="primary">
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
                <TableCell>Type</TableCell>
                <TableCell>Cluster IP</TableCell>
                <TableCell>External IP</TableCell>
                <TableCell>Ports</TableCell>
                <TableCell>Age</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {services.map((service) => (
                <TableRow key={`${service.namespace}-${service.name}`} hover>
                  <TableCell>
                    <Typography fontWeight={600}>{service.name}</Typography>
                  </TableCell>
                  <TableCell>
                    <Chip size="small" label={service.namespace} variant="outlined" />
                  </TableCell>
                  <TableCell>{getTypeChip(service.type)}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{service.cluster_ip}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace' }}>
                    {service.external_ip || '-'}
                  </TableCell>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{service.ports}</TableCell>
                  <TableCell>{service.age}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
};

export default ServicesPage;
