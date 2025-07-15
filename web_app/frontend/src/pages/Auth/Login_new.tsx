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
  InputAdornment,
  IconButton,
  Divider,
  Stack,
  Avatar,
} from '@mui/material';
import { 
  Visibility, 
  VisibilityOff, 
  Email, 
  Lock, 
  Google, 
  Microsoft,
  Description,
} from '@mui/icons-material';
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
        bgcolor: '#f8fafc',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Container maxWidth="sm">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3 }}>
              <Avatar
                sx={{
                  width: 48,
                  height: 48,
                  bgcolor: '#0066FF',
                  mr: 2,
                }}
              >
                <Description />
              </Avatar>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: '#1a202c',
                  fontFamily: 'Montserrat, sans-serif',
                }}
              >
                PDF Extractor
              </Typography>
            </Box>
            <Typography
              sx={{
                color: '#64748b',
                fontSize: '14px',
                mb: 1,
              }}
            >
              Don't have an account?{' '}
              <Link
                component={RouterLink}
                to="/register"
                sx={{
                  color: '#0066FF',
                  textDecoration: 'none',
                  fontWeight: 500,
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                Sign Up
              </Link>
            </Typography>
          </Box>

          {/* Main Card */}
          <Card
            sx={{
              boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
              borderRadius: 3,
              border: '1px solid #e2e8f0',
              overflow: 'visible',
            }}
          >
            <CardContent sx={{ p: 5 }}>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  textAlign: 'center',
                  mb: 4,
                  color: '#1a202c',
                }}
              >
                Login to your PDF Extractor account
              </Typography>

              {/* Social Login Buttons */}
              <Stack spacing={2} sx={{ mb: 3 }}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Google />}
                  sx={{
                    py: 1.5,
                    borderColor: '#e2e8f0',
                    color: '#374151',
                    bgcolor: 'white',
                    '&:hover': {
                      bgcolor: '#f8fafc',
                      borderColor: '#d1d5db',
                    },
                    textTransform: 'none',
                    fontSize: '14px',
                    fontWeight: 500,
                  }}
                >
                  Sign in with Google
                </Button>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Microsoft />}
                  sx={{
                    py: 1.5,
                    borderColor: '#e2e8f0',
                    color: '#374151',
                    bgcolor: 'white',
                    '&:hover': {
                      bgcolor: '#f8fafc',
                      borderColor: '#d1d5db',
                    },
                    textTransform: 'none',
                    fontSize: '14px',
                    fontWeight: 500,
                  }}
                >
                  Sign in with Microsoft
                </Button>
              </Stack>

              {/* Divider */}
              <Box sx={{ display: 'flex', alignItems: 'center', my: 3 }}>
                <Divider sx={{ flex: 1 }} />
                <Typography
                  sx={{
                    px: 2,
                    color: '#9ca3af',
                    fontSize: '13px',
                    fontWeight: 500,
                  }}
                >
                  OR
                </Typography>
                <Divider sx={{ flex: 1 }} />
              </Box>

              {/* Login Form */}
              <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
                <Stack spacing={3}>
                  <TextField
                    fullWidth
                    label="Work email"
                    type="email"
                    placeholder="Enter your work email"
                    {...register('email', {
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Please enter a valid email address',
                      },
                    })}
                    error={!!errors.email}
                    helperText={errors.email?.message}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Email sx={{ color: '#9ca3af', fontSize: 20 }} />
                        </InputAdornment>
                      ),
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: '#e2e8f0',
                        },
                        '&:hover fieldset': {
                          borderColor: '#0066FF',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#0066FF',
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: '#64748b',
                        fontSize: '14px',
                      },
                      '& .MuiOutlinedInput-input': {
                        fontSize: '14px',
                      },
                    }}
                  />

                  <TextField
                    fullWidth
                    label="Password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    {...register('password', {
                      required: 'Password is required',
                    })}
                    error={!!errors.password}
                    helperText={errors.password?.message}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Lock sx={{ color: '#9ca3af', fontSize: 20 }} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                            size="small"
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: '#e2e8f0',
                        },
                        '&:hover fieldset': {
                          borderColor: '#0066FF',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#0066FF',
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: '#64748b',
                        fontSize: '14px',
                      },
                      '& .MuiOutlinedInput-input': {
                        fontSize: '14px',
                      },
                    }}
                  />

                  {/* Forgot Password Link */}
                  <Box sx={{ textAlign: 'right' }}>
                    <Link
                      href="#"
                      sx={{
                        color: '#0066FF',
                        textDecoration: 'none',
                        fontSize: '13px',
                        fontWeight: 500,
                        '&:hover': {
                          textDecoration: 'underline',
                        },
                      }}
                    >
                      Forgot Password?
                    </Link>
                  </Box>

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={isLoading}
                    sx={{
                      py: 1.5,
                      bgcolor: '#0066FF',
                      color: 'white',
                      fontSize: '14px',
                      fontWeight: 600,
                      textTransform: 'none',
                      borderRadius: 2,
                      '&:hover': {
                        bgcolor: '#0052CC',
                      },
                      '&:disabled': {
                        bgcolor: '#9ca3af',
                      },
                    }}
                  >
                    {isLoading ? 'Logging in...' : 'Login'}
                  </Button>

                  {/* SSO Login Link */}
                  <Box sx={{ textAlign: 'center' }}>
                    <Link
                      href="#"
                      sx={{
                        color: '#0066FF',
                        textDecoration: 'none',
                        fontSize: '13px',
                        fontWeight: 500,
                        '&:hover': {
                          textDecoration: 'underline',
                        },
                      }}
                    >
                      Login with SSO
                    </Link>
                  </Box>
                </Stack>
              </Box>
            </CardContent>
          </Card>

          {/* Footer */}
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <Typography
              sx={{
                color: '#9ca3af',
                fontSize: '13px',
              }}
            >
              Don't have an account?{' '}
              <Link
                component={RouterLink}
                to="/register"
                sx={{
                  color: '#0066FF',
                  textDecoration: 'none',
                  fontWeight: 500,
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                Sign Up
              </Link>
            </Typography>
          </Box>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Login;
