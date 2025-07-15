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
  useTheme,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
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
  const [emailVerificationDialog, setEmailVerificationDialog] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();
  const theme = useTheme();

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
      
      console.log('Login error:', errorMessage); // Debug
      console.log('Full error object:', error); // Debug
      
      // Check if it's an email verification error
      if (errorMessage.includes('Casi listo') || errorMessage.includes('verificar tu email') || errorMessage.includes('Email not verified')) {
        setEmailVerificationDialog(true);
      } else {
        toast.error(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
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
                  bgcolor: theme.palette.primary.main,
                  mr: 2,
                }}
              >
                <Description />
              </Avatar>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: theme.palette.text.primary,
                  fontFamily: 'Montserrat, sans-serif',
                }}
              >
                PDF Extractor
              </Typography>
            </Box>
            <Typography
              sx={{
                color: theme.palette.text.secondary,
                fontSize: '14px',
                mb: 1,
              }}
            >
              Don't have an account?{' '}
              <Link
                component={RouterLink}
                to="/register"
                sx={{
                  color: theme.palette.primary.main,
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
              boxShadow: theme.palette.mode === 'dark' 
                ? '0 10px 25px rgba(0,0,0,0.3)' 
                : '0 10px 25px rgba(0,0,0,0.1)',
              borderRadius: 3,
              border: `1px solid ${theme.palette.divider}`,
              overflow: 'visible',
              bgcolor: theme.palette.background.paper,
            }}
          >
            <CardContent sx={{ p: 5 }}>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  textAlign: 'center',
                  mb: 4,
                  color: theme.palette.text.primary,
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
                    borderColor: theme.palette.divider,
                    color: theme.palette.text.primary,
                    bgcolor: theme.palette.background.paper,
                    '&:hover': {
                      bgcolor: theme.palette.action.hover,
                      borderColor: theme.palette.primary.main,
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
                    borderColor: theme.palette.divider,
                    color: theme.palette.text.primary,
                    bgcolor: theme.palette.background.paper,
                    '&:hover': {
                      bgcolor: theme.palette.action.hover,
                      borderColor: theme.palette.primary.main,
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
                    color: theme.palette.text.secondary,
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
                          <Email sx={{ color: theme.palette.text.secondary, fontSize: 20 }} />
                        </InputAdornment>
                      ),
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: theme.palette.divider,
                        },
                        '&:hover fieldset': {
                          borderColor: theme.palette.primary.main,
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: theme.palette.primary.main,
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: theme.palette.text.secondary,
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
                          <Lock sx={{ color: theme.palette.text.secondary, fontSize: 20 }} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                            size="small"
                            sx={{ color: theme.palette.text.secondary }}
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: theme.palette.divider,
                        },
                        '&:hover fieldset': {
                          borderColor: theme.palette.primary.main,
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: theme.palette.primary.main,
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: theme.palette.text.secondary,
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
                        color: theme.palette.primary.main,
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
                      bgcolor: theme.palette.primary.main,
                      color: theme.palette.primary.contrastText,
                      fontSize: '14px',
                      fontWeight: 600,
                      textTransform: 'none',
                      borderRadius: 2,
                      '&:hover': {
                        bgcolor: theme.palette.primary.dark,
                      },
                      '&:disabled': {
                        bgcolor: theme.palette.action.disabled,
                        color: theme.palette.action.disabled,
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
                        color: theme.palette.primary.main,
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
                color: theme.palette.text.secondary,
                fontSize: '13px',
              }}
            >
              Don't have an account?{' '}
              <Link
                component={RouterLink}
                to="/register"
                sx={{
                  color: theme.palette.primary.main,
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

      {/* Email Verification Dialog */}
      <Dialog 
        open={emailVerificationDialog} 
        onClose={() => setEmailVerificationDialog(false)}
        maxWidth="sm"
        fullWidth
        sx={{
          '& .MuiDialog-paper': {
            borderRadius: 3,
            p: 2,
          }
        }}
      >
        <DialogTitle sx={{ 
          textAlign: 'center', 
          pb: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: 2
        }}>
          <Box sx={{ 
            fontSize: '48px',
            color: theme.palette.warning.main,
          }}>
            ✉️
          </Box>
          <Typography variant="h5" sx={{ 
            fontWeight: 600,
            color: theme.palette.text.primary,
          }}>
            ¡Casi listo!
          </Typography>
        </DialogTitle>
        
        <DialogContent sx={{ textAlign: 'center', py: 2 }}>
          <Typography variant="body1" sx={{ 
            color: theme.palette.text.secondary,
            lineHeight: 1.6,
            mb: 2,
          }}>
            Solo falta verificar tu email para acceder a tu cuenta.
          </Typography>
          
          <Typography variant="body2" sx={{ 
            color: theme.palette.text.secondary,
            lineHeight: 1.6,
          }}>
            📧 Revisa tu bandeja de entrada y haz clic en el enlace de verificación que te enviamos.
          </Typography>
          
          <Typography variant="body2" sx={{ 
            color: theme.palette.text.secondary,
            lineHeight: 1.6,
            mt: 1,
          }}>
            💡 <strong>Tip:</strong> Si no lo encuentras, revisa tu carpeta de spam.
          </Typography>
        </DialogContent>
        
        <DialogActions sx={{ 
          justifyContent: 'center',
          pb: 2,
        }}>
          <Button
            onClick={() => setEmailVerificationDialog(false)}
            variant="contained"
            sx={{
              px: 4,
              py: 1,
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 500,
              bgcolor: theme.palette.primary.main,
              color: theme.palette.primary.contrastText,
              '&:hover': {
                bgcolor: theme.palette.primary.dark,
              },
            }}
          >
            Entendido
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Login;
