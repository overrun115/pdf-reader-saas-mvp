import React from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Switch,
  FormControlLabel,
} from '@mui/material';
import { CheckCircle } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const Pricing: React.FC = () => {
  const [yearly, setYearly] = React.useState(false);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  const plans = [
    {
      name: 'Free',
      price: { monthly: 0, yearly: 0 },
      description: 'Perfect for getting started',
      features: [
        '5 PDFs per month',
        'Excel export only',
        'Basic support',
        'Email notifications',
        'File history (7 days)',
      ],
      limits: {
        files: 5,
        api: false,
        priority: false,
        storage: '7 days',
      },
      popular: false,
      current: false,
    },
    {
      name: 'Basic',
      price: { monthly: 9, yearly: 90 },
      description: 'For individuals and small teams',
      features: [
        '50 PDFs per month',
        'All export formats (Excel, CSV)',
        'Email support',
        'Advanced table preview',
        'File history (30 days)',
        'Batch processing',
      ],
      limits: {
        files: 50,
        api: false,
        priority: false,
        storage: '30 days',
      },
      popular: true,
      current: false,
    },
    {
      name: 'Pro',
      price: { monthly: 29, yearly: 290 },
      description: 'For growing businesses',
      features: [
        '200 PDFs per month',
        'All export formats',
        'Priority support',
        'API access (10,000 requests/month)',
        'File history (90 days)',
        'Advanced analytics',
        'Webhook integrations',
        'Custom extraction templates',
      ],
      limits: {
        files: 200,
        api: true,
        priority: true,
        storage: '90 days',
      },
      popular: false,
      current: false,
    },
    {
      name: 'Enterprise',
      price: { monthly: 99, yearly: 990 },
      description: 'For large organizations',
      features: [
        'Unlimited PDFs',
        'All export formats',
        'Priority support + SLA',
        'Unlimited API requests',
        'Unlimited file history',
        'Advanced analytics + reporting',
        'Custom integrations',
        'Dedicated account manager',
        'On-premise deployment option',
        'Custom training & onboarding',
      ],
      limits: {
        files: -1,
        api: true,
        priority: true,
        storage: 'Unlimited',
      },
      popular: false,
      current: false,
    },
  ];

  const competitors = [
    {
      name: 'Our Solution',
      basic: '$9/month',
      pro: '$29/month',
      enterprise: '$99/month',
      features: ['Intelligent mapping', 'Real-time preview', 'API included'],
      highlight: true,
    },
    {
      name: 'Docsumo',
      basic: 'N/A',
      pro: '$500/month',
      enterprise: '$1000+/month',
      features: ['Manual setup', 'No preview', 'Enterprise only'],
    },
    {
      name: 'Amazon Textract',
      basic: 'N/A',
      pro: '$45/month*',
      enterprise: '$200+/month*',
      features: ['AWS knowledge required', 'Complex integration', 'No UI'],
    },
    {
      name: 'PDFTables',
      basic: '$20/month',
      pro: '$50/month',
      enterprise: 'Custom',
      features: ['Limited features', 'No batch processing', 'Basic API'],
    },
  ];

  const handleGetStarted = (planName: string) => {
    if (!isAuthenticated) {
      navigate('/register');
    } else {
      // TODO: Implement subscription upgrade
      console.log(`Upgrading to ${planName}`);
    }
  };

  return (
    <Box sx={{ py: 8 }}>
      <Container maxWidth="lg">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Box textAlign="center" mb={6}>
            <Typography variant="h2" fontWeight={700} gutterBottom>
              Simple, Transparent Pricing
            </Typography>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Choose the plan that's right for you. Upgrade or downgrade at any time.
            </Typography>
            
            {/* Annual Toggle */}
            <Box display="flex" justifyContent="center" alignItems="center" mt={3}>
              <Typography variant="body1" sx={{ mr: 2 }}>
                Monthly
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={yearly}
                    onChange={(e) => setYearly(e.target.checked)}
                    color="primary"
                  />
                }
                label=""
              />
              <Typography variant="body1" sx={{ ml: 2 }}>
                Yearly
              </Typography>
              <Chip
                label="Save 17%"
                color="success"
                size="small"
                sx={{ ml: 1 }}
              />
            </Box>
          </Box>
        </motion.div>

        {/* Pricing Cards */}
        <Grid container spacing={3} sx={{ mb: 8 }}>
          {plans.map((plan, index) => (
            <Grid item xs={12} md={6} lg={3} key={plan.name}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    position: 'relative',
                    border: plan.popular ? '2px solid' : '1px solid',
                    borderColor: plan.popular ? 'primary.main' : 'divider',
                    '&:hover': {
                      boxShadow: (theme) => theme.shadows[8],
                      transform: 'translateY(-4px)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  {plan.popular && (
                    <Chip
                      label="Most Popular"
                      color="primary"
                      sx={{
                        position: 'absolute',
                        top: -12,
                        left: '50%',
                        transform: 'translateX(-50%)',
                        fontWeight: 600,
                      }}
                    />
                  )}
                  
                  <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <Box textAlign="center" mb={3}>
                      <Typography variant="h5" fontWeight={600} gutterBottom>
                        {plan.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {plan.description}
                      </Typography>
                      
                      <Box display="flex" alignItems="baseline" justifyContent="center" mt={2}>
                        <Typography variant="h3" fontWeight={700} color="primary">
                          ${yearly ? plan.price.yearly : plan.price.monthly}
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ ml: 1 }}>
                          /{yearly ? 'year' : 'month'}
                        </Typography>
                      </Box>
                      
                      {yearly && plan.price.monthly > 0 && (
                        <Typography variant="caption" color="text.secondary">
                          ${plan.price.monthly}/month billed annually
                        </Typography>
                      )}
                    </Box>

                    <List dense sx={{ flexGrow: 1 }}>
                      {plan.features.map((feature, idx) => (
                        <ListItem key={idx} sx={{ px: 0, py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <CheckCircle color="success" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText
                            primary={feature}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    <Button
                      fullWidth
                      variant={plan.popular ? 'contained' : 'outlined'}
                      size="large"
                      onClick={() => handleGetStarted(plan.name)}
                      sx={{ mt: 2 }}
                    >
                      {plan.name === 'Free' ? 'Get Started' : 'Choose Plan'}
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* Feature Comparison */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <Typography variant="h4" textAlign="center" fontWeight={600} gutterBottom>
            Compare Plans
          </Typography>
          <Typography variant="body1" textAlign="center" color="text.secondary" sx={{ mb: 4 }}>
            Detailed feature comparison across all plans
          </Typography>

          <TableContainer component={Paper} sx={{ mb: 6 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Feature</TableCell>
                  <TableCell align="center">Free</TableCell>
                  <TableCell align="center">Basic</TableCell>
                  <TableCell align="center">Pro</TableCell>
                  <TableCell align="center">Enterprise</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>PDFs per month</TableCell>
                  <TableCell align="center">5</TableCell>
                  <TableCell align="center">50</TableCell>
                  <TableCell align="center">200</TableCell>
                  <TableCell align="center">Unlimited</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Export formats</TableCell>
                  <TableCell align="center">Excel</TableCell>
                  <TableCell align="center">Excel, CSV</TableCell>
                  <TableCell align="center">All formats</TableCell>
                  <TableCell align="center">All formats</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>API access</TableCell>
                  <TableCell align="center">❌</TableCell>
                  <TableCell align="center">❌</TableCell>
                  <TableCell align="center">✅</TableCell>
                  <TableCell align="center">✅</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Priority processing</TableCell>
                  <TableCell align="center">❌</TableCell>
                  <TableCell align="center">❌</TableCell>
                  <TableCell align="center">✅</TableCell>
                  <TableCell align="center">✅</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>File storage</TableCell>
                  <TableCell align="center">7 days</TableCell>
                  <TableCell align="center">30 days</TableCell>
                  <TableCell align="center">90 days</TableCell>
                  <TableCell align="center">Unlimited</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Support</TableCell>
                  <TableCell align="center">Basic</TableCell>
                  <TableCell align="center">Email</TableCell>
                  <TableCell align="center">Priority</TableCell>
                  <TableCell align="center">SLA + Dedicated</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </motion.div>

        {/* Competitor Comparison */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <Typography variant="h4" textAlign="center" fontWeight={600} gutterBottom>
            How We Compare
          </Typography>
          <Typography variant="body1" textAlign="center" color="text.secondary" sx={{ mb: 4 }}>
            See why we're the smarter choice for PDF table extraction
          </Typography>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Provider</TableCell>
                  <TableCell align="center">Basic Plan</TableCell>
                  <TableCell align="center">Pro Plan</TableCell>
                  <TableCell align="center">Enterprise</TableCell>
                  <TableCell>Key Features</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {competitors.map((competitor) => (
                  <TableRow
                    key={competitor.name}
                    sx={{
                      bgcolor: competitor.highlight ? 'rgba(102, 126, 234, 0.05)' : 'transparent',
                    }}
                  >
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography fontWeight={600}>
                          {competitor.name}
                        </Typography>
                        {competitor.highlight && (
                          <Chip label="US" color="primary" size="small" />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600 }}>
                      {competitor.basic}
                    </TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600 }}>
                      {competitor.pro}
                    </TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600 }}>
                      {competitor.enterprise}
                    </TableCell>
                    <TableCell>
                      <Box component="ul" sx={{ m: 0, pl: 2 }}>
                        {competitor.features.map((feature, idx) => (
                          <li key={idx}>
                            <Typography variant="body2">{feature}</Typography>
                          </li>
                        ))}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.7 }}
        >
          <Box textAlign="center" mt={8} p={4} bgcolor="rgba(102, 126, 234, 0.05)" borderRadius={2}>
            <Typography variant="h4" fontWeight={600} gutterBottom>
              Ready to Get Started?
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Join thousands of users who trust our platform for PDF table extraction
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/register')}
              sx={{ mr: 2 }}
            >
              Start Free Trial
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/contact')}
            >
              Contact Sales
            </Button>
          </Box>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Pricing;