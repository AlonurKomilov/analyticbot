import { useState, useEffect } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  CardMedia,
  CardActionArea,
  Chip,
  Skeleton,
  Alert,
  Button,
  Paper,
} from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import PeopleIcon from '@mui/icons-material/People'
import CategoryIcon from '@mui/icons-material/Category'
import StarIcon from '@mui/icons-material/Star'
import { publicApi } from '@/api'

interface Category {
  id: number
  name: string
  slug: string
  icon: string
  color: string
  channel_count: number
}

interface Channel {
  id: number
  username: string
  title: string
  description: string
  subscriber_count: number
  photo_url?: string
  is_verified: boolean
  is_featured: boolean
  category_name?: string
  growth_rate?: number
}

interface Stats {
  total_channels: number
  total_categories: number
  total_subscribers: number
}

export default function HomePage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [featuredChannels, setFeaturedChannels] = useState<Channel[]>([])
  const [trendingChannels, setTrendingChannels] = useState<Channel[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [categoriesRes, featuredRes, trendingRes, statsRes] = await Promise.all([
          publicApi.getCategories(),
          publicApi.getFeaturedChannels(),
          publicApi.getTrendingChannels(6),
          publicApi.getStats(),
        ])
        
        // API returns nested objects like {categories: [...], channels: [...]}
        const categoriesData = categoriesRes.data?.categories || categoriesRes.data || []
        const featuredData = featuredRes.data?.channels || featuredRes.data || []
        const trendingData = trendingRes.data?.channels || trendingRes.data || []
        
        setCategories(categoriesData)
        setFeaturedChannels(featuredData)
        setTrendingChannels(trendingData)
        setStats(statsRes.data || null)
      } catch (err: any) {
        console.error('Failed to fetch data:', err)
        setError(err.message || 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  return (
    <>
      <Helmet>
        <title>AnalyticBot - Free Telegram Channel Analytics</title>
        <meta name="description" content="Find and analyze any Telegram channel. Free statistics, subscriber counts, growth rates, and engagement metrics." />
      </Helmet>

      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', mb: 6, mt: 2 }}>
        <Typography variant="h2" component="h1" gutterBottom fontWeight={700}>
          Telegram Channel Analytics
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}>
          Discover and analyze Telegram channels. Get free statistics, growth rates, and engagement metrics.
        </Typography>

        {/* Stats Cards */}
        {stats && (
          <Grid container spacing={3} justifyContent="center" sx={{ mt: 4 }}>
            <Grid item>
              <Paper sx={{ p: 3, textAlign: 'center', minWidth: 150 }}>
                <PeopleIcon color="primary" sx={{ fontSize: 40 }} />
                <Typography variant="h4" fontWeight={700}>{formatNumber(stats.total_channels)}</Typography>
                <Typography color="text.secondary">Channels</Typography>
              </Paper>
            </Grid>
            <Grid item>
              <Paper sx={{ p: 3, textAlign: 'center', minWidth: 150 }}>
                <CategoryIcon color="secondary" sx={{ fontSize: 40 }} />
                <Typography variant="h4" fontWeight={700}>{stats.total_categories}</Typography>
                <Typography color="text.secondary">Categories</Typography>
              </Paper>
            </Grid>
            <Grid item>
              <Paper sx={{ p: 3, textAlign: 'center', minWidth: 150 }}>
                <TrendingUpIcon color="success" sx={{ fontSize: 40 }} />
                <Typography variant="h4" fontWeight={700}>{formatNumber(stats.total_subscribers)}</Typography>
                <Typography color="text.secondary">Total Subscribers</Typography>
              </Paper>
            </Grid>
          </Grid>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>
      )}

      {/* Featured Channels */}
      <Box sx={{ mb: 6 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <StarIcon color="warning" sx={{ mr: 1 }} />
          <Typography variant="h4" component="h2">Featured Channels</Typography>
        </Box>
        
        <Grid container spacing={3}>
          {loading ? (
            [...Array(3)].map((_, i) => (
              <Grid item xs={12} sm={6} md={4} key={i}>
                <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />
              </Grid>
            ))
          ) : featuredChannels.length > 0 ? (
            featuredChannels.map((channel) => (
              <Grid item xs={12} sm={6} md={4} key={channel.id}>
                <Card>
                  <CardActionArea component={RouterLink} to={`/channel/${channel.username}`}>
                    <CardMedia
                      component="div"
                      sx={{
                        height: 100,
                        bgcolor: 'primary.light',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {channel.photo_url ? (
                        <img src={channel.photo_url} alt={channel.title} style={{ height: '100%', width: '100%', objectFit: 'cover' }} />
                      ) : (
                        <Typography variant="h2" color="white">{channel.title.charAt(0)}</Typography>
                      )}
                    </CardMedia>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="h6" noWrap>{channel.title}</Typography>
                        {channel.is_verified && <Chip size="small" label="✓" color="primary" />}
                      </Box>
                      <Typography variant="body2" color="text.secondary" noWrap>
                        @{channel.username}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                        <Chip 
                          icon={<PeopleIcon />} 
                          label={formatNumber(channel.subscriber_count)} 
                          size="small" 
                          variant="outlined"
                        />
                        {channel.growth_rate !== undefined && channel.growth_rate > 0 && (
                          <Chip
                            icon={<TrendingUpIcon />}
                            label={`+${channel.growth_rate.toFixed(1)}%`}
                            size="small"
                            color="success"
                          />
                        )}
                      </Box>
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))
          ) : (
            <Grid item xs={12}>
              <Alert severity="info">No featured channels yet. Check back soon!</Alert>
            </Grid>
          )}
        </Grid>
      </Box>

      {/* Trending Channels */}
      <Box sx={{ mb: 6 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <TrendingUpIcon color="success" sx={{ mr: 1 }} />
          <Typography variant="h4" component="h2">Trending Channels</Typography>
        </Box>
        
        <Grid container spacing={3}>
          {loading ? (
            [...Array(6)].map((_, i) => (
              <Grid item xs={12} sm={6} md={4} key={i}>
                <Skeleton variant="rectangular" height={150} sx={{ borderRadius: 2 }} />
              </Grid>
            ))
          ) : trendingChannels.length > 0 ? (
            trendingChannels.map((channel) => (
              <Grid item xs={12} sm={6} md={4} key={channel.id}>
                <Card>
                  <CardActionArea component={RouterLink} to={`/channel/${channel.username}`}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box
                          sx={{
                            width: 60,
                            height: 60,
                            borderRadius: '50%',
                            bgcolor: 'primary.light',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontWeight: 700,
                            fontSize: 24,
                            overflow: 'hidden',
                          }}
                        >
                          {channel.photo_url ? (
                            <img src={channel.photo_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                          ) : (
                            channel.title.charAt(0)
                          )}
                        </Box>
                        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                          <Typography variant="subtitle1" fontWeight={600} noWrap>
                            {channel.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" noWrap>
                            @{channel.username}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              {formatNumber(channel.subscriber_count)} subscribers
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))
          ) : (
            <Grid item xs={12}>
              <Alert severity="info">No trending channels yet.</Alert>
            </Grid>
          )}
        </Grid>
      </Box>

      {/* Categories */}
      <Box sx={{ mb: 6 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <CategoryIcon color="primary" sx={{ mr: 1 }} />
          <Typography variant="h4" component="h2">Browse by Category</Typography>
        </Box>
        
        <Grid container spacing={2}>
          {loading ? (
            [...Array(8)].map((_, i) => (
              <Grid item xs={6} sm={4} md={3} key={i}>
                <Skeleton variant="rectangular" height={80} sx={{ borderRadius: 2 }} />
              </Grid>
            ))
          ) : categories.length > 0 ? (
            categories.map((category) => (
              <Grid item xs={6} sm={4} md={3} key={category.id}>
                <Card 
                  component={RouterLink} 
                  to={`/category/${category.slug}`}
                  sx={{ 
                    textDecoration: 'none',
                    transition: 'transform 0.2s',
                    '&:hover': { transform: 'translateY(-4px)' }
                  }}
                >
                  <CardContent sx={{ textAlign: 'center', py: 3 }}>
                    <Typography variant="h4" sx={{ mb: 1 }}>{category.icon}</Typography>
                    <Typography variant="subtitle1" fontWeight={600}>{category.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {category.channel_count} channels
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))
          ) : (
            <Grid item xs={12}>
              <Alert severity="info">No categories available.</Alert>
            </Grid>
          )}
        </Grid>
      </Box>

      {/* Premium CTA */}
      <Paper
        sx={{
          p: 4,
          textAlign: 'center',
          background: 'linear-gradient(135deg, #0088cc 0%, #7c4dff 100%)',
          color: 'white',
          borderRadius: 3,
        }}
      >
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Want More Analytics?
        </Typography>
        <Typography variant="body1" sx={{ mb: 3, opacity: 0.9 }}>
          Get detailed analytics, growth charts, engagement metrics, and export capabilities with a free account.
        </Typography>
        <Button
          variant="contained"
          size="large"
          href="https://app.analyticbot.org/register"
          sx={{
            bgcolor: 'white',
            color: 'primary.main',
            '&:hover': { bgcolor: 'grey.100' },
          }}
        >
          Create Free Account
        </Button>
      </Paper>
    </>
  )
}
