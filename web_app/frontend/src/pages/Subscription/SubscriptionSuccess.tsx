import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Home as HomeIcon,
  Payment as PaymentIcon
} from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { subscriptionAPI, SubscriptionStatus } from '../../services/subscriptionApi';
import { useAuthStore } from '../../store/authStore';

const SubscriptionSuccess: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const { user, checkAuth } = useAuthStore();

  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    loadSubscriptionStatus();
    // Refresh user data to get updated subscription info
    checkAuth();
  }, []);

  const loadSubscriptionStatus = async () => {
    try {
      const status = await subscriptionAPI.getSubscriptionStatus();
      setSubscriptionStatus(status);
    } catch (error) {
      console.error('Error loading subscription status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Box display="flex" flexDirection="column" alignItems="center">
          <CircularProgress sx={{ mb: 2 }} />
          <Typography>Verifying your subscription...</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 6 }}>
          <CheckIcon 
            sx={{ 
              fontSize: 80, 
              color: 'success.main', 
              mb: 2 
            }} 
          />
          
          <Typography variant="h4" gutterBottom fontWeight={600}>
            Subscription Activated!
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Thank you for subscribing! Your account has been upgraded and you now have access to all premium features.
          </Typography>

          {subscriptionStatus && (
            <Alert severity="success" sx={{ mb: 3, textAlign: 'left' }}>
              <Typography variant="subtitle2" gutterBottom>
                Subscription Details:
              </Typography>
              <Typography variant="body2">
                Plan: {subscriptionStatus.tier.charAt(0).toUpperCase() + subscriptionStatus.tier.slice(1)}
              </Typography>
              <Typography variant="body2">
                Status: {subscriptionStatus.subscription_active ? 'Active' : 'Inactive'}
              </Typography>
              {sessionId && (
                <Typography variant="body2">
                  Session ID: {sessionId}
                </Typography>
              )}
            </Alert>
          )}

          <Box display="flex" gap={2} justifyContent="center" mt={4}>
            <Button
              variant="contained"
              startIcon={<HomeIcon />}
              onClick={() => navigate('/dashboard')}
              size="large"
            >
              Go to Dashboard
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<PaymentIcon />}
              onClick={() => navigate('/subscription')}
              size="large"
            >
              Manage Subscription
            </Button>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
            You should receive a confirmation email shortly with your receipt and subscription details.
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default SubscriptionSuccess;