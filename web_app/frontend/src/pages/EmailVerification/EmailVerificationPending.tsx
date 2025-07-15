import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Alert,
  CircularProgress,
  Link as MuiLink
} from '@mui/material';
import {
  Email,
  CheckCircle,
  Refresh
} from '@mui/icons-material';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import api from '../../services/api';
import toast from 'react-hot-toast';

const EmailVerificationPending: React.FC = () => {
  const location = useLocation();
  const email = location.state?.email;
  const [isResending, setIsResending] = useState(false);
  const navigate = useNavigate();

  const handleResendVerification = async () => {
    if (!email) {
      toast.error('La dirección de email es requerida');
      return;
    }

    setIsResending(true);
    try {
      await api.post('/api/email/send-verification', { email });
      toast.success('¡Email de verificación enviado exitosamente!');
    } catch (error: any) {
      toast.error('No se pudo enviar el email de verificación. Por favor intenta de nuevo.');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        <Box sx={{ mb: 3 }}>
          <Email sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Check Your Email
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Te hemos enviado un enlace de verificación a {email ? <strong>{email}</strong> : 'tu dirección de email'}
          </Typography>
        </Box>

        <Alert severity="info" sx={{ mb: 3, textAlign: 'left' }}>
          <Typography variant="body2">
            <strong>Next steps:</strong>
            <br />
            1. Check your email inbox (and spam folder)
            <br />
            2. Click the verification link in the email
            <br />
            3. Return here to log in to your account
          </Typography>
        </Alert>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 3 }}>
          <Button
            variant="outlined"
            startIcon={isResending ? <CircularProgress size={20} /> : <Refresh />}
            onClick={handleResendVerification}
            disabled={isResending || !email}
          >
            {isResending ? 'Sending...' : 'Resend Email'}
          </Button>
          
          <Button
            variant="contained"
            startIcon={<CheckCircle />}
            onClick={() => navigate('/login')}
          >
            I've Verified My Email
          </Button>
        </Box>

        <Typography variant="body2" color="text.secondary">
          Need help? <MuiLink component={Link} to="/contact">Contact Support</MuiLink>
        </Typography>
      </Paper>
    </Container>
  );
};

export default EmailVerificationPending;