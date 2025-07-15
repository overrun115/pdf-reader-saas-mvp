import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Chip,
  IconButton,
  Divider,
  Container,
  useTheme,
} from '@mui/material';
import {
  CloudUpload,
  GetApp,
  FolderOpen,
  Upgrade,
  CheckCircle,
  Speed,
  Today,
  CalendarToday,
  Timeline,
  AccessTime,
  Assessment,
  Warning,
  Psychology,
  Insights,
  TrendingUp,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import api from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import { dashboardQueryOptions } from '../../config/reactQuery';
import LoginPerformanceMonitor from '../../components/Performance/LoginPerformanceMonitor';

interface DashboardStats {
  user_stats: {
    files_processed_today: number;
    files_processed_this_month: number;
    total_files_processed: number;
    tier: string;
    tier_limit: number;
    remaining_files: number;
  };
  recent_files: Array<{
    id: number;
    original_filename: string;
    status: string;
    tables_found: number;
    created_at: string;
    download_url?: string;
  }>;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const theme = useTheme();

  const { data: dashboardData, isLoading } = useQuery<DashboardStats>(
    'dashboard-stats',
    async () => {
      const response = await api.get('/files/dashboard/stats');
      return response.data;
    },
    dashboardQueryOptions
  );

  const stats = dashboardData?.user_stats;
  const recentFiles = dashboardData?.recent_files || [];

  // AI Predictions data (mock for now, could come from API later)
  const aiPredictions = {
    processing_time: { value: '45s', trend: '+12%', description: 'Estimated time for next document' },
    quality_score: { value: '92%', trend: '+8%', description: 'Predicted output quality' },
    success_rate: { value: '98.5%', trend: '+2%', description: 'Processing success probability' },
    error_risk: { value: '1.5%', trend: '-5%', description: 'Estimated error probability' }
  };

  const getUsagePercentage = () => {
    if (!stats || stats.tier_limit === -1) return 0;
    return (stats.files_processed_this_month / stats.tier_limit) * 100;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'info';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'processing': return '⏳';
      case 'failed': return '❌';
      default: return '📄';
    }
  };

  const getTierBenefits = (tier: string) => {
    const benefits = {
      free: ['5 PDFs/month', 'Excel export', 'Basic support'],
      basic: ['50 PDFs/month', 'All formats', 'Email support'],
      pro: ['200 PDFs/month', 'API access', 'Priority support'],
      enterprise: ['Unlimited', 'Custom features', 'SLA guarantee'],
    };
    return benefits[tier as keyof typeof benefits] || benefits.free;
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box mb={4}>
          <Typography 
            variant="h4" 
            fontWeight={700} 
            gutterBottom
            sx={{ 
              color: 'text.primary',
              fontFamily: 'Montserrat, sans-serif',
            }}
          >
            Welcome back, {user?.full_name?.split(' ')[0]}! 👋
          </Typography>
          <Typography 
            variant="body1" 
            color="text.secondary" 
            gutterBottom
          >
            Here's what's happening with your PDF extractions today.
          </Typography>
        </Box>
      </motion.div>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Files Today
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      {stats?.files_processed_today || 0}
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      Daily progress
                    </Typography>
                  </Box>
                  <Today sx={{ fontSize: 40, color: 'primary.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      This Month
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      {stats?.files_processed_this_month || 0}
                    </Typography>
                    <Typography variant="body2" color="info.main">
                      of {stats?.tier_limit === -1 ? '∞' : stats?.tier_limit} limit
                    </Typography>
                  </Box>
                  <CalendarToday sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Total Processed
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      {stats?.total_files_processed || 0}
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      All time
                    </Typography>
                  </Box>
                  <Timeline sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Processing
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      {recentFiles.filter(f => f.status === 'processing').length}
                    </Typography>
                    <Typography variant="body2" color="warning.main">
                      In queue
                    </Typography>
                  </Box>
                  <Speed sx={{ fontSize: 40, color: 'warning.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* AI Predictions Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography 
              variant="h6" 
              fontWeight={600}
              gutterBottom
              sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
            >
              <Psychology sx={{ fontSize: 24, color: 'primary.main' }} />
              AI Predictions
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ mb: 3 }}
            >
              Smart insights and predictions for your next document processing
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Box 
                  sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    bgcolor: 'primary.50',
                    border: '1px solid',
                    borderColor: 'primary.200',
                    textAlign: 'center'
                  }}
                >
                  <AccessTime sx={{ fontSize: 32, color: 'primary.main', mb: 1 }} />
                  <Typography variant="h5" fontWeight={700} color="primary.main">
                    {aiPredictions.processing_time.value}
                  </Typography>
                  <Typography variant="body2" fontWeight={500} gutterBottom>
                    Processing Time
                  </Typography>
                  <Typography variant="caption" color="success.main" fontWeight={500}>
                    {aiPredictions.processing_time.trend}
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Box 
                  sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    bgcolor: 'success.50',
                    border: '1px solid',
                    borderColor: 'success.200',
                    textAlign: 'center'
                  }}
                >
                  <Assessment sx={{ fontSize: 32, color: 'success.main', mb: 1 }} />
                  <Typography variant="h5" fontWeight={700} color="success.main">
                    {aiPredictions.quality_score.value}
                  </Typography>
                  <Typography variant="body2" fontWeight={500} gutterBottom>
                    Quality Score
                  </Typography>
                  <Typography variant="caption" color="success.main" fontWeight={500}>
                    {aiPredictions.quality_score.trend}
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Box 
                  sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    bgcolor: 'info.50',
                    border: '1px solid',
                    borderColor: 'info.200',
                    textAlign: 'center'
                  }}
                >
                  <CheckCircle sx={{ fontSize: 32, color: 'info.main', mb: 1 }} />
                  <Typography variant="h5" fontWeight={700} color="info.main">
                    {aiPredictions.success_rate.value}
                  </Typography>
                  <Typography variant="body2" fontWeight={500} gutterBottom>
                    Success Rate
                  </Typography>
                  <Typography variant="caption" color="success.main" fontWeight={500}>
                    {aiPredictions.success_rate.trend}
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Box 
                  sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    bgcolor: 'warning.50',
                    border: '1px solid',
                    borderColor: 'warning.200',
                    textAlign: 'center'
                  }}
                >
                  <Warning sx={{ fontSize: 32, color: 'warning.main', mb: 1 }} />
                  <Typography variant="h5" fontWeight={700} color="warning.main">
                    {aiPredictions.error_risk.value}
                  </Typography>
                  <Typography variant="body2" fontWeight={500} gutterBottom>
                    Error Risk
                  </Typography>
                  <Typography variant="caption" color="success.main" fontWeight={500}>
                    {aiPredictions.error_risk.trend}
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            {/* AI Insights */}
            <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
              <Typography 
                variant="subtitle1" 
                fontWeight={600}
                gutterBottom
                sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
              >
                <Insights sx={{ fontSize: 20, color: 'info.main' }} />
                Smart Insights
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1 }}>
                    <TrendingUp sx={{ fontSize: 16, color: 'success.main' }} />
                    <Typography variant="body2">
                      PDFs process 25% faster than Word docs
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1 }}>
                    <Speed sx={{ fontSize: 16, color: 'info.main' }} />
                    <Typography variant="body2">
                      Files under 10MB show better quality
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1 }}>
                    <AccessTime sx={{ fontSize: 16, color: 'warning.main' }} />
                    <Typography variant="body2">
                      Off-peak hours reduce processing time
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </CardContent>
        </Card>
      </motion.div>

      <Grid container spacing={3}>
        {/* Main Content */}
        <Grid item xs={12} lg={8}>
          {/* Usage Overview */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                  <Box>
                    <Typography 
                      variant="h6" 
                      fontWeight={600}
                      gutterBottom
                    >
                      Monthly Usage
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color="text.secondary"
                    >
                      Track your PDF processing usage
                    </Typography>
                  </Box>
                  <Chip
                    label={`${stats?.tier.toUpperCase()} PLAN`}
                    color="primary"
                  />
                </Box>
                
                <Box mb={3}>
                  <Grid container spacing={3} sx={{ mb: 3 }}>
                    <Grid item xs={4}>
                      <Box textAlign="center">
                        <Typography variant="h6" fontWeight={700}>
                          {stats?.files_processed_this_month || 0}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Used
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4}>
                      <Box textAlign="center">
                        <Typography variant="h6" fontWeight={700}>
                          {stats?.tier_limit === -1 ? '∞' : stats?.tier_limit}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Limit
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4}>
                      <Box textAlign="center">
                        <Typography variant="h6" fontWeight={700}>
                          {stats?.remaining_files === -1 ? '∞' : stats?.remaining_files}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Remaining
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Typography variant="body2" color="text.secondary" fontWeight={500}>
                        Usage Progress
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {Math.round(getUsagePercentage())}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={getUsagePercentage()}
                      sx={{ 
                        height: 8, 
                        borderRadius: 4,
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 4,
                        }
                      }}
                    />
                  </Box>
                </Box>
                
                {stats?.tier === 'free' && getUsagePercentage() > 70 && (
                  <Box
                    p={2}
                    sx={{
                      backgroundColor: 'warning.light',
                      borderRadius: 1,
                      border: `1px solid ${theme.palette.warning.main}`,
                    }}
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                  >
                    <Box>
                      <Typography 
                        variant="body1" 
                        fontWeight={600}
                        color="warning.contrastText"
                      >
                        Running low on extractions?
                      </Typography>
                      <Typography 
                        variant="body2" 
                        color="warning.contrastText"
                      >
                        Upgrade to get 50+ PDFs per month
                      </Typography>
                    </Box>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<Upgrade />}
                      onClick={() => navigate('/subscription')}
                      color="warning"
                    >
                      Upgrade
                    </Button>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <Card>
              <CardContent>
                <Typography 
                  variant="h6" 
                  fontWeight={600}
                  gutterBottom
                >
                  Quick Actions
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ mb: 3 }}
                >
                  Get started with common tasks
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Button
                      fullWidth
                      variant="contained"
                      size="large"
                      startIcon={<CloudUpload />}
                      onClick={() => navigate('/upload')}
                      sx={{ py: 1.5 }}
                    >
                      Upload New PDF
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button
                      fullWidth
                      variant="outlined"
                      size="large"
                      startIcon={<FolderOpen />}
                      onClick={() => navigate('/files')}
                      sx={{ py: 1.5 }}
                    >
                      View All Files
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} lg={4}>
          {/* Recent Files */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
          >
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography 
                  variant="h6" 
                  fontWeight={600}
                  gutterBottom
                >
                  Recent Files
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Your latest PDF extractions
                </Typography>
                
                {recentFiles.length === 0 ? (
                  <Box textAlign="center" py={3}>
                    <Typography 
                      variant="body2" 
                      color="text.secondary"
                    >
                      No files processed yet
                    </Typography>
                    <Button
                      variant="text"
                      onClick={() => navigate('/upload')}
                      sx={{ mt: 1 }}
                    >
                      Upload your first PDF
                    </Button>
                  </Box>
                ) : (
                  <List dense>
                    {recentFiles.slice(0, 5).map((file, index) => (
                      <React.Fragment key={file.id}>
                        <ListItem
                          sx={{ px: 0 }}
                          secondaryAction={
                            file.download_url && (
                              <IconButton
                                size="small"
                                onClick={() => window.open(file.download_url, '_blank')}
                              >
                                <GetApp />
                              </IconButton>
                            )
                          }
                        >
                          <ListItemAvatar>
                            <Avatar sx={{ 
                              width: 32, 
                              height: 32, 
                              fontSize: '1rem',
                            }}>
                              {getStatusIcon(file.status)}
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={
                              <Box display="flex" alignItems="center" gap={1}>
                                <Typography 
                                  variant="body2" 
                                  noWrap 
                                  sx={{ 
                                    maxWidth: 140,
                                    fontWeight: 500,
                                  }}
                                >
                                  {file.original_filename}
                                </Typography>
                                <Chip
                                  label={file.status}
                                  size="small"
                                  color={getStatusColor(file.status)}
                                />
                              </Box>
                            }
                            secondary={
                              <Typography variant="caption" color="text.secondary">
                                {file.tables_found} tables • {format(new Date(file.created_at), 'MMM dd')}
                              </Typography>
                            }
                          />
                        </ListItem>
                        {index < recentFiles.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Plan Benefits */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography 
                  variant="h6" 
                  fontWeight={600}
                  gutterBottom
                >
                  Your Plan
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Current subscription benefits
                </Typography>
                
                <Chip
                  label={`${stats?.tier.toUpperCase()} PLAN`}
                  color="primary"
                  sx={{ mb: 2 }}
                />
                
                <Box>
                  {getTierBenefits(stats?.tier || 'free').map((benefit, index) => (
                    <Box key={index} display="flex" alignItems="center" gap={1} sx={{ mb: 1 }}>
                      <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                      <Typography 
                        variant="body2"
                        fontWeight={500}
                      >
                        {benefit}
                      </Typography>
                    </Box>
                  ))}
                </Box>
                
                {stats?.tier === 'free' && (
                  <Button
                    fullWidth
                    variant="outlined"
                    size="small"
                    onClick={() => navigate('/subscription')}
                    sx={{ mt: 2 }}
                  >
                    Upgrade Plan
                  </Button>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Performance Monitor */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.9 }}
          >
            <Card>
              <CardContent>
                <LoginPerformanceMonitor />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;