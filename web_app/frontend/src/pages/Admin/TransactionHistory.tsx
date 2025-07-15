import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Pagination,
  Grid,
  Card,
  CardContent,
  Divider,
  Container
} from '@mui/material';
import {
  Search,
  Visibility,
  FilterList,
  FileDownload,
  TrendingUp,
  AccountBalanceWallet,
  Receipt,
  AttachMoney
} from '@mui/icons-material';
import { format, parseISO, startOfMonth, endOfMonth } from 'date-fns';
import api from '../../services/api';
import toast from 'react-hot-toast';

interface Transaction {
  id: string;
  user_id: number;
  user_name: string;
  user_email: string;
  amount: number;
  currency: string;
  status: string;
  payment_method: string;
  stripe_payment_intent_id?: string;
  stripe_subscription_id?: string;
  subscription_tier: string;
  billing_period: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

interface TransactionStats {
  total_revenue: number;
  monthly_revenue: number;
  total_transactions: number;
  successful_transactions: number;
  failed_transactions: number;
  average_transaction_value: number;
}

const TransactionHistory: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<TransactionStats | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 50,
    total: 0,
    pages: 0
  });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [tierFilter, setTierFilter] = useState('');
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  useEffect(() => {
    loadTransactions();
    loadStats();
  }, [pagination.page, searchTerm, statusFilter, tierFilter]);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        limit: pagination.limit.toString()
      });

      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter) params.append('status', statusFilter);
      if (tierFilter) params.append('tier', tierFilter);

      const response = await api.get(`/management/transactions?${params.toString()}`);
      const data = response.data;

      setTransactions(data.transactions);
      setPagination(prev => ({
        ...prev,
        total: data.pagination.total,
        pages: data.pagination.pages
      }));
    } catch (error) {
      console.error('Error loading transactions:', error);
      toast.error('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/management/transactions/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error loading transaction stats:', error);
    }
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleStatusFilter = (event: any) => {
    setStatusFilter(event.target.value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleTierFilter = (event: any) => {
    setTierFilter(event.target.value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, page: number) => {
    setPagination(prev => ({ ...prev, page }));
  };

  const handleViewDetails = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setDetailDialogOpen(true);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'succeeded':
      case 'completed':
        return 'success';
      case 'pending':
      case 'processing':
        return 'warning';
      case 'failed':
      case 'canceled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'basic': return 'primary';
      case 'pro': return 'secondary';
      case 'enterprise': return 'warning';
      default: return 'default';
    }
  };

  const formatAmount = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount / 100); // Assuming amounts are in cents
  };

  const exportTransactions = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter) params.append('status', statusFilter);
      if (tierFilter) params.append('tier', tierFilter);

      const response = await api.get(`/management/transactions/export?${params.toString()}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `transactions_${format(new Date(), 'yyyy-MM-dd')}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('Transactions exported successfully');
    } catch (error) {
      console.error('Error exporting transactions:', error);
      toast.error('Failed to export transactions');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Transaction History
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Monitor payments, subscriptions, and revenue analytics
      </Typography>

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <AttachMoney sx={{ color: 'success.main', mr: 1 }} />
                  <Typography color="text.secondary" variant="body2">
                    Total Revenue
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight={700} color="success.main">
                  {formatAmount(stats.total_revenue)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <TrendingUp sx={{ color: 'info.main', mr: 1 }} />
                  <Typography color="text.secondary" variant="body2">
                    Monthly Revenue
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight={700} color="info.main">
                  {formatAmount(stats.monthly_revenue)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Receipt sx={{ color: 'primary.main', mr: 1 }} />
                  <Typography color="text.secondary" variant="body2">
                    Total Transactions
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight={700}>
                  {stats.total_transactions.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {stats.successful_transactions} successful
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <AccountBalanceWallet sx={{ color: 'secondary.main', mr: 1 }} />
                  <Typography color="text.secondary" variant="body2">
                    Average Value
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight={700} color="secondary.main">
                  {formatAmount(stats.average_transaction_value)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filters and Actions */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        <TextField
          placeholder="Search by user, email, or transaction ID..."
          value={searchTerm}
          onChange={handleSearch}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 300 }}
        />
        
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={statusFilter}
            label="Status"
            onChange={handleStatusFilter}
          >
            <MenuItem value="">All Status</MenuItem>
            <MenuItem value="succeeded">Succeeded</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="failed">Failed</MenuItem>
            <MenuItem value="canceled">Canceled</MenuItem>
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Tier</InputLabel>
          <Select
            value={tierFilter}
            label="Tier"
            onChange={handleTierFilter}
          >
            <MenuItem value="">All Tiers</MenuItem>
            <MenuItem value="basic">Basic</MenuItem>
            <MenuItem value="pro">Pro</MenuItem>
            <MenuItem value="enterprise">Enterprise</MenuItem>
          </Select>
        </FormControl>

        <Button
          variant="outlined"
          startIcon={<FilterList />}
          onClick={loadTransactions}
        >
          Refresh
        </Button>

        <Button
          variant="contained"
          startIcon={<FileDownload />}
          onClick={exportTransactions}
          sx={{ ml: 'auto' }}
        >
          Export CSV
        </Button>
      </Box>

      {/* Transactions Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Transaction ID</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Tier</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Payment Method</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transactions.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {transaction.id.slice(0, 8)}...
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        {transaction.user_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {transaction.user_email}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600} color="success.main">
                      {formatAmount(transaction.amount, transaction.currency)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {transaction.billing_period}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={transaction.subscription_tier.toUpperCase()} 
                      color={getTierColor(transaction.subscription_tier)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={transaction.status.toUpperCase()} 
                      color={getStatusColor(transaction.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {transaction.payment_method}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {format(parseISO(transaction.created_at), 'MMM d, yyyy')}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {format(parseISO(transaction.created_at), 'HH:mm')}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      onClick={() => handleViewDetails(transaction)}
                      size="small"
                    >
                      <Visibility />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
          <Pagination
            count={pagination.pages}
            page={pagination.page}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      </Paper>

      {/* Transaction Details Dialog */}
      <Dialog open={detailDialogOpen} onClose={() => setDetailDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Transaction Details</DialogTitle>
        <DialogContent>
          {selectedTransaction && (
            <Box sx={{ pt: 1 }}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Transaction Information
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Transaction ID</Typography>
                    <Typography variant="body2" fontFamily="monospace">{selectedTransaction.id}</Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Amount</Typography>
                    <Typography variant="h6" color="success.main">
                      {formatAmount(selectedTransaction.amount, selectedTransaction.currency)}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Status</Typography>
                    <Chip 
                      label={selectedTransaction.status.toUpperCase()} 
                      color={getStatusColor(selectedTransaction.status)}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Payment Method</Typography>
                    <Typography variant="body2">{selectedTransaction.payment_method}</Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    User Information
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">User</Typography>
                    <Typography variant="body2">{selectedTransaction.user_name}</Typography>
                    <Typography variant="body2" color="text.secondary">{selectedTransaction.user_email}</Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Subscription Tier</Typography>
                    <Chip 
                      label={selectedTransaction.subscription_tier.toUpperCase()} 
                      color={getTierColor(selectedTransaction.subscription_tier)}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Billing Period</Typography>
                    <Typography variant="body2">{selectedTransaction.billing_period}</Typography>
                  </Box>
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Stripe Information
                  </Typography>
                  {selectedTransaction.stripe_payment_intent_id && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">Payment Intent ID</Typography>
                      <Typography variant="body2" fontFamily="monospace">
                        {selectedTransaction.stripe_payment_intent_id}
                      </Typography>
                    </Box>
                  )}
                  {selectedTransaction.stripe_subscription_id && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">Subscription ID</Typography>
                      <Typography variant="body2" fontFamily="monospace">
                        {selectedTransaction.stripe_subscription_id}
                      </Typography>
                    </Box>
                  )}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Created</Typography>
                    <Typography variant="body2">
                      {format(parseISO(selectedTransaction.created_at), 'PPpp')}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Last Updated</Typography>
                    <Typography variant="body2">
                      {format(parseISO(selectedTransaction.updated_at), 'PPpp')}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default TransactionHistory;