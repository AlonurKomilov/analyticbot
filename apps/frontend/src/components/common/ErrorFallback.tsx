/**
 * Error Fallback Component
 *
 * User-friendly error UI with Material-UI styling
 */

import React from 'react';
import { Box, Button, Container, Paper, Typography } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import RefreshIcon from '@mui/icons-material/Refresh';
import HomeIcon from '@mui/icons-material/Home';

export interface ErrorFallbackProps {
  error: Error;
  reset?: () => void;
  /** Show error details (development mode) */
  showDetails?: boolean;
}

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  reset,
  showDetails = import.meta.env.DEV === true,
}) => {
  const handleGoHome = () => {
    window.location.href = '/';
  };

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          py: 8,
        }}
      >
        <ErrorOutlineIcon
          sx={{
            fontSize: 100,
            color: 'error.main',
            mb: 3,
          }}
        />

        <Typography
          variant="h3"
          component="h1"
          gutterBottom
          sx={{
            fontWeight: 600,
            textAlign: 'center',
            mb: 2,
          }}
        >
          Oops! Something went wrong
        </Typography>

        <Typography
          variant="body1"
          color="text.secondary"
          sx={{
            textAlign: 'center',
            mb: 4,
            maxWidth: 600,
          }}
        >
          We're sorry, but something unexpected happened. Please try refreshing
          the page or contact support if the problem persists.
        </Typography>

        {showDetails && (
          <Paper
            elevation={0}
            sx={{
              p: 3,
              mb: 4,
              bgcolor: 'error.lighter',
              borderLeft: 4,
              borderColor: 'error.main',
              maxWidth: 700,
              width: '100%',
            }}
          >
            <Typography
              variant="subtitle2"
              sx={{
                fontWeight: 600,
                color: 'error.dark',
                mb: 1,
              }}
            >
              Error Details (Development Mode)
            </Typography>
            <Typography
              variant="body2"
              component="pre"
              sx={{
                color: 'error.dark',
                overflow: 'auto',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
              }}
            >
              {error.message}
              {error.stack && (
                <>
                  {'\n\n'}
                  {error.stack}
                </>
              )}
            </Typography>
          </Paper>
        )}

        <Box sx={{ display: 'flex', gap: 2 }}>
          {reset && (
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={<RefreshIcon />}
              onClick={reset}
            >
              Try Again
            </Button>
          )}

          <Button
            variant="outlined"
            color="primary"
            size="large"
            startIcon={<HomeIcon />}
            onClick={handleGoHome}
          >
            Go Home
          </Button>
        </Box>
      </Box>
    </Container>
  );
};
