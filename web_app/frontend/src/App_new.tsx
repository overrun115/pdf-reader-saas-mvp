import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider, QueryClient } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { useAuthStore } from './store/authStore';
import { useThemeMode } from './hooks/useTheme';
import { getTheme } from './theme/theme';

// Layout components
import Layout from './components/Layout/Layout';

// Auth pages
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';

// Main pages
import Dashboard from './pages/Dashboard/Dashboard';
import FileUploadPage from './pages/FileUpload/FileUpload';
import FileManager from './pages/FileManager/FileManager';
import Subscription from './pages/Subscription/Subscription';
import SubscriptionSuccess from './pages/Subscription/SubscriptionSuccess';
import PDFViewer from './pages/PDFViewer/PDFViewer';

// Admin pages
import AdminDashboard from './pages/Admin/AdminDashboard';
import UserManagement from './pages/Admin/UserManagement';

// Support pages
import FAQ from './pages/Support/FAQ';
import Contact from './pages/Support/Contact';

// Trial page
import Trial from './pages/Trial/TrialUpload';

// Simple Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const queryClient = new QueryClient();

function App() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const themeMode = useThemeMode();
  
  // Always use light theme for public pages, user preference for private pages
  const isPublicRoute = window.location.pathname === '/' || 
                       window.location.pathname === '/login' || 
                       window.location.pathname === '/register' ||
                       window.location.pathname === '/trial' ||
                       window.location.pathname === '/contact' ||
                       window.location.pathname === '/faq';
  
  const theme = getTheme(isPublicRoute ? 'light' : themeMode.mode);

  // Show loading screen while checking authentication
  if (isLoading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          background: '#f8fafc',
          color: '#0066FF',
          fontSize: '18px',
          flexDirection: 'column'
        }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: '4px solid rgba(0, 102, 255, 0.2)',
            borderTop: '4px solid #0066FF',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            marginBottom: '20px'
          }} />
          <div>Loading...</div>
        </div>
      </ThemeProvider>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Trial />} />
            <Route path="/trial" element={<Trial />} />
            <Route path="/try-demo" element={<Trial />} />
            <Route path="/pdf-analyzer" element={<PDFViewer />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/faq" element={<FAQ />} />
            <Route path="/login" element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
            } />
            <Route path="/register" element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />
            } />

            {/* Protected Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/upload" element={
              <ProtectedRoute>
                <Layout>
                  <FileUploadPage />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/files" element={
              <ProtectedRoute>
                <Layout>
                  <FileManager />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/subscription" element={
              <ProtectedRoute>
                <Layout>
                  <Subscription />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/subscription/success" element={
              <ProtectedRoute>
                <Layout>
                  <SubscriptionSuccess />
                </Layout>
              </ProtectedRoute>
            } />

            {/* Admin Routes */}
            <Route path="/admin" element={
              <ProtectedRoute>
                <Layout>
                  <AdminDashboard />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/admin/users" element={
              <ProtectedRoute>
                <Layout>
                  <UserManagement />
                </Layout>
              </ProtectedRoute>
            } />

            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 5000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                style: {
                  background: '#10b981',
                },
              },
              error: {
                style: {
                  background: '#ef4444',
                },
              },
            }}
          />
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
