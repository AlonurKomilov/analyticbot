import { useState, useEffect } from 'react'
import { useSearchParams, Link as RouterLink } from 'react-router-dom'
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
  TextField,
  InputAdornment,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import PeopleIcon from '@mui/icons-material/People'
import { publicApi } from '@/api'

interface Channel {
  id: number
  username: string
  title: string
  description: string
  subscriber_count: number
  photo_url?: string
  is_verified: boolean
  category_name?: string
}

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  const [channels, setChannels] = useState<Channel[]>([])
  const [loading, setLoading] = useState(false)
  const [searchInput, setSearchInput] = useState(query)

  useEffect(() => {
    const fetchResults = async () => {
      if (!query.trim()) {
        setChannels([])
        return
      }
      
      try {
        setLoading(true)
        const response = await publicApi.searchChannels(query, 20)
        setChannels(response.data?.channels || response.data || [])
      } catch (err: any) {
        console.error('Search failed:', err)
        setChannels([])
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [query])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchInput.trim()) {
      setSearchParams({ q: searchInput.trim() })
    }
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  return (
    <>
      <Helmet>
        <title>{query ? `Search: ${query}` : 'Search'} - AnalyticBot</title>
        <meta name="description" content={`Search Telegram channels${query ? ` for "${query}"` : ''}. Find channel statistics and analytics.`} />
      </Helmet>

      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" fontWeight={700} gutterBottom>
          Search Channels
        </Typography>

        <form onSubmit={handleSearch}>
          <TextField
            fullWidth
            placeholder="Search for Telegram channels..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ maxWidth: 600 }}
          />
        </form>
      </Box>

      {query && (
        <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
          {loading ? 'Searching...' : `${channels.length} results for "${query}"`}
        </Typography>
      )}

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
                        <Box sx={{ display: 'flex', gap: 1, mt: 1, alignItems: 'center' }}>
                          <Chip 
                            icon={<PeopleIcon />} 
                            label={formatNumber(channel.subscriber_count)} 
                            size="small" 
                            variant="outlined"
                          />
                          {channel.category_name && (
                            <Chip 
                              label={channel.category_name} 
                              size="small" 
                              color="primary"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </Box>
                    </Box>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))
        ) : query ? (
          <Grid item xs={12}>
            <Alert severity="info">
              No channels found for "{query}". Try a different search term.
            </Alert>
          </Grid>
        ) : (
          <Grid item xs={12}>
            <Alert severity="info">
              Enter a search term to find Telegram channels.
            </Alert>
          </Grid>
        )}
      </Grid>
    </>
  )
}
