import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Check as CheckIcon,
  Star as StarIcon,
  Upgrade as UpgradeIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { subscriptionAPI, SubscriptionPlan, SubscriptionStatus } from '../../services/subscriptionApi';
import toast from 'react-hot-toast';

interface PricingPlansProps {
  onPlanSelect?: (plan: SubscriptionPlan) => void;
  currentPlan?: string;
  showCurrentPlan?: boolean;
}

const PricingPlans: React.FC<PricingPlansProps> = ({
  onPlanSelect,
  currentPlan,
  showCurrentPlan = true
}) => {
  const theme = useTheme();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [upgrading, setUpgrading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [plansData, statusData] = await Promise.all([
        subscriptionAPI.getSubscriptionPlans(),
        subscriptionAPI.getSubscriptionStatus()
      ]);
      setPlans(plansData);
      setSubscriptionStatus(statusData);
    } catch (err) {
      setError('Failed to load subscription data');
      console.error('Error loading subscription data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePlanSelect = (plan: SubscriptionPlan) => {
    if (plan.tier === 'free') {
      toast.error('You are already on the free plan');
      return;
    }

    if (subscriptionStatus?.tier === plan.tier) {
      toast.success('You are already on this plan');
      return;
    }

    setSelectedPlan(plan);
    setConfirmDialogOpen(true);
  };

  const handleUpgrade = async () => {
    if (!selectedPlan) return;

    try {
      setUpgrading(true);
      
      const successUrl = `${window.location.origin}/subscription/success`;
      const cancelUrl = `${window.location.origin}/subscription`;
      
      const checkoutResponse = await subscriptionAPI.createCheckoutSession({
        price_id: selectedPlan.price_id,
        success_url: successUrl,
        cancel_url: cancelUrl
      });

      // Redirect to Stripe Checkout
      window.location.href = checkoutResponse.checkout_url;
      
    } catch (err) {
      toast.error('Failed to create checkout session');
      console.error('Checkout error:', err);
    } finally {
      setUpgrading(false);
      setConfirmDialogOpen(false);
    }
  };

  const getButtonText = (plan: SubscriptionPlan) => {
    if (plan.tier === 'free') {
      return 'Current Plan';
    }
    
    if (subscriptionStatus?.tier === plan.tier) {
      return 'Current Plan';
    }
    
    return 'Upgrade';
  };

  const getButtonColor = (plan: SubscriptionPlan) => {
    if (subscriptionStatus?.tier === plan.tier) {
      return 'success' as const;
    }
    return 'primary' as const;
  };

  const isCurrentPlan = (plan: SubscriptionPlan) => {
    return subscriptionStatus?.tier === plan.tier;
  };

  const isPlanDisabled = (plan: SubscriptionPlan) => {
    return plan.tier === 'free' || isCurrentPlan(plan);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h2" gutterBottom align="center" fontWeight={600}>
        Choose Your Plan
      </Typography>
      <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
        Upgrade to unlock more features and increase your processing limits
      </Typography>

      <Grid container spacing={3} justifyContent="center">
        {plans.map((plan, index) => (
          <Grid item xs={12} sm={6} md={3} key={plan.tier}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                border: isCurrentPlan(plan) ? `2px solid ${theme.palette.primary.main}` : '1px solid',
                borderColor: isCurrentPlan(plan) ? 'primary.main' : 'divider',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: plan.tier !== 'free' ? 'translateY(-4px)' : 'none',
                  boxShadow: plan.tier !== 'free' ? theme.shadows[8] : 'none'
                }
              }}
            >
              {plan.tier === 'pro' && (
                <Chip
                  label="Most Popular"
                  color="primary"
                  size="small"
                  icon={<StarIcon />}
                  sx={{
                    position: 'absolute',
                    top: -12,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    zIndex: 1
                  }}
                />
              )}

              {isCurrentPlan(plan) && (
                <Chip
                  label="Current Plan"
                  color="success"
                  size="small"
                  sx={{
                    position: 'absolute',
                    top: 16,
                    right: 16,
                    zIndex: 1
                  }}
                />
              )}

              <CardContent sx={{ flexGrow: 1, p: 3 }}>
                <Typography variant="h5" component="h3" gutterBottom fontWeight={600}>
                  {plan.name}
                </Typography>
                
                <Box display="flex" alignItems="baseline" mb={2}>
                  <Typography variant="h3" component="span" fontWeight="bold">
                    ${plan.price}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" ml={1}>
                    /month
                  </Typography>
                </Box>

                <Typography variant="body2" color="text.secondary" mb={3}>
                  {plan.files_per_month === -1 
                    ? 'Unlimited files per month' 
                    : `${plan.files_per_month} files per month`
                  }
                </Typography>

                <List dense sx={{ mb: 3 }}>
                  {plan.features.map((feature, idx) => (
                    <ListItem key={idx} sx={{ px: 0, py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <CheckIcon color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={feature}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>

                <Button
                  variant={isCurrentPlan(plan) ? "outlined" : "contained"}
                  color={getButtonColor(plan)}
                  fullWidth
                  size="large"
                  disabled={isPlanDisabled(plan) || upgrading}
                  onClick={() => handlePlanSelect(plan)}
                  startIcon={!isCurrentPlan(plan) && <UpgradeIcon />}
                  sx={{ mt: 'auto' }}
                >
                  {getButtonText(plan)}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Confirmation Dialog */}
      <Dialog open={confirmDialogOpen} onClose={() => setConfirmDialogOpen(false)}>
        <DialogTitle>Confirm Plan Upgrade</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to upgrade to the {selectedPlan?.name} for ${selectedPlan?.price}/month?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            You will be redirected to Stripe to complete the payment.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleUpgrade}
            variant="contained"
            disabled={upgrading}
            startIcon={upgrading ? <CircularProgress size={16} /> : <UpgradeIcon />}
          >
            {upgrading ? 'Processing...' : 'Upgrade Now'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PricingPlans;