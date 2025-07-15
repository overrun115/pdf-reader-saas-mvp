import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Divider,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  AccountCircle as AccountIcon,
  Payment as PaymentIcon,
  Cancel as CancelIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import PricingPlans from '../../components/Subscription/PricingPlans';
import { subscriptionAPI, SubscriptionStatus, UsageInfo } from '../../services/subscriptionApi';
import { format, parseISO } from 'date-fns';
import toast from 'react-hot-toast';

const Subscription: React.FC = () => {
  const navigate = useNavigate();
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus | null>(null);
  const [usageInfo, setUsageInfo] = useState<UsageInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      setLoading(true);
      const [statusData, usageData] = await Promise.all([
        subscriptionAPI.getSubscriptionStatus(),
        subscriptionAPI.getUsageInfo()
      ]);
      setSubscriptionStatus(statusData);
      setUsageInfo(usageData);
    } catch (error) {
      console.error('Error loading subscription data:', error);
      toast.error('Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  };

  const handleManageBilling = async () => {
    try {
      const returnUrl = window.location.href;
      const response = await subscriptionAPI.createBillingPortalSession(returnUrl);
      window.location.href = response.portal_url;
    } catch (error) {
      console.error('Error creating billing portal session:', error);
      toast.error('Failed to open billing portal');
    }
  };

  const handleCancelSubscription = async () => {
    try {
      setCancelling(true);
      await subscriptionAPI.cancelSubscription();
      toast.success('Subscription cancelled successfully');
      setShowCancelDialog(false);
      await loadSubscriptionData(); // Reload data
    } catch (error) {
      console.error('Error cancelling subscription:', error);
      toast.error('Failed to cancel subscription');
    } finally {
      setCancelling(false);
    }
  };

  const getUsagePercentage = () => {
    if (!usageInfo || usageInfo.tier_limit === -1) return 0;
    return (usageInfo.files_processed_this_month / usageInfo.tier_limit) * 100;
  };

  const getUsageColor = () => {
    const percentage = getUsagePercentage();
    if (percentage >= 90) return 'error';
    if (percentage >= 70) return 'warning';
    return 'primary';
  };

  const formatTierName = (tier: string) => {
    return tier.charAt(0).toUpperCase() + tier.slice(1);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <LinearProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Current Subscription Status */}
      <Grid container spacing={4} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom fontWeight={600}>
                Current Subscription
              </Typography>
              
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Chip 
                  label={formatTierName(subscriptionStatus?.tier || 'free')}
                  color="primary"
                  variant="outlined"
                />
                {subscriptionStatus?.subscription_active ? (
                  <Chip label="Active" color="success" size="small" />
                ) : (
                  <Chip label="Inactive" color="default" size="small" />
                )}
              </Box>

              {subscriptionStatus?.subscription_end_date && (
                <Typography variant="body2" color="text.secondary" mb={2}>
                  {subscriptionStatus.subscription_active ? 'Renews' : 'Expires'} on{' '}
                  {format(parseISO(subscriptionStatus.subscription_end_date), 'MMMM d, yyyy')}
                </Typography>
              )}

              {subscriptionStatus?.tier !== 'free' && (
                <Box display="flex" gap={2} mt={2}>
                  <Button
                    variant="outlined"
                    startIcon={<PaymentIcon />}
                    onClick={handleManageBilling}
                  >
                    Manage Billing
                  </Button>
                  
                  {subscriptionStatus?.subscription_active && (
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<CancelIcon />}
                      onClick={() => setShowCancelDialog(true)}
                    >
                      Cancel Subscription
                    </Button>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Usage This Month
              </Typography>
              
              <Box mb={2}>
                <Typography variant="body2" color="text.secondary" mb={1}>
                  {usageInfo?.files_processed_this_month || 0} of{' '}
                  {usageInfo?.tier_limit === -1 ? 'unlimited' : usageInfo?.tier_limit} files used
                </Typography>
                
                {usageInfo?.tier_limit !== -1 && (
                  <LinearProgress
                    variant="determinate"
                    value={getUsagePercentage()}
                    color={getUsageColor()}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                )}
              </Box>

              {usageInfo?.remaining_files !== undefined && usageInfo.remaining_files >= 0 && (
                <Typography variant="body2" color="text.secondary">
                  {usageInfo.remaining_files} files remaining
                </Typography>
              )}

              {getUsagePercentage() >= 90 && usageInfo?.tier_limit !== -1 && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  You're running low on files. Consider upgrading your plan.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Divider sx={{ my: 4 }} />

      {/* Pricing Plans */}
      <PricingPlans 
        currentPlan={subscriptionStatus?.tier}
        onPlanSelect={(plan) => {
          // Handle plan selection if needed
        }}
      />

      {/* Cancel Subscription Dialog */}
      <Dialog open={showCancelDialog} onClose={() => setShowCancelDialog(false)}>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WarningIcon color="warning" />
          Cancel Subscription
        </DialogTitle>
        <DialogContent>
          <Typography mb={2}>
            Are you sure you want to cancel your subscription?
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon>
                <InfoIcon color="info" />
              </ListItemIcon>
              <ListItemText primary="Your access will continue until the end of your billing period" />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <InfoIcon color="info" />
              </ListItemIcon>
              <ListItemText primary="You can reactivate your subscription at any time" />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <WarningIcon color="warning" />
              </ListItemIcon>
              <ListItemText primary="You will lose access to premium features after the billing period ends" />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCancelDialog(false)}>
            Keep Subscription
          </Button>
          <Button
            onClick={handleCancelSubscription}
            color="error"
            variant="contained"
            disabled={cancelling}
          >
            {cancelling ? 'Cancelling...' : 'Cancel Subscription'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Subscription;