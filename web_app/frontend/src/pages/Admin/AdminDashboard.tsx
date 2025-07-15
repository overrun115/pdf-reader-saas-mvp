import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Tab,
  Tabs,
  Alert,
  LinearProgress,
  Button,
  CardActions,
  Container
} from '@mui/material';
import {
  TrendingUp,
  People,
  AttachMoney,
  Description,
  Dashboard as DashboardIcon,
  Storage,
  Speed,
  ManageAccounts,
  Receipt,
  ArrowForward
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts';
import { format, parseISO } from 'date-fns';
import api from '../../services/api';
import toast from 'react-hot-toast';

interface DashboardData {
  users: {
    total: number;
    new_30d: number;
    new_7d: number;
    active_subscriptions: number;
    tier_distribution: Array<{ tier: string; count: number }>;
  };
  files: {
    total: number;
    processed_30d: number;
    processed_7d: number;
    status_distribution: Array<{ status: string; count: number }>;
  };
  recent_activity: {
    recent_files: Array<{
      id: number;
      filename: string;
      user_email: string;
      status: string;
      created_at: string;
    }>;
    recent_users: Array<{
      id: number;
      email: string;
      tier: string;
      subscription_active: boolean;
      created_at: string;
    }>;
  };
  daily_stats: Array<{
    date: string;
    new_users: number;
    files_processed: number;
  }>;
}

interface RevenueData {
  mrr: number;
  arr: number;
  active_subscriptions: number;
  new_subscriptions_30d: number;
  tier_revenue: Array<{
    tier: string;
    users: number;
    monthly_revenue: number;
  }>;
}

interface SystemHealth {
  database: {
    status: string;
    total_tables: string[];
  };
  processing: {
    failed_files_24h: number;
    queue_status: string;
  };
  uptime: string;
}

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [revenueData, setRevenueData] = useState<RevenueData | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      const [dashboardRes, revenueRes, healthRes] = await Promise.all([
        api.get('/management/dashboard'),
        api.get('/management/revenue'),
        api.get('/management/system-health')
      ]);

      setDashboardData(dashboardRes.data);
      setRevenueData(revenueRes.data);
      setSystemHealth(healthRes.data);
    } catch (error) {
      console.error('Error loading admin data:', error);
      toast.error('Failed to load admin dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'success';
      case 'processing': return 'info';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'free': return 'default';
      case 'basic': return 'primary';
      case 'pro': return 'secondary';
      case 'enterprise': return 'warning';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <DashboardIcon /> Admin Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Complete business overview and system management
      </Typography>

      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="Revenue" />
        <Tab label="Users" />
        <Tab label="System Health" />
      </Tabs>

      {/* Overview Tab */}
      {tabValue === 0 && dashboardData && (
        <Box>
          {/* Quick Actions */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <ManageAccounts sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h6" fontWeight={600}>
                        User Management
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Create, edit, and manage user accounts
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    endIcon={<ArrowForward />}
                    onClick={() => navigate('/management/users')}
                  >
                    Manage Users
                  </Button>
                </CardActions>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Receipt sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h6" fontWeight={600}>
                        Transactions
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        View payment history and analytics
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    endIcon={<ArrowForward />}
                    onClick={() => navigate('/management/transactions')}
                  >
                    View Transactions
                  </Button>
                </CardActions>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Storage sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h6" fontWeight={600}>
                        System Health
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Monitor system performance
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    endIcon={<ArrowForward />}
                    onClick={() => setTabValue(3)}
                  >
                    View Status
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>

          {/* Key Metrics Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Total Users
                      </Typography>
                      <Typography variant="h4" fontWeight={700}>
                        {dashboardData.users.total.toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="success.main">
                        +{dashboardData.users.new_30d} this month
                      </Typography>
                    </Box>
                    <People sx={{ fontSize: 40, color: 'primary.main' }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Active Subscriptions
                      </Typography>
                      <Typography variant="h4" fontWeight={700}>
                        {dashboardData.users.active_subscriptions}
                      </Typography>
                      <Typography variant="body2" color="info.main">
                        {((dashboardData.users.active_subscriptions / dashboardData.users.total) * 100).toFixed(1)}% conversion
                      </Typography>
                    </Box>
                    <AttachMoney sx={{ fontSize: 40, color: 'success.main' }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Files Processed
                      </Typography>
                      <Typography variant="h4" fontWeight={700}>
                        {dashboardData.files.total.toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="info.main">
                        +{dashboardData.files.processed_30d} this month
                      </Typography>
                    </Box>
                    <Description sx={{ fontSize: 40, color: 'info.main' }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        MRR
                      </Typography>
                      <Typography variant="h4" fontWeight={700}>
                        {revenueData ? formatCurrency(revenueData.mrr) : '$0'}
                      </Typography>
                      <Typography variant="body2" color="success.main">
                        {revenueData ? formatCurrency(revenueData.arr) : '$0'} ARR
                      </Typography>
                    </Box>
                    <TrendingUp sx={{ fontSize: 40, color: 'success.main' }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Charts */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Growth Trends (Last 30 Days)
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={dashboardData.daily_stats}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={(value) => format(parseISO(value), 'MMM d')}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => format(parseISO(value), 'MMM d, yyyy')}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="new_users" 
                        stroke="#8884d8" 
                        name="New Users"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="files_processed" 
                        stroke="#82ca9d" 
                        name="Files Processed"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    User Tier Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={dashboardData.users.tier_distribution}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ tier, count }) => `${tier}: ${count}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {dashboardData.users.tier_distribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Recent Activity */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Files Processed
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>File</TableCell>
                          <TableCell>User</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Date</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {dashboardData.recent_activity.recent_files.map((file) => (
                          <TableRow key={file.id}>
                            <TableCell>
                              <Typography variant="body2" noWrap>
                                {file.filename.length > 20 
                                  ? `${file.filename.substring(0, 20)}...` 
                                  : file.filename
                                }
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {file.user_email}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip 
                                label={file.status} 
                                color={getStatusColor(file.status)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {format(parseISO(file.created_at), 'MMM d')}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    New Users
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Email</TableCell>
                          <TableCell>Tier</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Joined</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {dashboardData.recent_activity.recent_users.map((user) => (
                          <TableRow key={user.id}>
                            <TableCell>
                              <Typography variant="body2">
                                {user.email}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip 
                                label={user.tier} 
                                color={getTierColor(user.tier)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              <Chip 
                                label={user.subscription_active ? 'Active' : 'Free'} 
                                color={user.subscription_active ? 'success' : 'default'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {format(parseISO(user.created_at), 'MMM d')}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Revenue Tab */}
      {tabValue === 1 && revenueData && (
        <Box>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Revenue by Tier
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={revenueData.tier_revenue}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="tier" />
                      <YAxis />
                      <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                      <Bar dataKey="monthly_revenue" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Revenue Metrics
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Monthly Recurring Revenue
                    </Typography>
                    <Typography variant="h4" fontWeight={700} color="success.main">
                      {formatCurrency(revenueData.mrr)}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Annual Recurring Revenue
                    </Typography>
                    <Typography variant="h5" fontWeight={600}>
                      {formatCurrency(revenueData.arr)}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Active Subscriptions
                    </Typography>
                    <Typography variant="h5" fontWeight={600}>
                      {revenueData.active_subscriptions}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      New Subscriptions (30d)
                    </Typography>
                    <Typography variant="h5" fontWeight={600} color="info.main">
                      {revenueData.new_subscriptions_30d}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Users Tab */}
      {tabValue === 2 && dashboardData && (
        <Box>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Users
                  </Typography>
                  <Typography variant="h4" fontWeight={700}>
                    {dashboardData.users.total.toLocaleString()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Active Subscriptions
                  </Typography>
                  <Typography variant="h4" fontWeight={700} color="success.main">
                    {dashboardData.users.active_subscriptions}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    New Users (30d)
                  </Typography>
                  <Typography variant="h4" fontWeight={700} color="info.main">
                    {dashboardData.users.new_30d}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    New Users (7d)
                  </Typography>
                  <Typography variant="h4" fontWeight={700} color="warning.main">
                    {dashboardData.users.new_7d}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    User Tier Distribution
                  </Typography>
                  <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <PieChart width={300} height={300}>
                      <Pie
                        data={dashboardData.users.tier_distribution}
                        cx={150}
                        cy={150}
                        labelLine={false}
                        label={({ tier, count }) => `${tier}: ${count}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {dashboardData.users.tier_distribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Users
                  </Typography>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>User</TableCell>
                        <TableCell>Tier</TableCell>
                        <TableCell>Joined</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dashboardData.recent_activity.recent_users.map((user) => (
                        <TableRow key={user.id}>
                          <TableCell>{user.email}</TableCell>
                          <TableCell>
                            <Chip 
                              label={user.tier} 
                              size="small" 
                              color={getTierColor(user.tier)}
                            />
                          </TableCell>
                          <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
            <Button 
              variant="contained" 
              size="large"
              startIcon={<ManageAccounts />}
              onClick={() => navigate('/management/users')}
            >
              Go to User Management
            </Button>
          </Box>
        </Box>
      )}

      {/* System Health Tab */}
      {tabValue === 3 && systemHealth && (
        <Box>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Storage /> Database Status
                  </Typography>
                  <Alert 
                    severity={systemHealth.database.status === 'healthy' ? 'success' : 'error'}
                    sx={{ mb: 2 }}
                  >
                    Database: {systemHealth.database.status}
                  </Alert>
                  <Typography variant="body2" color="text.secondary">
                    Tables: {systemHealth.database.total_tables.join(', ')}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Speed /> Processing Status
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Failed Files (24h)
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      {systemHealth.processing.failed_files_24h}
                    </Typography>
                  </Box>
                  <Alert 
                    severity={systemHealth.processing.queue_status === 'active' ? 'success' : 'warning'}
                  >
                    Queue Status: {systemHealth.processing.queue_status}
                  </Alert>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}
    </Container>
  );
};

export default AdminDashboard;