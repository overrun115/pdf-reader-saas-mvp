import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  Stack,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  useTheme,
} from '@mui/material';
import {
  CheckCircle,
  Speed,
  Security,
  TableChart,
  AttachMoney,
  AutoAwesome,
  Api,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

// Animation variants
const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

const Landing: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  const features = [
    {
      icon: <AutoAwesome />,
      title: 'Intelligent Column Mapping',
      description: 'AI automatically maps numbered columns to descriptive names across pages',
      unique: true,
    },
    {
      icon: <TableChart />,
      title: 'Smart Table Preview',
      description: 'See extracted tables before processing with ML-powered suggestions',
    },
    {
      icon: <Speed />,
      title: 'Lightning Fast',
      description: 'Process PDFs in 30-60 seconds with our optimized extraction engine',
    },
    {
      icon: <AttachMoney />,
      title: '10x Cheaper',
      description: 'Starting at $0.002/page vs competitors at $0.50/page',
    },
    {
      icon: <Security />,
      title: 'Secure & Private',
      description: 'Your data is encrypted and automatically deleted after 30 days',
    },
    {
      icon: <Api />,
      title: 'Developer-Friendly API',
      description: 'REST API with webhooks, perfect for automation and integrations',
    },
  ];

  const competitors = [
    {
      name: 'Docsumo',
      price: '$500/month',
      pages: '1,000 pages',
      limitations: ['Manual column mapping', 'Complex setup', 'Enterprise-only'],
    },
    {
      name: 'Amazon Textract',
      price: '$15/month',
      pages: '1,000 pages',
      limitations: ['AWS knowledge required', 'Complex integration', 'No preview'],
    },
    {
      name: 'Our Solution',
      price: '$9/month',
      pages: '50 PDFs (~2,500 pages)',
      limitations: [],
      highlight: true,
    },
  ];

  return (
    <Box sx={{ background: 'background.default' }}>
      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ pt: 14, pb: 14 }}>
        <motion.div {...fadeInUp}>
          <Box textAlign="center">
            <Chip
              label="NEW: Intelligent Column Mapping"
              size="small"
              variant="outlined"
              sx={{
                mb: 3,
                borderColor: 'divider',
                color: 'text.secondary',
                fontWeight: 400,
                fontSize: '0.75rem',
                height: 24,
              }}
            />
            <Typography 
              variant="h1" 
              component="h1" 
              gutterBottom
              sx={{ 
                color: 'text.primary',
                fontWeight: 700,
                mb: 2,
                lineHeight: 1.1,
                fontSize: { xs: '2rem', md: '2.5rem' },
              }}
            >
              Extract PDF Tables with AI Precision
            </Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                mb: 4, 
                color: 'text.secondary',
                maxWidth: 600, 
                mx: 'auto',
                fontSize: '1.125rem',
                lineHeight: 1.5,
              }}
            >
              The only PDF table extractor with intelligent column mapping. 
              10x cheaper than competitors, infinitely smarter.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center" sx={{ mb: 4 }}>
              <Button
                variant="contained"
                onClick={() => navigate('/try-demo')}
                sx={{
                  bgcolor: 'text.primary',
                  color: 'background.default',
                  '&:hover': { 
                    bgcolor: 'text.secondary',
                  },
                  px: 3,
                  py: 1.5,
                }}
              >
                Try now
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/pricing')}
                sx={{
                  borderColor: 'divider',
                  color: 'text.secondary',
                  '&:hover': { 
                    borderColor: 'text.secondary',
                    color: 'text.primary',
                  },
                  px: 3,
                  py: 1.5,
                }}
              >
                View pricing
              </Button>
            </Stack>
            
            <Typography variant="body2" sx={{ color: 'text.disabled' }}>
              No registration required • 3 free PDFs to start
            </Typography>
          </Box>
        </motion.div>
      </Container>

      {/* Features Section */}
      <Box sx={{ py: 14 }}>
        <Container maxWidth="lg">
          <motion.div {...staggerContainer} initial="initial" animate="animate">
            <Typography
              variant="h2"
              textAlign="center"
              gutterBottom
              sx={{ 
                color: 'text.primary',
                mb: 2,
                fontWeight: 600,
                fontSize: '1.75rem',
              }}
            >
              Features
            </Typography>
            <Typography
              variant="body1"
              textAlign="center"
              sx={{ 
                color: 'text.secondary',
                mb: 14,
                maxWidth: 500,
                mx: 'auto',
              }}
            >
              Everything you need to extract and process PDF tables efficiently
            </Typography>
            <Grid container spacing={4}>
              {features.map((feature, index) => (
                <Grid item xs={12} md={6} lg={4} key={index}>
                  <motion.div {...fadeInUp}>
                    <Box
                      sx={{
                        p: 4,
                        height: '100%',
                        borderRadius: 1,
                        border: '1px solid',
                        borderColor: 'divider',
                        bgcolor: 'background.paper',
                        transition: 'border-color 0.15s ease-in-out',
                        '&:hover': {
                          borderColor: 'text.disabled',
                        },
                      }}
                    >
                      <Box 
                        sx={{ 
                          color: 'text.secondary', 
                          mb: 3,
                          '& svg': {
                            fontSize: 24,
                          }
                        }}
                      >
                        {feature.icon}
                      </Box>
                      <Typography 
                        variant="h6" 
                        gutterBottom 
                        sx={{ 
                          fontWeight: 500,
                          color: 'text.primary',
                          mb: 2,
                          fontSize: '1rem',
                        }}
                      >
                        {feature.title}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: 'text.secondary',
                          lineHeight: 1.5,
                        }}
                      >
                        {feature.description}
                      </Typography>
                    </Box>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </motion.div>
        </Container>
      </Box>

      {/* Comparison Section */}
      <Container maxWidth="lg" sx={{ py: 14 }}>
        <motion.div {...fadeInUp}>
          <Typography
            variant="h2"
            textAlign="center"
            gutterBottom
            sx={{ 
              color: 'text.primary',
              mb: 3,
              fontWeight: 700,
            }}
          >
            See How We Stack Up
          </Typography>
          <Typography
            variant="h6"
            textAlign="center"
            sx={{ 
              color: 'text.secondary',
              mb: 8,
              maxWidth: 600,
              mx: 'auto',
              fontWeight: 400,
            }}
          >
            Compare our solution with leading competitors in the market
          </Typography>
          <Grid container spacing={4}>
            {competitors.map((competitor, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 4,
                    height: '100%',
                    border: competitor.highlight ? '2px solid' : '1px solid',
                    borderColor: competitor.highlight ? 'primary.main' : 'divider',
                    position: 'relative',
                    background: 'background.paper',
                    borderRadius: 3,
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: competitor.highlight 
                        ? theme.palette.mode === 'dark'
                          ? '0 12px 40px rgba(51, 153, 255, 0.3)'
                          : '0 12px 40px rgba(0, 102, 255, 0.2)'
                        : theme.palette.mode === 'dark'
                          ? '0 8px 32px rgba(0, 0, 0, 0.5)'
                          : '0 8px 32px rgba(0, 0, 0, 0.12)',
                    },
                    transition: 'all 0.3s ease-in-out',
                  }}
                >
                  {competitor.highlight && (
                    <Chip
                      label="RECOMMENDED"
                      sx={{
                        position: 'absolute',
                        top: -12,
                        left: '50%',
                        transform: 'translateX(-50%)',
                        bgcolor: 'primary.main',
                        color: 'primary.contrastText',
                        fontWeight: 'bold',
                      }}
                    />
                  )}
                  <Typography 
                    variant="h4" 
                    fontWeight={700} 
                    gutterBottom
                    sx={{ 
                      color: 'text.primary',
                      mt: 2,
                    }}
                  >
                    {competitor.name}
                  </Typography>
                  <Typography 
                    variant="h5" 
                    gutterBottom
                    sx={{ 
                      color: competitor.highlight ? 'primary.main' : 'text.secondary',
                      fontWeight: 600,
                      mb: 1,
                    }}
                  >
                    {competitor.price}
                  </Typography>
                  <Typography 
                    variant="body1" 
                    gutterBottom
                    sx={{ 
                      color: 'text.secondary',
                      mb: 3,
                    }}
                  >
                    {competitor.pages}
                  </Typography>
                  
                  {competitor.limitations.length > 0 ? (
                    <List dense sx={{ mt: 2 }}>
                      {competitor.limitations.map((limitation, idx) => (
                        <ListItem key={idx} sx={{ px: 0, py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 36 }}>
                            <Box sx={{ color: 'error.main', fontSize: 18, fontWeight: 'bold' }}>✗</Box>
                          </ListItemIcon>
                          <ListItemText 
                            primary={limitation}
                            sx={{ 
                              '& .MuiListItemText-primary': { 
                                color: 'text.secondary',
                                fontSize: '0.95rem',
                              } 
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <List dense sx={{ mt: 2 }}>
                      <ListItem sx={{ px: 0, py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckCircle sx={{ color: 'success.main', fontSize: 20 }} />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Intelligent column mapping"
                          sx={{ 
                            '& .MuiListItemText-primary': { 
                              color: 'text.primary',
                              fontSize: '0.95rem',
                              fontWeight: 500,
                            } 
                          }}
                        />
                      </ListItem>
                      <ListItem sx={{ px: 0, py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckCircle sx={{ color: 'success.main', fontSize: 20 }} />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Smart table preview"
                          sx={{ 
                            '& .MuiListItemText-primary': { 
                              color: 'text.primary',
                              fontSize: '0.95rem',
                              fontWeight: 500,
                            } 
                          }}
                        />
                      </ListItem>
                      <ListItem sx={{ px: 0, py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckCircle sx={{ color: 'success.main', fontSize: 20 }} />
                        </ListItemIcon>
                        <ListItemText 
                          primary="1-click setup"
                          sx={{ 
                            '& .MuiListItemText-primary': { 
                              color: 'text.primary',
                              fontSize: '0.95rem',
                              fontWeight: 500,
                            } 
                          }}
                        />
                      </ListItem>
                    </List>
                  )}
                </Paper>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Container>

      {/* CTA Section */}
      <Box sx={{ py: 14 }}>
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <motion.div {...fadeInUp}>
            <Typography 
              variant="h2" 
              gutterBottom 
              sx={{ 
                color: 'text.primary',
                fontWeight: 700,
                mb: 3,
              }}
            >
              Ready to Extract Smarter?
            </Typography>
            <Typography 
              variant="h6" 
              sx={{ 
                mb: 6, 
                color: 'text.secondary',
                maxWidth: 500,
                mx: 'auto',
                fontWeight: 400,
                lineHeight: 1.6,
              }}
            >
              Join thousands of users who've already discovered the power of intelligent table extraction.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} justifyContent="center" sx={{ mb: 4 }}>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/register')}
                sx={{
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  '&:hover': { 
                    bgcolor: 'primary.dark',
                    transform: 'translateY(-2px)',
                  },
                  fontSize: '1.1rem',
                  py: 2,
                  px: 5,
                  fontWeight: 600,
                  minWidth: 200,
                }}
              >
                Start Your Free Trial
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/try-demo')}
                sx={{
                  borderColor: 'primary.main',
                  color: 'primary.main',
                  '&:hover': { 
                    borderColor: 'primary.dark', 
                    color: 'primary.dark',
                    bgcolor: theme.palette.mode === 'dark' ? 'primary.dark' : 'rgba(0, 102, 255, 0.05)'
                  },
                  fontSize: '1.1rem',
                  py: 2,
                  px: 5,
                  fontWeight: 600,
                  minWidth: 200,
                }}
              >
                Try Demo First
              </Button>
            </Stack>
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'text.disabled',
                maxWidth: 400,
                mx: 'auto',
              }}
            >
              No credit card required • 5 PDFs included • Cancel anytime
            </Typography>
          </motion.div>
        </Container>
      </Box>
    </Box>
  );
};

export default Landing;