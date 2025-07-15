import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';

interface User {
  id: number;
  email: string;
  full_name: string;
  tier: 'free' | 'basic' | 'pro' | 'enterprise';
  subscription_active: boolean;
  files_processed_this_month: number;
  total_files_processed: number;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: true,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          console.log('Login attempt with API base:', api.defaults.baseURL);
          
          // Single request for login
          const response = await api.post('/auth/login', {
            email,
            password,
          });

          const { access_token } = response.data;
          
          // Set token in API headers immediately
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          
          // Get user profile - simplified without retry
          const userResponse = await api.get('/users/me');
          
          set({
            token: access_token,
            user: userResponse.data,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({ isLoading: false });
          // Provide more specific error messages
          if (error.code === 'ECONNABORTED') {
            throw new Error('Login timeout. Please try again.');
          } else if (error.code === 'ERR_CONNECTION_RESET' || error.code === 'ERR_NETWORK') {
            throw new Error('Cannot connect to server. Please ensure the backend is running.');
          }
          throw error;
        }
      },

      register: async (email: string, password: string, fullName: string) => {
        try {
          await api.post('/auth/register', {
            email,
            password,
            full_name: fullName,
          });

          // Auto-login after registration
          await get().login(email, password);
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        // Remove token from API headers
        delete api.defaults.headers.common['Authorization'];
        
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
        
        // Clear persisted state
        localStorage.removeItem('auth-storage');
      },

      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({
            user: { ...currentUser, ...userData },
          });
        }
      },

      checkAuth: async () => {
        const token = get().token;
        
        if (!token) {
          set({ isLoading: false, isAuthenticated: false });
          return;
        }

        try {
          // Set token in API headers
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Verify token by getting user profile with shorter timeout for checkAuth
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout for auth check
          
          const response = await api.get('/users/me', {
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          
          set({
            user: response.data,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          // Token is invalid or request failed, clear auth state
          console.warn('Auth check failed:', error.message);
          get().logout();
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
      }),
      onRehydrateStorage: () => (state) => {
        // Fast auth check on app load - don't block the UI
        if (state?.token) {
          // Check auth in background without blocking
          setTimeout(() => {
            state.checkAuth();
          }, 100); // Small delay to allow UI to render first
        } else {
          state && (state.isLoading = false);
        }
      },
    }
  )
);

// Initialize auth check on app start - optimized for faster loading
if (typeof window !== 'undefined') {
  const { checkAuth, token } = useAuthStore.getState();
  if (token) {
    // Defer auth check to avoid blocking initial render
    setTimeout(() => {
      checkAuth();
    }, 200);
  } else {
    useAuthStore.setState({ isLoading: false });
  }
}