import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  useTheme
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer
} from 'recharts';

const DashboardCharts = React.memo(({ trends }) => {
  const theme = useTheme();

  return (
    <Grid container spacing={3}>
      {/* Trends Chart */}
      <Grid item xs={12} lg={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📈 Weekly Performance Trends
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <RechartsTooltip />
                <Line
                  type="monotone"
                  dataKey="views"
                  stroke={theme.palette.primary.main}
                  strokeWidth={3}
                  name="Views"
                />
                <Line
                  type="monotone"
                  dataKey="engagement"
                  stroke={theme.palette.secondary.main}
                  strokeWidth={3}
                  name="Engagement"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
});

DashboardCharts.displayName = 'DashboardCharts';

export default DashboardCharts;
