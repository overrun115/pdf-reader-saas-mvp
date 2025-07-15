import { QueryClient } from 'react-query';

// Optimized React Query configuration for better login performance
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Reduce background refetching to improve performance
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      
      // Faster stale times for auth-related queries
      staleTime: 30000, // 30 seconds
      cacheTime: 300000, // 5 minutes
      
      // Retry configuration
      retry: (failureCount, error: any) => {
        // Don't retry auth errors (401, 403)
        if (error?.response?.status === 401 || error?.response?.status === 403) {
          return false;
        }
        // Only retry network errors up to 2 times
        return failureCount < 2;
      },
      
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 3000),
    },
    mutations: {
      // Faster timeout for mutations like login
      retry: 1,
      retryDelay: 1000,
    },
  },
});

// Special configuration for auth-related queries
export const authQueryOptions = {
  staleTime: 60000, // 1 minute for auth data
  cacheTime: 300000, // 5 minutes
  retry: false, // Don't retry auth failures
  refetchOnWindowFocus: false,
};

// Configuration for dashboard data
export const dashboardQueryOptions = {
  staleTime: 30000, // 30 seconds
  cacheTime: 300000, // 5 minutes
  refetchInterval: 60000, // Auto-refresh every minute
  retry: 1,
  retryDelay: 2000,
};

// Configuration for file operations
export const fileQueryOptions = {
  staleTime: 10000, // 10 seconds (files change more frequently)
  cacheTime: 300000, // 5 minutes
  retry: 2,
  retryDelay: 1000,
};
