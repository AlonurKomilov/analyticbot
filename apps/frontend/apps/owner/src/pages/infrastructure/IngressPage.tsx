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
import { Refresh, CheckCircle, Warning } from '@mui/icons-material';
import { ownerApi } from '@api/ownerApi';

interface Ingress {
  name: string;
  namespace: string;
  class: string;
  hosts: string[];
  address: string;
  tls: boolean;
  age: string;
}

const IngressPage: React.FC = () => {
  const [ingresses, setIngresses] = useState<Ingress[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchIngresses = async () => {
    setLoading(true);
    try {
      const response = await ownerApi.getIngress();
      setIngresses(response.data);
    } catch (err) {
      // Mock data
      setIngresses([
        { name: 'analyticbot-main', namespace: 'analyticbot', class: 'nginx', hosts: ['analyticbot.org', 'www.analyticbot.org'], address: '207.180.226.85', tls: true, age: '15d' },
        { name: 'analyticbot-api', namespace: 'analyticbot', class: 'nginx', hosts: ['api.analyticbot.org'], address: '207.180.226.85', tls: true, age: '15d' },
        { name: 'analyticbot-admin', namespace: 'analyticbot', class: 'nginx', hosts: ['admin.analyticbot.org'], address: '207.180.226.85', tls: true, age: '15d' },
        { name: 'analyticbot-owner', namespace: 'analyticbot', class: 'nginx', hosts: ['owner.analyticbot.org'], address: '207.180.226.85', tls: true, age: '1d' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIngresses();
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
            Ingress
          </Typography>
          <Typography variant="body1" color="text.secondary">
            External access routes and TLS configuration
          </Typography>
        </Box>
        <IconButton onClick={fetchIngresses} color="primary">
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
                <TableCell>Class</TableCell>
                <TableCell>Hosts</TableCell>
                <TableCell>Address</TableCell>
                <TableCell>TLS</TableCell>
                <TableCell>Age</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {ingresses.map((ingress) => (
                <TableRow key={`${ingress.namespace}-${ingress.name}`} hover>
                  <TableCell>
                    <Typography fontWeight={600}>{ingress.name}</Typography>
                  </TableCell>
                  <TableCell>
                    <Chip size="small" label={ingress.namespace} variant="outlined" />
                  </TableCell>
                  <TableCell>{ingress.class}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {ingress.hosts.map((host) => (
                        <Chip
                          key={host}
                          size="small"
                          label={host}
                          sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}
                        />
                      ))}
                    </Box>
                  </TableCell>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{ingress.address}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      icon={ingress.tls ? <CheckCircle /> : <Warning />}
                      label={ingress.tls ? 'Enabled' : 'Disabled'}
                      color={ingress.tls ? 'success' : 'warning'}
                    />
                  </TableCell>
                  <TableCell>{ingress.age}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
};

export default IngressPage;
