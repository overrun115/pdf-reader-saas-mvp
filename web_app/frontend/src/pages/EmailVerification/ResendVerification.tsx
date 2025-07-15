import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import {
  Email,
  Send,
  CheckCircle,
  Home
} from '@mui/icons-material';
import api from '../../services/api';
import toast from 'react-hot-toast';
import { extractApiErrorMessage } from '../../utils/errorUtils';

const ResendVerification: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!email) {
      setError('Please enter your email address');
      return;
    }

    try {
      setLoading(true);
      await api.post('/email/send-verification', { email });
      setSent(true);
      toast.success('¡Email de verificación enviado exitosamente!');
    } catch (error: any) {
      console.error('Failed to send verification email:', error);
      const errorMessage = extractApiErrorMessage(error) || 'Failed to send verification email';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
          <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
          <Typography variant="h4" gutterBottom fontWeight={700}>
            Email Sent Successfully!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Te hemos enviado un email de verificación a <strong>{email}</strong>.
            Por favor revisa tu bandeja de entrada y haz clic en el enlace de verificación.
          </Typography>
          
          <Card sx={{ mb: 4, textAlign: 'left' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📧 Check Your Email
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                The verification email may take a few minutes to arrive. Please check:
              </Typography>
              <Box component="ul" sx={{ mt: 2, pl: 2 }}>
                <li>Your inbox for the verification email</li>
                <li>Your spam/junk folder</li>
                <li>Your promotions folder (if using Gmail)</li>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                The verification link will expire in 24 hours.
              </Typography>
            </CardContent>
          </Card>
          
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<Home />}
              onClick={() => navigate('/')}
              sx={{ minWidth: 150 }}
            >
              Go Home
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => {
                setSent(false);
                setEmail('');
              }}
              sx={{ minWidth: 150 }}
            >
              Send Another
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Email sx={{ fontSize: 80, color: 'primary.main', mb: 3 }} />
          <Typography variant="h4" gutterBottom fontWeight={700}>
            Resend Verification Email
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Enter your email address to receive a new verification link.
          </Typography>
        </Box>

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Email Address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
            sx={{ mb: 3 }}
            helperText="We'll send you a new verification link to this email address"
          />

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
            sx={{ mb: 3 }}
          >
            {loading ? 'Sending...' : 'Send Verification Email'}
          </Button>
        </form>

        <Divider sx={{ my: 3 }} />

        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Already verified your email?
          </Typography>
          <Button
            variant="text"
            onClick={() => navigate('/login')}
            sx={{ textTransform: 'none' }}
          >
            Back to Login
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default ResendVerification;