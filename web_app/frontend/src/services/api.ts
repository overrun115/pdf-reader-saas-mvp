import axios from 'axios';
import toast from 'react-hot-toast';
import { extractErrorMessage } from '../utils/errorUtils';

// Create axios instance
const apiBaseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
console.log('API Base URL:', apiBaseURL);

const api = axios.create({
  baseURL: apiBaseURL,
  timeout: 15000, // Reduced to 15 seconds for faster login feedback
  withCredentials: false, // Disable credentials to match CORS wildcard origins
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent caching
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      };
    }
    
    // Add auth token from localStorage
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const authData = JSON.parse(authStorage);
        if (authData.state?.token) {
          config.headers.Authorization = `Bearer ${authData.state.token}`;
        }
      }
    } catch (error) {
      console.error('Error reading auth token:', error);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const { response } = error;
    
    // Handle network errors specifically
    if (!response) {
      if (error.code === 'ECONNABORTED') {
        toast.error('Request timeout. Please try again.');
      } else if (error.code === 'ERR_NETWORK' || error.code === 'ERR_CONNECTION_RESET') {
        toast.error('Cannot connect to server. Please check if the backend is running.');
      } else {
        toast.error('Network error. Please check your connection.');
      }
      return Promise.reject(error);
    }

    const { status, data } = response;

    switch (status) {
      case 400:
        toast.error(extractErrorMessage(data.detail) || 'Bad request');
        break;
      case 401:
        toast.error('Session expired. Please login again.');
        // Clear auth state
        localStorage.removeItem('auth-storage');
        window.location.href = '/login';
        break;
      case 403:
        toast.error('Access denied');
        break;
      case 404:
        toast.error('Resource not found');
        break;
      case 413:
        toast.error('File too large. Please upload a smaller file.');
        break;
      case 422:
        // Validation errors
        console.log('422 Error details:', data.detail);
        const errorMessage = extractErrorMessage(data.detail);
        console.log('Extracted error message:', errorMessage);
        toast.error(errorMessage || 'Validation error');
        break;
      case 429:
        toast.error('Rate limit exceeded. Please try again later.');
        break;
      case 500:
        toast.error('Server error. Please try again later.');
        break;
      default:
        toast.error(extractErrorMessage(data.detail) || 'An unexpected error occurred');
    }

    return Promise.reject(error);
  }
);

// Create a separate instance for file uploads with longer timeout
export const fileApi = axios.create({
  baseURL: apiBaseURL,
  timeout: 300000, // 5 minutes for file uploads
  withCredentials: false, // Disable credentials to match CORS wildcard origins
  headers: {
    'Content-Type': 'multipart/form-data',
    'Accept': 'application/json',
  },
});

// Apply same interceptors to fileApi
fileApi.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent caching
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      };
    }
    
    // Add auth token from localStorage
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const authData = JSON.parse(authStorage);
        if (authData.state?.token) {
          config.headers.Authorization = `Bearer ${authData.state.token}`;
        }
      }
    } catch (error) {
      console.error('Error reading auth token:', error);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

fileApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const { response } = error;
    
    // Handle network errors specifically
    if (!response) {
      if (error.code === 'ECONNABORTED') {
        toast.error('File upload timeout. Please try with a smaller file or check your connection.');
      } else if (error.code === 'ERR_NETWORK' || error.code === 'ERR_CONNECTION_RESET') {
        toast.error('Cannot connect to server. Please check if the backend is running.');
      } else {
        toast.error('Network error. Please check your connection.');
      }
      return Promise.reject(error);
    }

    const { status, data } = response;

    switch (status) {
      case 400:
        toast.error(extractErrorMessage(data.detail) || 'Bad request');
        break;
      case 401:
        toast.error('Session expired. Please login again.');
        localStorage.removeItem('auth-storage');
        window.location.href = '/login';
        break;
      case 403:
        toast.error('Access denied');
        break;
      case 404:
        toast.error('Resource not found');
        break;
      case 413:
        toast.error('File too large. Please upload a smaller file.');
        break;
      case 422:
        toast.error(extractErrorMessage(data.detail) || 'Validation error');
        break;
      case 429:
        toast.error('Rate limit exceeded. Please try again later.');
        break;
      case 500:
        toast.error('Server error. Please try again later.');
        break;
      default:
        toast.error(extractErrorMessage(data.detail) || 'An unexpected error occurred');
    }

    return Promise.reject(error);
  }
);

export default api;