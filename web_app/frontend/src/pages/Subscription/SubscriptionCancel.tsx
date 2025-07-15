import React from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Alert
} from '@mui/material';
import {
  Cancel as CancelIcon,
  Home as HomeIcon,
  Refresh as RetryIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const SubscriptionCancel: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 6 }}>
          <CancelIcon 
            sx={{ 
              fontSize: 80, 
              color: 'warning.main', 
              mb: 2 
            }} 
          />
          
          <Typography variant="h4" gutterBottom fontWeight={600}>
            Subscription Cancelled
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            You cancelled the subscription process. No charges have been made to your account.
          </Typography>

          <Alert severity="info" sx={{ mb: 3, textAlign: 'left' }}>
            <Typography variant="body2">
              Don't worry! You can try again anytime. Your current plan and usage remain unchanged.
            </Typography>
          </Alert>

          <Box display="flex" gap={2} justifyContent="center" mt={4}>
            <Button
              variant="contained"
              startIcon={<RetryIcon />}
              onClick={() => navigate('/subscription')}
              size="large"
            >
              Try Again
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<HomeIcon />}
              onClick={() => navigate('/dashboard')}
              size="large"
            >
              Go to Dashboard
            </Button>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
            If you have any questions about our plans, feel free to contact our support team.
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default SubscriptionCancel;