import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Avatar,
  Button,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Star as StarIcon,
  StarOutline as StarOutlineIcon,
  OpenInNew as OpenIcon,
} from '@mui/icons-material';
import { apiClient } from '@api/client';
import { API_ENDPOINTS } from '@config/api';
import { PageSkeleton } from '@components/Skeletons';

interface CatalogEntry {
  id: number;
  telegram_id: number;
  username: string | null;
  title: string;
  description: string | null;
  avatar_url: string | null;
  category_name: string | null;
  subscriber_count: number | null;
  is_featured: boolean;
}

const FeaturedPage: React.FC = () => {
  const [entries, setEntries] = useState<CatalogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const fetchFeatured = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(API_ENDPOINTS.CATALOG.LIST, {
        params: { is_featured: true, per_page: 50 },
      });
      setEntries(response.data.entries || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load featured channels');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeatured();
  }, []);

  const handleUnfeature = async (entry: CatalogEntry) => {
    setActionLoading(entry.id);
    try {
      await apiClient.post(API_ENDPOINTS.CATALOG.FEATURE(entry.id), null, {
        params: { featured: false },
      });
      fetchFeatured();
    } catch (err: any) {
      setError(err.message || 'Failed to unfeature channel');
    } finally {
      setActionLoading(null);
    }
  };

  const formatNumber = (num: number | null): string => {
    if (num === null) return '-';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  if (loading) {
    return <PageSkeleton />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        <StarIcon sx={{ mr: 1, verticalAlign: 'bottom', color: 'warning.main' }} />
        Featured Channels
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Channels displayed on the public homepage ({entries.length} featured)
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {entries.length === 0 ? (
        <Alert severity="info">
          No featured channels yet. Go to Channel Catalog to feature channels.
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {entries.map((entry) => (
            <Grid item xs={12} sm={6} md={4} key={entry.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Avatar
                      src={entry.avatar_url || undefined}
                      sx={{ width: 56, height: 56 }}
                    >
                      {entry.title?.[0] || '?'}
                    </Avatar>
                    <Box sx={{ flex: 1, overflow: 'hidden' }}>
                      <Typography variant="h6" noWrap>
                        {entry.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" noWrap>
                        @{entry.username || 'private'}
                      </Typography>
                    </Box>
                    <StarIcon sx={{ color: 'warning.main' }} />
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip
                      label={`${formatNumber(entry.subscriber_count)} subscribers`}
                      size="small"
                      variant="outlined"
                    />
                    {entry.category_name && (
                      <Chip
                        label={entry.category_name}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    startIcon={<StarOutlineIcon />}
                    onClick={() => handleUnfeature(entry)}
                    disabled={actionLoading === entry.id}
                  >
                    {actionLoading === entry.id ? (
                      <CircularProgress size={16} />
                    ) : (
                      'Unfeature'
                    )}
                  </Button>
                  {entry.username && (
                    <Button
                      size="small"
                      startIcon={<OpenIcon />}
                      href={`https://t.me/${entry.username}`}
                      target="_blank"
                    >
                      Open
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default FeaturedPage;
