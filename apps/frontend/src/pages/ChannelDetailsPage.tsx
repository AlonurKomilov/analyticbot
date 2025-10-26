/**
 * Channel Details Page
 * View detailed analytics and information for a specific channel
 */

import React from 'react';
import { Container, Typography, Box, Paper, Grid, Card, CardContent } from '@mui/material';
import { TrendingUp, People, Visibility, Message } from '@mui/icons-material';
import { useParams } from 'react-router-dom';

const ChannelDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  // Mock data - replace with real API call
  const channel = {
    id,
    name: 'Main Channel',
    subscribers: 15234,
    views: 45678,
    posts: 123,
    engagement: '4.2%',
  };

  const stats = [
    { label: 'Subscribers', value: channel.subscribers.toLocaleString(), icon: <People /> },
    { label: 'Views', value: channel.views.toLocaleString(), icon: <Visibility /> },
    { label: 'Posts', value: channel.posts, icon: <Message /> },
    { label: 'Engagement', value: channel.engagement, icon: <TrendingUp /> },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {channel.name}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Channel ID: {channel.id}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {stat.icon}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {stat.value}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {stat.label}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Channel Analytics
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Detailed analytics charts and insights will appear here.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ChannelDetailsPage;
