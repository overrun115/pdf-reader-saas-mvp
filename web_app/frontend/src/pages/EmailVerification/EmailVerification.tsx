import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Email,
  Home,
  Login
} from '@mui/icons-material';
import api from '../../services/api';
import toast from 'react-hot-toast';

const EmailVerification: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resendingEmail, setResendingEmail] = useState(false);
  
  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      verifyEmail(token);
    } else {
      setLoading(false);
      setError('Invalid verification link. No token provided.');
    }
  }, [token]);

  const verifyEmail = async (token: string) => {
    try {
      setLoading(true);
      await api.post('/email/verify-email', { token });
      setSuccess(true);
      toast.success('Email verified successfully!');
    } catch (error: any) {
      console.error('Email verification failed:', error);
      const errorMessage = error.response?.data?.detail || 'Email verification failed';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleResendEmail = async () => {
    if (!token) return;
    
    try {
      setResendingEmail(true);
      await api.post('/email/resend-verification');
      toast.success('Verification email sent successfully!');
    } catch (error: any) {
      console.error('Failed to resend email:', error);
      toast.error('Failed to resend verification email');
    } finally {
      setResendingEmail(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
          <CircularProgress size={60} sx={{ mb: 3 }} />
          <Typography variant="h5" gutterBottom>
            Verifying your email...
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Please wait while we verify your email address.
          </Typography>
        </Paper>
      </Container>
    );
  }

  if (success) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
          <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
          <Typography variant="h4" gutterBottom fontWeight={700}>
            Email Verified Successfully!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Your email has been verified. You can now access all features of PDF Extractor.
          </Typography>
          
          <Card sx={{ mb: 4, textAlign: 'left' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Email /> Welcome to PDF Extractor!
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Your account is now fully activated. Here's what you can do:
              </Typography>
              <Box component="ul" sx={{ mt: 2, pl: 2 }}>
                <li>Upload PDF files for table extraction</li>
                <li>Download results in Excel or CSV format</li>
                <li>Access advanced processing features</li>
                <li>Manage your subscription and usage</li>
              </Box>
            </CardContent>
          </Card>
          
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<Home />}
              onClick={() => navigate('/dashboard')}
              sx={{ minWidth: 150 }}
            >
              Go to Dashboard
            </Button>
            <Button
              variant="outlined"
              size="large"
              startIcon={<Login />}
              onClick={() => navigate('/login')}
              sx={{ minWidth: 150 }}
            >
              Login
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
          <Error sx={{ fontSize: 80, color: 'error.main', mb: 3 }} />
          <Typography variant="h4" gutterBottom fontWeight={700}>
            Verification Failed
          </Typography>
          <Alert severity="error" sx={{ mb: 3, textAlign: 'left' }}>
            {error}
          </Alert>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            This could happen if:
          </Typography>
          
          <Box component="ul" sx={{ textAlign: 'left', mb: 4, color: 'text.secondary' }}>
            <li>The verification link has expired (links expire after 24 hours)</li>
            <li>The link has already been used</li>
            <li>The link is invalid or corrupted</li>
          </Box>
          
          <Divider sx={{ mb: 3 }} />
          
          <Typography variant="h6" gutterBottom>
            What can you do?
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap', mb: 3 }}>
            <Button
              variant="contained"
              onClick={handleResendEmail}
              disabled={resendingEmail}
              startIcon={resendingEmail ? <CircularProgress size={20} /> : <Email />}
            >
              {resendingEmail ? 'Sending...' : 'Resend Verification Email'}
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate('/login')}
              startIcon={<Login />}
            >
              Back to Login
            </Button>
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            If you continue to have problems, please contact our support team.
          </Typography>
        </Paper>
      </Container>
    );
  }

  return null;
};

export default EmailVerification;