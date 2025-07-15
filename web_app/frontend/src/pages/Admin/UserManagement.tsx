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
  Menu,
  Alert,
  Container
} from '@mui/material';
import {
  Search,
  MoreVert,
  Edit,
  Delete,
  Block,
  CheckCircle,
  PersonAdd,
  FilterList,
  ToggleOff,
  ToggleOn
} from '@mui/icons-material';
import { format, parseISO } from 'date-fns';
import api from '../../services/api';
import toast from 'react-hot-toast';
import { extractApiErrorMessage } from '../../utils/errorUtils';

interface User {
  id: number;
  email: string;
  full_name: string;
  tier: string;
  subscription_active: boolean;
  subscription_id: string | null;
  stripe_customer_id: string | null;
  files_processed_this_month: number;
  total_files_processed: number;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login: string | null;
}

interface UsersResponse {
  users: User[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 50,
    total: 0,
    pages: 0
  });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [tierFilter, setTierFilter] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [newTier, setNewTier] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuUserId, setMenuUserId] = useState<number | null>(null);
  const [createUserDialog, setCreateUserDialog] = useState(false);
  const [deleteConfirmDialog, setDeleteConfirmDialog] = useState(false);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);
  const [newUserData, setNewUserData] = useState({
    email: '',
    full_name: '',
    password: '',
    tier: 'free'
  });

  useEffect(() => {
    loadUsers();
  }, [pagination.page, searchTerm, tierFilter]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        limit: pagination.limit.toString()
      });

      if (searchTerm) params.append('search', searchTerm);
      if (tierFilter) params.append('tier_filter', tierFilter);

      const response = await api.get(`/management/users?${params.toString()}`);
      const data: UsersResponse = response.data;

      setUsers(data.users);
      setPagination(prev => ({
        ...prev,
        total: data.pagination.total,
        pages: data.pagination.pages
      }));
    } catch (error) {
      console.error('Error loading users:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleTierFilter = (event: any) => {
    setTierFilter(event.target.value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, page: number) => {
    setPagination(prev => ({ ...prev, page }));
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, userId: number) => {
    setAnchorEl(event.currentTarget);
    setMenuUserId(userId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuUserId(null);
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setNewTier(user.tier);
    setEditDialogOpen(true);
    handleMenuClose();
  };

  const handleUpdateTier = async () => {
    if (!selectedUser) return;

    try {
      await api.put(`/management/users/${selectedUser.id}/tier`, { tier: newTier }, {
        headers: { 'Content-Type': 'application/json' }
      });
      
      toast.success('User tier updated successfully');
      setEditDialogOpen(false);
      setSelectedUser(null);
      loadUsers();
    } catch (error) {
      console.error('Error updating user tier:', error);
      toast.error('Failed to update user tier');
    }
  };

  const handleCreateUser = async () => {
    try {
      await api.post('/management/users', newUserData);
      toast.success('User created successfully');
      setCreateUserDialog(false);
      setNewUserData({ email: '', full_name: '', password: '', tier: 'free' });
      loadUsers();
    } catch (error: any) {
      console.error('Error creating user:', error);
      toast.error(extractApiErrorMessage(error) || 'Failed to create user');
    }
  };

  const handleDeleteUser = async () => {
    if (!userToDelete) return;

    try {
      await api.delete(`/management/users/${userToDelete.id}`);
      toast.success('User deleted successfully');
      setDeleteConfirmDialog(false);
      setUserToDelete(null);
      loadUsers();
    } catch (error: any) {
      console.error('Error deleting user:', error);
      toast.error(extractApiErrorMessage(error) || 'Failed to delete user');
    }
  };

  const handleToggleUserStatus = async (userId: number, currentStatus: boolean) => {
    try {
      await api.put(`/management/users/${userId}/status`, { is_active: !currentStatus });
      toast.success(`User ${!currentStatus ? 'activated' : 'deactivated'} successfully`);
      loadUsers();
    } catch (error: any) {
      console.error('Error toggling user status:', error);
      toast.error('Failed to update user status');
    }
  };

  const handleToggleSubscription = async (userId: number, currentStatus: boolean) => {
    try {
      await api.put(`/management/users/${userId}/subscription`, { subscription_active: !currentStatus });
      toast.success(`Subscription ${!currentStatus ? 'activated' : 'deactivated'} successfully`);
      loadUsers();
    } catch (error: any) {
      console.error('Error toggling subscription:', error);
      toast.error('Failed to update subscription status');
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

  const getSubscriptionStatusColor = (active: boolean) => {
    return active ? 'success' : 'default';
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return format(parseISO(dateString), 'MMM d, yyyy');
  };

  const calculateRevenue = (tier: string, active: boolean) => {
    if (!active) return '$0';
    
    const tierPrices: Record<string, number> = {
      free: 0,
      basic: 9.99,
      pro: 29.99,
      enterprise: 99.99
    };
    
    return `$${tierPrices[tier.toLowerCase()] || 0}/mo`;
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        User Management
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Manage users, subscriptions, and analyze user behavior
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Users
              </Typography>
              <Typography variant="h4" fontWeight={700}>
                {pagination.total.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Active Subscriptions
              </Typography>
              <Typography variant="h4" fontWeight={700} color="success.main">
                {users.filter(u => u.subscription_active).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Monthly Revenue
              </Typography>
              <Typography variant="h4" fontWeight={700} color="info.main">
                ${users.reduce((sum, user) => {
                  if (!user.subscription_active) return sum;
                  const prices: Record<string, number> = {
                    basic: 9.99, pro: 29.99, enterprise: 99.99
                  };
                  return sum + (prices[user.tier.toLowerCase()] || 0);
                }, 0).toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Files Processed
              </Typography>
              <Typography variant="h4" fontWeight={700}>
                {users.reduce((sum, user) => sum + user.total_files_processed, 0).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search users..."
          value={searchTerm}
          onChange={handleSearch}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 250 }}
        />
        
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Tier Filter</InputLabel>
          <Select
            value={tierFilter}
            label="Tier Filter"
            onChange={handleTierFilter}
          >
            <MenuItem value="">All Tiers</MenuItem>
            <MenuItem value="free">Free</MenuItem>
            <MenuItem value="basic">Basic</MenuItem>
            <MenuItem value="pro">Pro</MenuItem>
            <MenuItem value="enterprise">Enterprise</MenuItem>
          </Select>
        </FormControl>

        <Button
          variant="outlined"
          startIcon={<FilterList />}
          onClick={loadUsers}
        >
          Refresh
        </Button>

        <Button
          variant="contained"
          startIcon={<PersonAdd />}
          onClick={() => setCreateUserDialog(true)}
          sx={{ ml: 'auto' }}
        >
          Create User
        </Button>
      </Box>

      {/* Users Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Tier</TableCell>
                <TableCell>Subscription</TableCell>
                <TableCell>Revenue</TableCell>
                <TableCell>Files</TableCell>
                <TableCell>Joined</TableCell>
                <TableCell>Last Login</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        {user.full_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {user.email}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={user.tier.toUpperCase()} 
                      color={getTierColor(user.tier)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={user.subscription_active ? 'Active' : 'Inactive'} 
                      color={getSubscriptionStatusColor(user.subscription_active)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600} color="success.main">
                      {calculateRevenue(user.tier, user.subscription_active)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">
                        {user.files_processed_this_month} this month
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {user.total_files_processed} total
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(user.created_at)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(user.last_login)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Chip 
                        label={user.is_active ? 'Active' : 'Inactive'} 
                        color={user.is_active ? 'success' : 'default'}
                        size="small"
                      />
                      {user.is_verified && (
                        <Chip 
                          label="Verified" 
                          color="info"
                          size="small"
                        />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      onClick={(e) => handleMenuOpen(e, user.id)}
                      size="small"
                    >
                      <MoreVert />
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

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem 
          onClick={() => {
            const user = users.find(u => u.id === menuUserId);
            if (user) handleEditUser(user);
          }}
        >
          <Edit sx={{ mr: 1 }} />
          Edit Tier
        </MenuItem>
        <MenuItem 
          onClick={() => {
            const user = users.find(u => u.id === menuUserId);
            if (user) handleToggleUserStatus(user.id, user.is_active);
            handleMenuClose();
          }}
        >
          {users.find(u => u.id === menuUserId)?.is_active ? 
            <ToggleOff sx={{ mr: 1 }} /> : <ToggleOn sx={{ mr: 1 }} />
          }
          {users.find(u => u.id === menuUserId)?.is_active ? 'Deactivate' : 'Activate'} User
        </MenuItem>
        <MenuItem 
          onClick={() => {
            const user = users.find(u => u.id === menuUserId);
            if (user) handleToggleSubscription(user.id, user.subscription_active);
            handleMenuClose();
          }}
        >
          {users.find(u => u.id === menuUserId)?.subscription_active ? 
            <Block sx={{ mr: 1 }} /> : <CheckCircle sx={{ mr: 1 }} />
          }
          {users.find(u => u.id === menuUserId)?.subscription_active ? 'Disable' : 'Enable'} Subscription
        </MenuItem>
        <MenuItem 
          onClick={() => {
            const user = users.find(u => u.id === menuUserId);
            if (user) {
              setUserToDelete(user);
              setDeleteConfirmDialog(true);
            }
            handleMenuClose();
          }}
          sx={{ color: 'error.main' }}
        >
          <Delete sx={{ mr: 1 }} />
          Delete User
        </MenuItem>
      </Menu>

      {/* Edit User Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)}>
        <DialogTitle>Edit User Tier</DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Box sx={{ pt: 1 }}>
              <Typography variant="body2" gutterBottom>
                User: {selectedUser.full_name} ({selectedUser.email})
              </Typography>
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Tier</InputLabel>
                <Select
                  value={newTier}
                  label="Tier"
                  onChange={(e) => setNewTier(e.target.value)}
                >
                  <MenuItem value="free">Free</MenuItem>
                  <MenuItem value="basic">Basic</MenuItem>
                  <MenuItem value="pro">Pro</MenuItem>
                  <MenuItem value="enterprise">Enterprise</MenuItem>
                </Select>
              </FormControl>
              <Alert severity="info" sx={{ mt: 2 }}>
                This will manually change the user's tier. Subscription status in Stripe won't be affected.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleUpdateTier} variant="contained">
            Update Tier
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create User Dialog */}
      <Dialog open={createUserDialog} onClose={() => setCreateUserDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Full Name"
              value={newUserData.full_name}
              onChange={(e) => setNewUserData({ ...newUserData, full_name: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Email"
              type="email"
              value={newUserData.email}
              onChange={(e) => setNewUserData({ ...newUserData, email: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Password"
              type="password"
              value={newUserData.password}
              onChange={(e) => setNewUserData({ ...newUserData, password: e.target.value })}
              fullWidth
              required
              helperText="Minimum 8 characters"
            />
            <FormControl fullWidth>
              <InputLabel>Tier</InputLabel>
              <Select
                value={newUserData.tier}
                label="Tier"
                onChange={(e) => setNewUserData({ ...newUserData, tier: e.target.value })}
              >
                <MenuItem value="free">Free</MenuItem>
                <MenuItem value="basic">Basic</MenuItem>
                <MenuItem value="pro">Pro</MenuItem>
                <MenuItem value="enterprise">Enterprise</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateUserDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleCreateUser} 
            variant="contained"
            disabled={!newUserData.email || !newUserData.full_name || !newUserData.password}
          >
            Create User
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmDialog} onClose={() => setDeleteConfirmDialog(false)}>
        <DialogTitle>Delete User</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete user <strong>{userToDelete?.full_name}</strong> ({userToDelete?.email})?
          </Typography>
          <Alert severity="error" sx={{ mt: 2 }}>
            This action cannot be undone. All user data will be permanently deleted.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmDialog(false)}>
            Cancel
          </Button>
          <Button onClick={handleDeleteUser} variant="contained" color="error">
            Delete User
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default UserManagement;