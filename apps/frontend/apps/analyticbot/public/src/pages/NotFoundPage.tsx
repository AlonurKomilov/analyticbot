import { Link as RouterLink } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { Box, Typography, Button, Paper } from '@mui/material'
import HomeIcon from '@mui/icons-material/Home'
import SearchIcon from '@mui/icons-material/Search'

export default function NotFoundPage() {
  return (
    <>
      <Helmet>
        <title>Page Not Found - AnalyticBot</title>
      </Helmet>

      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '50vh',
          textAlign: 'center',
        }}
      >
        <Paper sx={{ p: 6, maxWidth: 500 }}>
          <Typography variant="h1" color="primary" sx={{ fontSize: 120, fontWeight: 700, lineHeight: 1 }}>
            404
          </Typography>
          <Typography variant="h4" gutterBottom sx={{ mt: 2 }}>
            Page Not Found
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 4 }}>
            The page you're looking for doesn't exist or has been moved.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              component={RouterLink}
              to="/"
              variant="contained"
              startIcon={<HomeIcon />}
            >
              Go Home
            </Button>
            <Button
              component={RouterLink}
              to="/search"
              variant="outlined"
              startIcon={<SearchIcon />}
            >
              Search Channels
            </Button>
          </Box>
        </Paper>
      </Box>
    </>
  )
}
