import { useState, useEffect } from 'react'
import { useParams, Link as RouterLink } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Button,
  Skeleton,
  Card,
  CardContent,
} from '@mui/material'
import PeopleIcon from '@mui/icons-material/People'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import ArticleIcon from '@mui/icons-material/Article'
import VisibilityIcon from '@mui/icons-material/Visibility'
import CalendarTodayIcon from '@mui/icons-material/CalendarToday'
import VerifiedIcon from '@mui/icons-material/Verified'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import LockIcon from '@mui/icons-material/Lock'
import { publicApi } from '@/api'

interface ChannelDetails {
  id: number
  username: string
  title: string
  description: string
  subscriber_count: number
  photo_url?: string
  is_verified: boolean
  is_featured: boolean
  category_name?: string
  category_slug?: string
  growth_rate?: number
  posts_per_day?: number
  avg_views?: number
  engagement_rate?: number
  created_at?: string
  last_synced?: string
}

export default function ChannelPage() {
  const { username } = useParams<{ username: string }>()
  const [channel, setChannel] = useState<ChannelDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchChannel = async () => {
      if (!username) return
      
      try {
        setLoading(true)
        const response = await publicApi.getChannel(username)
        setChannel(response.data)
      } catch (err: any) {
        console.error('Failed to fetch channel:', err)
        setError(err.response?.data?.detail || 'Channel not found')
      } finally {
        setLoading(false)
      }
    }

    fetchChannel()
  }, [username])

  const formatNumber = (num: number | undefined) => {
    if (!num) return '0'
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  if (loading) {
    return (
      <Box>
        <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2, mb: 3 }} />
        <Grid container spacing={3}>
          {[...Array(4)].map((_, i) => (
            <Grid item xs={6} md={3} key={i}>
              <Skeleton variant="rectangular" height={100} sx={{ borderRadius: 2 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    )
  }

  if (error || !channel) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h4" gutterBottom>Channel Not Found</Typography>
        <Typography color="text.secondary" sx={{ mb: 3 }}>
          {error || `The channel @${username} was not found in our catalog.`}
        </Typography>
        <Button component={RouterLink} to="/" variant="contained">
          Back to Home
        </Button>
      </Box>
    )
  }

  return (
    <>
      <Helmet>
        <title>{channel.title} (@{channel.username}) - AnalyticBot</title>
        <meta name="description" content={`${channel.title} Telegram channel statistics: ${formatNumber(channel.subscriber_count)} subscribers. ${channel.description?.slice(0, 120)}`} />
      </Helmet>

      {/* Channel Header */}
      <Paper sx={{ p: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          {/* Avatar */}
          <Box
            sx={{
              width: 120,
              height: 120,
              borderRadius: 2,
              bgcolor: 'primary.light',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: 48,
              fontWeight: 700,
              overflow: 'hidden',
              flexShrink: 0,
            }}
          >
            {channel.photo_url ? (
              <img src={channel.photo_url} alt={channel.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            ) : (
              channel.title.charAt(0)
            )}
          </Box>

          {/* Info */}
          <Box sx={{ flexGrow: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, flexWrap: 'wrap' }}>
              <Typography variant="h4" fontWeight={700}>{channel.title}</Typography>
              {channel.is_verified && (
                <VerifiedIcon color="primary" />
              )}
              {channel.is_featured && (
                <Chip label="Featured" color="warning" size="small" />
              )}
            </Box>
            
            <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
              @{channel.username}
            </Typography>

            {channel.description && (
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2, maxWidth: 600 }}>
                {channel.description}
              </Typography>
            )}

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {channel.category_name && (
                <Chip
                  label={channel.category_name}
                  component={RouterLink}
                  to={`/category/${channel.category_slug}`}
                  clickable
                  color="primary"
                  variant="outlined"
                />
              )}
              <Button
                variant="contained"
                startIcon={<OpenInNewIcon />}
                href={`https://t.me/${channel.username}`}
                target="_blank"
                size="small"
              >
                Open in Telegram
              </Button>
            </Box>
          </Box>
        </Box>
      </Paper>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <PeopleIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" fontWeight={700}>
                {formatNumber(channel.subscriber_count)}
              </Typography>
              <Typography color="text.secondary">Subscribers</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <TrendingUpIcon 
                color={channel.growth_rate && channel.growth_rate > 0 ? 'success' : 'error'} 
                sx={{ fontSize: 40, mb: 1 }} 
              />
              <Typography variant="h4" fontWeight={700}>
                {channel.growth_rate ? `${channel.growth_rate > 0 ? '+' : ''}${channel.growth_rate.toFixed(1)}%` : 'N/A'}
              </Typography>
              <Typography color="text.secondary">Monthly Growth</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <ArticleIcon color="secondary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" fontWeight={700}>
                {channel.posts_per_day?.toFixed(1) || 'N/A'}
              </Typography>
              <Typography color="text.secondary">Posts/Day</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <VisibilityIcon color="info" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" fontWeight={700}>
                {formatNumber(channel.avg_views || 0)}
              </Typography>
              <Typography color="text.secondary">Avg. Views</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Premium Features Lock */}
      <Paper
        sx={{
          p: 4,
          textAlign: 'center',
          background: 'linear-gradient(135deg, rgba(0,136,204,0.1) 0%, rgba(124,77,255,0.1) 100%)',
          border: '2px dashed',
          borderColor: 'primary.main',
          borderRadius: 3,
          mb: 4,
        }}
      >
        <LockIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h5" fontWeight={700} gutterBottom>
          Unlock Full Analytics
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 3, maxWidth: 500, mx: 'auto' }}>
          Get detailed growth charts, engagement metrics, posting schedule analysis, 
          audience insights, and more with a free AnalyticBot account.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            size="large"
            href="https://2bot.org/register"
          >
            Create Free Account
          </Button>
          <Button
            variant="outlined"
            size="large"
            href="https://2bot.org"
          >
            Sign In
          </Button>
        </Box>
      </Paper>

      {/* Last Updated */}
      {channel.last_synced && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'center' }}>
          <CalendarTodayIcon fontSize="small" color="action" />
          <Typography variant="caption" color="text.secondary">
            Last updated: {new Date(channel.last_synced).toLocaleDateString()}
          </Typography>
        </Box>
      )}
    </>
  )
}
