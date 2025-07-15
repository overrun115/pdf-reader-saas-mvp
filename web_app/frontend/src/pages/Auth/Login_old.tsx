import React, { useState } from 'react';
import {
  Box,
  Container,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
  InputAdornment,
  IconButton,
  Divider,
  Stack,
  Grid,
  Paper,
} from '@mui/material';
import { Visibility, VisibilityOff, Email, Lock, Business } from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { useAuthStore } from '../../store/authStore';
import { extractApiErrorMessage } from '../../utils/errorUtils';

interface LoginForm {
  email: string;
  password: string;
}

const Login: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>();

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    try {
      await login(data.email, data.password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (error: any) {
      // Better error handling with specific messages
      const errorMessage = extractApiErrorMessage(error) || 'Login failed. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: '#FFFFFF',
        display: 'flex',
      }}
    >
      <Grid container sx={{ minHeight: '100vh' }}>
        {/* Left Side - Branding */}
        <Grid 
          item 
          xs={12} 
          md={6} 
          sx={{
            bgcolor: '#0066FF',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            p: 4,
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <Box sx={{ textAlign: 'center', zIndex: 2 }}>
            <Business sx={{ fontSize: 60, mb: 3 }} />
            <Typography 
              variant="h3" 
              sx={{ 
                fontWeight: 700,
                mb: 2,
                fontFamily: 'Montserrat, sans-serif',
              }}
            >
              PDF Extractor
            </Typography>
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 400,
                mb: 4,
                opacity: 0.9,
                maxWidth: 400,
                lineHeight: 1.6,
              }}
            >
              Extract structured data from your documents with AI-powered precision
            </Typography>
            <Box sx={{ display: 'flex', gap: 4, justifyContent: 'center', mt: 4 }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>99%</Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>Accuracy</Typography>
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>10K+</Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>Users</Typography>
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>1M+</Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>Documents</Typography>
              </Box>
            </Box>
          </Box>
          
          {/* Background Pattern */}
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              opacity: 0.1,
              backgroundImage: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.1"%3E%3Ccircle cx="30" cy="30" r="4"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
            }}
          />
        </Grid>
        
        {/* Right Side - Login Form */}
        <Grid 
          item 
          xs={12} 
          md={6} 
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            p: 4,
          }}
        >
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            style={{ width: '100%', maxWidth: 400 }}
          >
            <Box sx={{ mb: 4 }}>
              <Typography 
                variant="h4" 
                sx={{ 
                  fontWeight: 700,
                  color: '#1a202c',
                  mb: 2,
                  fontFamily: 'Montserrat, sans-serif',
                }}
              >
                Welcome back
              </Typography>
              <Typography 
                variant="body1" 
                sx={{ 
                  color: '#6B7280',
                  fontSize: '1.1rem',
                  lineHeight: 1.6,
                }}
              >
                Sign in to your account to continue
              </Typography>
            </Box>

            <form onSubmit={handleSubmit(onSubmit)}>
              <Stack spacing={3}>
                <TextField
                  fullWidth
                  placeholder="Enter your email"
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
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      bgcolor: '#F9FAFB',
                      border: '1px solid #E5E7EB',
                      '&:hover': {
                        borderColor: '#0066FF',
                      },
                      '&.Mui-focused': {
                        borderColor: '#0066FF',
                        boxShadow: '0 0 0 3px rgba(0, 102, 255, 0.1)',
                      },
                    },
                    '& .MuiInputBase-input': {
                      py: 1.5,
                      fontSize: '1rem',
                    },
                  }}
                />

                <TextField
                  fullWidth
                  placeholder="Enter your password"
                  type={showPassword ? 'text' : 'password'}
                  {...register('password', {
                    required: 'Password is required',
                  })}
                  error={!!errors.password}
                  helperText={errors.password?.message}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          sx={{ color: '#6B7280' }}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      bgcolor: '#F9FAFB',
                      border: '1px solid #E5E7EB',
                      '&:hover': {
                        borderColor: '#0066FF',
                      },
                      '&.Mui-focused': {
                        borderColor: '#0066FF',
                        boxShadow: '0 0 0 3px rgba(0, 102, 255, 0.1)',
                      },
                    },
                    '& .MuiInputBase-input': {
                      py: 1.5,
                      fontSize: '1rem',
                    },
                  }}
                />

                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                  <Link
                    component={RouterLink}
                    to="/forgot-password"
                    sx={{
                      color: '#0066FF',
                      textDecoration: 'none',
                      fontSize: '0.9rem',
                      fontWeight: 500,
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                    }}
                  >
                    Forgot password?
                  </Link>
                </Box>

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={isLoading}
                  sx={{
                    py: 1.5,
                    bgcolor: '#0066FF',
                    fontWeight: 600,
                    fontSize: '1rem',
                    borderRadius: 2,
                    textTransform: 'none',
                    boxShadow: 'none',
                    '&:hover': {
                      bgcolor: '#0052CC',
                      boxShadow: 'none',
                    },
                    '&:disabled': {
                      bgcolor: '#E5E7EB',
                      color: '#9CA3AF',
                    },
                  }}
                >
                  {isLoading ? 'Signing in...' : 'Sign in'}
                </Button>
              </Stack>
            </form>

            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <Typography 
                variant="body1" 
                sx={{ 
                  color: '#6B7280',
                  fontSize: '0.95rem',
                }}
              >
                Don't have an account?{' '}
                <Link
                  component={RouterLink}
                  to="/register"
                  sx={{
                    color: '#0066FF',
                    textDecoration: 'none',
                    fontWeight: 600,
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  Sign up for free
                </Link>
              </Typography>
            </Box>

            <Alert 
              severity="info" 
              sx={{ 
                mt: 4,
                bgcolor: 'rgba(0, 102, 255, 0.05)',
                border: '1px solid rgba(0, 102, 255, 0.2)',
                borderRadius: 2,
                '& .MuiAlert-message': {
                  color: '#1a202c',
                },
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                <strong>Demo Account:</strong><br />
                Email: admin@pdfextractor.com<br />
                Password: admin123
              </Typography>
            </Alert>

            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <Link
                component={RouterLink}
                to="/"
                sx={{
                  color: '#6B7280',
                  textDecoration: 'none',
                  fontSize: '0.9rem',
                  '&:hover': {
                    color: '#0066FF',
                  },
                }}
              >
                ← Back to Home
              </Link>
            </Box>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Login;