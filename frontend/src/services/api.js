import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error.response?.data || error.message);
    
    // Handle common error cases
    if (error.response?.status === 404) {
      throw new Error('Subreddit not found or no posts available');
    } else if (error.response?.status === 429) {
      throw new Error('Rate limit exceeded. Please try again later.');
    } else if (error.response?.status === 500) {
      throw new Error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please check your connection.');
    } else {
      throw new Error(error.response?.data?.detail || 'An unexpected error occurred');
    }
  }
);

/**
 * Fetch river feed from API
 * @param {string} source - Data source (currently only 'reddit')
 * @param {string} name - Subreddit name
 * @param {number} limit - Maximum number of posts to return
 * @returns {Promise<Object>} River response data
 */
export const fetchRiverFeed = async (source = 'reddit', name = 'technology', limit = 50) => {
  try {
    const response = await api.get('/api/river', {
      params: { source, name, limit }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching river feed:', error);
    throw error;
  }
};

/**
 * Health check for the API
 * @returns {Promise<Object>} Health status
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export default api;
