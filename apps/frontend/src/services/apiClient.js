/**
 * Base API client configuration
 * Handles authentication, error handling, and common request/response processing
 */

import axios from 'axios';

// Create base API client
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://185.211.5.244:11400',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common error cases
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 401:
          // Unauthorized - clear tokens and redirect to login
          localStorage.removeItem('authToken');
          sessionStorage.removeItem('authToken');
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden
          console.error('Access forbidden:', data.detail || 'Insufficient permissions');
          break;
        case 404:
          // Not found
          console.error('Resource not found:', error.config.url);
          break;
        case 429:
          // Rate limit exceeded
          console.error('Rate limit exceeded. Please try again later.');
          break;
        case 500:
          // Server error
          console.error('Internal server error. Please try again later.');
          break;
        default:
          console.error('API Error:', data.detail || error.message);
      }

      // Re-throw with enhanced error info
      const enhancedError = new Error(data.detail || data.message || error.message);
      enhancedError.status = status;
      enhancedError.data = data;
      throw enhancedError;
    } else if (error.request) {
      // Network error
      const networkError = new Error('Network error. Please check your connection.');
      networkError.isNetworkError = true;
      throw networkError;
    } else {
      // Other error
      throw error;
    }
  }
);

// Add file upload method
apiClient.uploadFileDirect = async (file, onProgress = null) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });

    return response.data;
  } catch (error) {
    console.error('File upload failed:', error);
    throw error;
  }
};

export { apiClient };
export default apiClient;
