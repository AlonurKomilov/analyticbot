import { useState, useEffect } from 'react'
import { useParams, Link as RouterLink } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Skeleton,
  Alert,
  Breadcrumbs,
  Link,
  Pagination,
} from '@mui/material'
import PeopleIcon from '@mui/icons-material/People'
import HomeIcon from '@mui/icons-material/Home'
import { publicApi } from '@/api'

interface Channel {
  id: number
  username: string
  title: string
  description: string
  subscriber_count: number
  photo_url?: string
  is_verified: boolean
  growth_rate?: number
}

interface Category {
  id: number
  name: string
  slug: string
  icon: string
  description?: string
}

export default function CategoryPage() {
  const { slug } = useParams<{ slug: string }>()
  const [channels, setChannels] = useState<Channel[]>([])
  const [category, setCategory] = useState<Category | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const limit = 12

  useEffect(() => {
    const fetchData = async () => {
      if (!slug) return
      
      try {
        setLoading(true)
        
        // Get category info from categories list
        const categoriesRes = await publicApi.getCategories()
        const categoriesData = categoriesRes.data?.categories || categoriesRes.data || []
        const cat = categoriesData.find((c: Category) => c.slug === slug)
        setCategory(cat || null)
        
        // Get channels in category
        const channelsRes = await publicApi.getChannelsByCategory(slug, {
          limit,
          offset: (page - 1) * limit,
        })
        
        setChannels(channelsRes.data?.channels || channelsRes.data || [])
        const total = channelsRes.data?.total || channelsRes.data?.length || 0
        setTotalPages(Math.ceil(total / limit))
      } catch (err: any) {
        console.error('Failed to fetch category:', err)
        setError(err.response?.data?.detail || 'Category not found')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [slug, page])

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  if (error) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h4" gutterBottom>Category Not Found</Typography>
        <Typography color="text.secondary" sx={{ mb: 3 }}>
          {error}
        </Typography>
      </Box>
    )
  }

  return (
    <>
      <Helmet>
        <title>{category?.name || 'Category'} Telegram Channels - AnalyticBot</title>
        <meta name="description" content={`Browse ${category?.name || ''} Telegram channels. Find the best channels with analytics and statistics.`} />
      </Helmet>

      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link
          component={RouterLink}
          to="/"
          sx={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}
          color="inherit"
        >
          <HomeIcon sx={{ mr: 0.5 }} fontSize="small" />
          Home
        </Link>
        <Typography color="text.primary">
          {category?.icon} {category?.name || slug}
        </Typography>
      </Breadcrumbs>

      {/* Category Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" fontWeight={700} gutterBottom>
          {category?.icon} {category?.name || 'Category'}
        </Typography>
        {category?.description && (
          <Typography variant="body1" color="text.secondary">
            {category.description}
          </Typography>
        )}
      </Box>

      {/* Channels Grid */}
      <Grid container spacing={3}>
        {loading ? (
          [...Array(6)].map((_, i) => (
            <Grid item xs={12} sm={6} md={4} key={i}>
              <Skeleton variant="rectangular" height={150} sx={{ borderRadius: 2 }} />
            </Grid>
          ))
        ) : channels.length > 0 ? (
          channels.map((channel) => (
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
                          flexShrink: 0,
                        }}
                      >
                        {channel.photo_url ? (
                          <img src={channel.photo_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        ) : (
                          channel.title.charAt(0)
                        )}
                      </Box>
                      <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1" fontWeight={600} noWrap>
                            {channel.title}
                          </Typography>
                          {channel.is_verified && <Chip size="small" label="✓" color="primary" />}
                        </Box>
                        <Typography variant="body2" color="text.secondary" noWrap>
                          @{channel.username}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                          <Chip 
                            icon={<PeopleIcon />} 
                            label={formatNumber(channel.subscriber_count)} 
                            size="small" 
                            variant="outlined"
                          />
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
            <Alert severity="info">No channels found in this category.</Alert>
          </Grid>
        )}
      </Grid>

      {/* Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, newPage) => setPage(newPage)}
            color="primary"
            size="large"
          />
        </Box>
      )}
    </>
  )
}
