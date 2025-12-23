import React from 'react';
import {
  Box,
  Skeleton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Grid,
} from '@mui/material';

interface TableSkeletonProps {
  rows?: number;
  columns?: number;
  hasHeader?: boolean;
}

/**
 * Skeleton loader for tables
 */
export const TableSkeleton: React.FC<TableSkeletonProps> = ({
  rows = 5,
  columns = 5,
  hasHeader = true,
}) => {
  return (
    <TableContainer component={Paper}>
      <Table>
        {hasHeader && (
          <TableHead>
            <TableRow>
              {Array.from({ length: columns }).map((_, i) => (
                <TableCell key={i}>
                  <Skeleton variant="text" width="80%" />
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
        )}
        <TableBody>
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <TableRow key={rowIndex}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <TableCell key={colIndex}>
                  <Skeleton
                    variant="text"
                    width={colIndex === 0 ? '60%' : '80%'}
                  />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

interface StatCardSkeletonProps {
  count?: number;
}

/**
 * Skeleton loader for stat cards grid
 */
export const StatCardsSkeleton: React.FC<StatCardSkeletonProps> = ({
  count = 4,
}) => {
  return (
    <Grid container spacing={2}>
      {Array.from({ length: count }).map((_, i) => (
        <Grid item xs={6} sm={3} key={i}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Skeleton
                variant="text"
                width={60}
                height={48}
                sx={{ mx: 'auto', mb: 1 }}
              />
              <Skeleton variant="text" width="60%" sx={{ mx: 'auto' }} />
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

interface PageSkeletonProps {
  hasTitle?: boolean;
  hasStats?: boolean;
  hasFilters?: boolean;
  hasTable?: boolean;
  statsCount?: number;
  tableRows?: number;
  tableColumns?: number;
}

/**
 * Full page skeleton with common components
 */
export const PageSkeleton: React.FC<PageSkeletonProps> = ({
  hasTitle = true,
  hasStats = true,
  hasFilters = true,
  hasTable = true,
  statsCount = 4,
  tableRows = 10,
  tableColumns = 6,
}) => {
  return (
    <Box>
      {/* Title Skeleton */}
      {hasTitle && (
        <Box sx={{ mb: 3 }}>
          <Skeleton variant="text" width={250} height={40} />
          <Skeleton variant="text" width={350} height={24} />
        </Box>
      )}

      {/* Stats Cards Skeleton */}
      {hasStats && (
        <Box sx={{ mb: 3 }}>
          <StatCardsSkeleton count={statsCount} />
        </Box>
      )}

      {/* Filters Skeleton */}
      {hasFilters && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Skeleton variant="rounded" width={200} height={40} />
            <Skeleton variant="rounded" width={150} height={40} />
            <Skeleton variant="rounded" width={150} height={40} />
          </Box>
        </Paper>
      )}

      {/* Table Skeleton */}
      {hasTable && <TableSkeleton rows={tableRows} columns={tableColumns} />}
    </Box>
  );
};

interface ListSkeletonProps {
  items?: number;
  showAvatar?: boolean;
}

/**
 * Skeleton loader for list items
 */
export const ListSkeleton: React.FC<ListSkeletonProps> = ({
  items = 5,
  showAvatar = true,
}) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {Array.from({ length: items }).map((_, i) => (
        <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {showAvatar && <Skeleton variant="circular" width={40} height={40} />}
          <Box sx={{ flex: 1 }}>
            <Skeleton variant="text" width="60%" />
            <Skeleton variant="text" width="40%" />
          </Box>
        </Box>
      ))}
    </Box>
  );
};

interface FormSkeletonProps {
  fields?: number;
}

/**
 * Skeleton loader for forms
 */
export const FormSkeleton: React.FC<FormSkeletonProps> = ({ fields = 4 }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {Array.from({ length: fields }).map((_, i) => (
        <Box key={i}>
          <Skeleton variant="text" width={100} sx={{ mb: 1 }} />
          <Skeleton variant="rounded" width="100%" height={56} />
        </Box>
      ))}
      <Skeleton variant="rounded" width={120} height={40} sx={{ mt: 2 }} />
    </Box>
  );
};

interface ChartSkeletonProps {
  height?: number;
}

/**
 * Skeleton loader for charts
 */
export const ChartSkeleton: React.FC<ChartSkeletonProps> = ({
  height = 300,
}) => {
  return (
    <Paper sx={{ p: 3 }}>
      <Skeleton variant="text" width={200} sx={{ mb: 2 }} />
      <Skeleton variant="rounded" width="100%" height={height} />
    </Paper>
  );
};

/**
 * Skeleton loader for dashboard grid
 */
export const DashboardSkeleton: React.FC = () => {
  return (
    <Box>
      {/* Title */}
      <Box sx={{ mb: 3 }}>
        <Skeleton variant="text" width={300} height={40} />
        <Skeleton variant="text" width={200} height={24} />
      </Box>

      {/* Stats Row */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {Array.from({ length: 4 }).map((_, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card>
              <CardContent>
                <Skeleton variant="text" width="50%" />
                <Skeleton variant="text" width={80} height={48} />
                <Skeleton variant="text" width="70%" />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <ChartSkeleton height={350} />
        </Grid>
        <Grid item xs={12} md={4}>
          <ChartSkeleton height={350} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default {
  TableSkeleton,
  StatCardsSkeleton,
  PageSkeleton,
  ListSkeleton,
  FormSkeleton,
  ChartSkeleton,
  DashboardSkeleton,
};
