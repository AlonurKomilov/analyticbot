/**
 * AIServicesGrid - AI services navigation component
 *
 * Extracted from MainDashboard.jsx to provide focused AI services display
 * with navigation capabilities.
 */

import React from 'react';
import { Box, Typography, Chip, SvgIconTypeMap } from '@mui/material';
import { OverridableComponent } from '@mui/material/OverridableComponent';
import { useNavigate } from 'react-router-dom';
import { StandardCard, StandardButton, GridContainer } from '../common/StandardComponents';
import { DESIGN_TOKENS } from '../../theme/designTokens';
import {
    AutoFixHigh as ContentIcon,
    TrendingUp as PredictiveIcon,
    PersonRemove as ChurnIcon,
    Security as SecurityIcon,
    Launch as LaunchIcon
} from '@mui/icons-material';

type ServiceStatus = 'active' | 'beta' | 'maintenance';
type StatusColor = 'success' | 'warning' | 'error' | 'default';

interface ServiceMetrics {
  [key: string]: string | number;
}

interface AIService {
  name: string;
  description: string;
  status: ServiceStatus;
  icon: OverridableComponent<SvgIconTypeMap<{}, "svg">>;
  path: string;
  metrics: ServiceMetrics;
}

const AIServicesGrid: React.FC = () => {
  const navigate = useNavigate();

  const aiServices: AIService[] = [
    {
      name: 'Content Optimizer',
      description: 'AI-powered content enhancement for maximum engagement',
      status: 'active',
      icon: ContentIcon,
      path: '/services/content-optimizer',
      metrics: { optimized: 1247, improvement: '+34%' }
    },
    {
      name: 'Predictive Analytics',
      description: 'Future performance predictions and trend analysis',
      status: 'active',
      icon: PredictiveIcon,
      path: '/services/predictive-analytics',
      metrics: { accuracy: '94.2%', predictions: 156 }
    },
    {
      name: 'Churn Predictor',
      description: 'Customer retention insights and risk assessment',
      status: 'beta',
      icon: ChurnIcon,
      path: '/services/churn-predictor',
      metrics: { atRisk: 47, saved: 23 }
    },
    {
      name: 'Security Monitoring',
      description: 'Real-time security analysis and threat detection',
      status: 'active',
      icon: SecurityIcon,
      path: '/services/security-monitoring',
      metrics: { blocked: 156, score: '87%' }
    }
  ];

  const getStatusColor = (status: ServiceStatus): StatusColor => {
    switch (status) {
      case 'active': return 'success';
      case 'beta': return 'warning';
      case 'maintenance': return 'error';
      default: return 'default';
    }
  };

  const handleServiceClick = (path: string): void => {
    navigate(path);
  };

  const handleViewAllClick = (): void => {
    navigate('/services');
  };

  return (
    <Box>
      <Box sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        mb: 3
      }}>
        <Typography variant="h6" fontWeight={600}>
          AI Services Quick Access
        </Typography>
        <StandardButton
          variant="secondary"
          size="medium"
          endIcon={<LaunchIcon />}
          onClick={handleViewAllClick}
        >
          View All Services
        </StandardButton>
      </Box>

      <GridContainer
        gap="md"
        columns={{ xs: 1, sm: 2, md: 2, lg: 4 }}
      >
        {aiServices.map((service) => {
          const IconComponent = service.icon;
          return (
            <StandardCard
              key={service.name}
              variant="interactive"
              interactive
              onClick={() => handleServiceClick(service.path)}
              sx={{
                height: '100%',
                cursor: 'pointer'
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 2
                }}
              >
                <IconComponent
                  sx={{
                    fontSize: DESIGN_TOKENS.components.icon.sizes.lg,
                    color: 'primary.main'
                  }}
                />
                <Chip
                  label={service.status}
                  color={getStatusColor(service.status)}
                  size="small"
                />
              </Box>

              <Typography
                variant="h6"
                fontWeight={600}
                sx={{ mb: 1 }}
              >
                {service.name}
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  mb: 2,
                  minHeight: 40,
                  lineHeight: 1.4
                }}
              >
                {service.description}
              </Typography>

              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: '0.85rem'
                }}
              >
                {Object.entries(service.metrics).map(([key, value]) => (
                  <Box key={key} sx={{ textAlign: 'center' }}>
                    <Typography variant="caption" color="text.secondary">
                      {key}
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                      {value}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </StandardCard>
          );
        })}
      </GridContainer>
    </Box>
  );
};

export default AIServicesGrid;
