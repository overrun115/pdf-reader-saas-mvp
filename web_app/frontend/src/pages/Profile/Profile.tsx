import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Button,
  Avatar,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  InputAdornment,
  Container,
} from '@mui/material';
import {
  Edit,
  Save,
  Cancel,
  Delete,
  Visibility,
  VisibilityOff,
  ContentCopy,
  Add,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import api from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import { extractApiErrorMessage } from '../../utils/errorUtils';

interface UserUpdate {
  full_name: string;
  email: string;
}

interface ApiKey {
  id: number;
  name: string;
  prefix: string;
  requests_made: number;
  last_used: string | null;
  created_at: string;
}

interface Subscription {
  tier: string;
  subscription_active: boolean;
  features: {
    monthly_limit: number;
    formats: string[];
    api_access: boolean;
    priority_processing: boolean;
    email_support: boolean;
  };
  usage: {
    files_processed_this_month: number;
    monthly_limit: number;
    remaining: number;
  };
}

const Profile: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [apiKeyDialogOpen, setApiKeyDialogOpen] = useState(false);
  const [newApiKeyName, setNewApiKeyName] = useState('');
  const [newApiKey, setNewApiKey] = useState<string | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);
  const { user, updateUser } = useAuthStore();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UserUpdate>({
    defaultValues: {
      full_name: user?.full_name || '',
      email: user?.email || '',
    },
  });

  // Fetch subscription info
  const { data: subscription } = useQuery<Subscription>(
    'user-subscription',
    async () => {
      const response = await api.get('/users/me/subscription');
      return response.data.data;
    }
  );

  // Fetch API keys
  const { data: apiKeys = [] } = useQuery<ApiKey[]>(
    'api-keys',
    async () => {
      const response = await api.get('/users/me/api-keys');
      return response.data.data.api_keys;
    },
    {
      enabled: subscription?.features.api_access,
    }
  );

  // Update profile mutation
  const updateProfileMutation = useMutation(
    async (data: UserUpdate) => {
      const response = await api.put('/users/me', data);
      return response.data;
    },
    {
      onSuccess: (data) => {
        updateUser(data);
        toast.success('Profile updated successfully');
        setIsEditing(false);
      },
      onError: (error: any) => {
        toast.error(extractApiErrorMessage(error) || 'Update failed');
      },
    }
  );

  // Create API key mutation
  const createApiKeyMutation = useMutation(
    async (name: string) => {
      const response = await api.post(`/users/me/api-keys?key_name=${encodeURIComponent(name)}`);
      return response.data;
    },
    {
      onSuccess: (data) => {
        setNewApiKey(data.data.api_key);
        toast.success('API key created successfully');
        queryClient.invalidateQueries(['api-keys']);
        setNewApiKeyName('');
      },
      onError: (error: any) => {
        toast.error(extractApiErrorMessage(error) || 'Failed to create API key');
      },
    }
  );

  // Delete API key mutation
  const deleteApiKeyMutation = useMutation(
    async (keyId: number) => {
      await api.delete(`/users/me/api-keys/${keyId}`);
    },
    {
      onSuccess: () => {
        toast.success('API key deleted successfully');
        queryClient.invalidateQueries(['api-keys']);
      },
      onError: (error: any) => {
        toast.error(extractApiErrorMessage(error) || 'Failed to delete API key');
      },
    }
  );

  const onSubmit = (data: UserUpdate) => {
    updateProfileMutation.mutate(data);
  };

  const handleCancelEdit = () => {
    reset();
    setIsEditing(false);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const getTierColor = (tier: string) => {
    const colors = {
      free: '#94a3b8',
      basic: '#3b82f6',
      pro: '#8b5cf6',
      enterprise: '#f59e0b',
    };
    return colors[tier as keyof typeof colors] || colors.free;
  };

  const getUsagePercentage = () => {
    if (!subscription?.usage) return 0;
    const { files_processed_this_month, monthly_limit } = subscription.usage;
    if (monthly_limit === -1) return 0;
    return (files_processed_this_month / monthly_limit) * 100;
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Profile Settings
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Manage your account settings and subscription
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Profile Information */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
                  <Typography variant="h6" fontWeight={600}>
                    Profile Information
                  </Typography>
                  {!isEditing && (
                    <Button
                      startIcon={<Edit />}
                      onClick={() => setIsEditing(true)}
                    >
                      Edit Profile
                    </Button>
                  )}
                </Box>

                <Box display="flex" alignItems="center" gap={3} mb={4}>
                  <Avatar
                    sx={{
                      width: 80,
                      height: 80,
                      bgcolor: '#667eea',
                      fontSize: '2rem',
                    }}
                  >
                    {user?.full_name?.charAt(0).toUpperCase()}
                  </Avatar>
                  <Box>
                    <Typography variant="h6" fontWeight={600}>
                      {user?.full_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Member since {user?.created_at ? format(new Date(user.created_at), 'MMMM yyyy') : 'Unknown'}
                    </Typography>
                  </Box>
                </Box>

                <form onSubmit={handleSubmit(onSubmit)}>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Full Name"
                        {...register('full_name', {
                          required: 'Full name is required',
                        })}
                        error={!!errors.full_name}
                        helperText={errors.full_name?.message}
                        disabled={!isEditing}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Email"
                        type="email"
                        {...register('email', {
                          required: 'Email is required',
                          pattern: {
                            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                            message: 'Invalid email address',
                          },
                        })}
                        error={!!errors.email}
                        helperText={errors.email?.message}
                        disabled={!isEditing}
                      />
                    </Grid>
                  </Grid>

                  {isEditing && (
                    <Box display="flex" gap={2} mt={3}>
                      <Button
                        type="submit"
                        variant="contained"
                        startIcon={<Save />}
                        disabled={updateProfileMutation.isLoading}
                      >
                        {updateProfileMutation.isLoading ? 'Saving...' : 'Save Changes'}
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<Cancel />}
                        onClick={handleCancelEdit}
                      >
                        Cancel
                      </Button>
                    </Box>
                  )}
                </form>
              </CardContent>
            </Card>
          </motion.div>

          {/* API Keys */}
          {subscription?.features.api_access && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Card sx={{ mt: 3 }}>
                <CardContent>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
                    <Typography variant="h6" fontWeight={600}>
                      API Keys
                    </Typography>
                    <Button
                      startIcon={<Add />}
                      onClick={() => setApiKeyDialogOpen(true)}
                      disabled={apiKeys.length >= 5}
                    >
                      Create API Key
                    </Button>
                  </Box>

                  {apiKeys.length === 0 ? (
                    <Alert severity="info">
                      No API keys created yet. Create your first API key to start using our REST API.
                    </Alert>
                  ) : (
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Name</TableCell>
                            <TableCell>Key</TableCell>
                            <TableCell>Requests</TableCell>
                            <TableCell>Last Used</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {apiKeys.map((apiKey) => (
                            <TableRow key={apiKey.id}>
                              <TableCell>{apiKey.name}</TableCell>
                              <TableCell>
                                <Box display="flex" alignItems="center" gap={1}>
                                  <Typography variant="body2" fontFamily="monospace">
                                    {apiKey.prefix}...
                                  </Typography>
                                  <IconButton
                                    size="small"
                                    onClick={() => copyToClipboard(apiKey.prefix)}
                                  >
                                    <ContentCopy fontSize="small" />
                                  </IconButton>
                                </Box>
                              </TableCell>
                              <TableCell>{apiKey.requests_made}</TableCell>
                              <TableCell>
                                {apiKey.last_used 
                                  ? format(new Date(apiKey.last_used), 'MMM dd, yyyy')
                                  : 'Never'
                                }
                              </TableCell>
                              <TableCell>
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => deleteApiKeyMutation.mutate(apiKey.id)}
                                >
                                  <Delete />
                                </IconButton>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}
        </Grid>

        {/* Subscription & Usage */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Subscription
                </Typography>

                <Box textAlign="center" mb={3}>
                  <Chip
                    label={subscription?.tier.toUpperCase() || 'FREE'}
                    sx={{
                      bgcolor: getTierColor(subscription?.tier || 'free'),
                      color: '#fff',
                      fontWeight: 600,
                      fontSize: '1rem',
                      px: 2,
                      py: 1,
                    }}
                  />
                </Box>

                {subscription && (
                  <>
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                      Monthly Usage
                    </Typography>
                    <Box mb={2}>
                      <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                        <Typography variant="body2" color="text.secondary">
                          {subscription.usage.files_processed_this_month} of{' '}
                          {subscription.usage.monthly_limit === -1 ? '∞' : subscription.usage.monthly_limit}
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {subscription.usage.remaining === -1 ? '∞' : subscription.usage.remaining} left
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={getUsagePercentage()}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                      Plan Features
                    </Typography>
                    <List dense>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemText
                          primary={`${subscription.features.monthly_limit === -1 ? 'Unlimited' : subscription.features.monthly_limit} files/month`}
                        />
                      </ListItem>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemText
                          primary={`Export: ${subscription.features.formats.join(', ')}`}
                        />
                      </ListItem>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemText
                          primary={`API Access: ${subscription.features.api_access ? 'Yes' : 'No'}`}
                        />
                      </ListItem>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemText
                          primary={`Priority: ${subscription.features.priority_processing ? 'Yes' : 'No'}`}
                        />
                      </ListItem>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemText
                          primary={`Support: ${subscription.features.email_support ? 'Email' : 'Basic'}`}
                        />
                      </ListItem>
                    </List>

                    {subscription.tier === 'free' && (
                      <Button
                        fullWidth
                        variant="contained"
                        sx={{ mt: 2 }}
                        onClick={() => window.open('/pricing', '_blank')}
                      >
                        Upgrade Plan
                      </Button>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Account Actions */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Account Actions
                </Typography>
                
                <Button
                  fullWidth
                  variant="outlined"
                  color="error"
                  sx={{ mt: 2 }}
                  onClick={() => {
                    if (window.confirm('Are you sure you want to deactivate your account?')) {
                      // Handle account deactivation
                      toast('Account deactivation feature coming soon');
                    }
                  }}
                >
                  Deactivate Account
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Create API Key Dialog */}
      <Dialog
        open={apiKeyDialogOpen}
        onClose={() => setApiKeyDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create API Key</DialogTitle>
        <DialogContent>
          {newApiKey ? (
            <Box>
              <Alert severity="success" sx={{ mb: 2 }}>
                API key created successfully! Copy it now - you won't see it again.
              </Alert>
              <TextField
                fullWidth
                label="Your API Key"
                value={newApiKey}
                type={showApiKey ? 'text' : 'password'}
                InputProps={{
                  readOnly: true,
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowApiKey(!showApiKey)}>
                        {showApiKey ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                      <IconButton onClick={() => copyToClipboard(newApiKey)}>
                        <ContentCopy />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
          ) : (
            <TextField
              fullWidth
              label="API Key Name"
              value={newApiKeyName}
              onChange={(e) => setNewApiKeyName(e.target.value)}
              placeholder="e.g., Production API Key"
              helperText="Choose a descriptive name for this API key"
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setApiKeyDialogOpen(false);
              setNewApiKey(null);
              setNewApiKeyName('');
            }}
          >
            {newApiKey ? 'Done' : 'Cancel'}
          </Button>
          {!newApiKey && (
            <Button
              variant="contained"
              onClick={() => createApiKeyMutation.mutate(newApiKeyName)}
              disabled={!newApiKeyName.trim() || createApiKeyMutation.isLoading}
            >
              {createApiKeyMutation.isLoading ? 'Creating...' : 'Create Key'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Profile;