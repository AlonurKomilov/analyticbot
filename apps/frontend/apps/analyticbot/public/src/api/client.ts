import axios from 'axios'

// API base URL - use proxy in development
const API_BASE = '/api'
const PUBLIC_BASE = '/public'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Public API endpoints (no auth required)
export const publicApi = {
  // Get all categories
  getCategories: () => api.get(`${PUBLIC_BASE}/categories`),
  
  // Get channels list with filters
  getChannels: (params?: {
    category_id?: number
    sort_by?: 'subscribers' | 'growth' | 'posts' | 'trending'
    limit?: number
    offset?: number
  }) => api.get(`${PUBLIC_BASE}/channels`, { params }),
  
  // Get featured channels
  getFeaturedChannels: () => api.get(`${PUBLIC_BASE}/channels/featured`),
  
  // Get trending channels
  getTrendingChannels: (limit?: number) => 
    api.get(`${PUBLIC_BASE}/channels/trending`, { params: { limit } }),
  
  // Get channel details by username
  getChannel: (username: string) => 
    api.get(`${PUBLIC_BASE}/channels/${username}`),
  
  // Search channels
  searchChannels: (query: string, limit?: number) =>
    api.get(`${PUBLIC_BASE}/search`, { params: { q: query, limit } }),
  
  // Get catalog stats
  getStats: () => api.get(`${PUBLIC_BASE}/stats`),
  
  // Get channels by category
  getChannelsByCategory: (categorySlug: string, params?: {
    limit?: number
    offset?: number
  }) => api.get(`${PUBLIC_BASE}/categories/${categorySlug}/channels`, { params }),
}

export default api
