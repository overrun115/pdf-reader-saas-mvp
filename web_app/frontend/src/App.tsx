import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider, QueryClient } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { useAuthStore } from './store/authStore';
import { useTheme, CustomThemeProvider } from './hooks/useTheme';
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
import EnterpriseIntegrations from './pages/EnterpriseIntegrations/EnterpriseIntegrations';

// Admin pages
import AdminDashboard from './pages/Admin/AdminDashboard';
import UserManagement from './pages/Admin/UserManagement';
import TransactionHistory from './pages/Admin/TransactionHistory';

// Support pages
import FAQ from './pages/Support/FAQ';
import Contact from './pages/Support/Contact';

// API Documentation
import ApiDocs from './pages/ApiDocs/ApiDocs';

// Landing and Trial pages
import Landing from './pages/Landing/Landing';
import Trial from './pages/Trial/TrialUpload';

// Profile page
import UserProfile from './pages/Profile/UserProfile';

// Email verification pages
import EmailVerification from './pages/EmailVerification/EmailVerification';
import ResendVerification from './pages/EmailVerification/ResendVerification';
import EmailVerificationPending from './pages/EmailVerification/EmailVerificationPending';

// Legal pages
import PrivacyPolicy from './pages/Legal/PrivacyPolicy';
import TermsOfService from './pages/Legal/TermsOfService';
import CookiePolicy from './pages/Legal/CookiePolicy';

// Simple Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const queryClient = new QueryClient();

// Internal App component that uses theme context
const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuthStore();
  const { mode } = useTheme();
  
  // Use user preference for all pages
  const theme = getTheme(mode);

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
          background: theme.palette.background.default,
          color: theme.palette.primary.main,
          fontSize: '18px',
          flexDirection: 'column'
        }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: `4px solid ${theme.palette.primary.main}20`,
            borderTop: `4px solid ${theme.palette.primary.main}`,
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
            <Route path="/" element={<Landing />} />
            <Route path="/trial" element={<Trial />} />
            <Route path="/try-demo" element={<Trial />} />
            <Route path="/pdf-analyzer" element={<PDFViewer />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/faq" element={<FAQ />} />
            
            {/* Legal Routes */}
            <Route path="/legal/privacy" element={<PrivacyPolicy />} />
            <Route path="/legal/terms" element={<TermsOfService />} />
            <Route path="/legal/cookies" element={<CookiePolicy />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/terms-of-service" element={<TermsOfService />} />
            <Route path="/cookie-policy" element={<CookiePolicy />} />
            <Route path="/login" element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
            } />
            <Route path="/register" element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />
            } />
            <Route path="/verify-email" element={<EmailVerification />} />
            <Route path="/resend-verification" element={<ResendVerification />} />
            <Route path="/email-verification-pending" element={<EmailVerificationPending />} />

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
            <Route path="/profile" element={
              <ProtectedRoute>
                <Layout>
                  <UserProfile />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/enterprise-integrations" element={
              <ProtectedRoute>
                <Layout>
                  <EnterpriseIntegrations />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/api-docs" element={
              <ProtectedRoute>
                <Layout>
                  <ApiDocs />
                </Layout>
              </ProtectedRoute>
            } />

            {/* Admin Routes */}
            <Route path="/management" element={
              <ProtectedRoute>
                <Layout>
                  <AdminDashboard />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/management/users" element={
              <ProtectedRoute>
                <Layout>
                  <UserManagement />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/management/transactions" element={
              <ProtectedRoute>
                <Layout>
                  <TransactionHistory />
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
                background: theme.palette.background.paper,
                color: theme.palette.text.primary,
                border: `1px solid ${theme.palette.divider}`,
              },
              success: {
                style: {
                  background: theme.palette.success.main,
                  color: theme.palette.success.contrastText,
                },
              },
              error: {
                style: {
                  background: theme.palette.error.main,
                  color: theme.palette.error.contrastText,
                },
              },
            }}
          />
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

// Main App component with theme provider
function App() {
  return (
    <CustomThemeProvider>
      <AppContent />
    </CustomThemeProvider>
  );
}

export default App;
