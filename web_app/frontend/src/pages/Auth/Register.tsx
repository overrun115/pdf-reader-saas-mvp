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
  Checkbox,
  FormControlLabel,
  LinearProgress,
  Avatar,
  useTheme,
} from '@mui/material';
import { 
  Visibility, 
  VisibilityOff, 
  Email, 
  Lock, 
  Person, 
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

interface RegisterForm {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
  acceptTerms: boolean;
}

const Register: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { register: registerUser } = useAuthStore();
  const navigate = useNavigate();
  const theme = useTheme();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterForm>();

  const password = watch('password');

  const getPasswordStrength = (pwd: string) => {
    if (!pwd) return 0;
    let strength = 0;
    if (pwd.length >= 8) strength += 25;
    if (/[a-z]/.test(pwd)) strength += 25;
    if (/[A-Z]/.test(pwd)) strength += 25;
    if (/[0-9]/.test(pwd)) strength += 25;
    return strength;
  };

  const passwordStrength = getPasswordStrength(password || '');

  const getPasswordStrengthColor = (strength: number) => {
    if (strength < 50) return 'error';
    if (strength < 75) return 'warning';
    return 'success';
  };

  const getPasswordStrengthText = (strength: number) => {
    if (strength < 25) return 'Very Weak';
    if (strength < 50) return 'Weak';
    if (strength < 75) return 'Good';
    return 'Strong';
  };

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true);
    try {
      await registerUser(data.email, data.password, data.fullName);
      toast.success('¡Cuenta creada exitosamente! Te hemos enviado un email con un enlace de verificación.');
      navigate('/email-verification-pending', { state: { email: data.email } });
    } catch (error: any) {
      toast.error(extractApiErrorMessage(error) || 'Registration failed');
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
                  bgcolor: 'primary.main',
                  mr: 2,
                }}
              >
                <Description />
              </Avatar>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: 'text.primary',
                  fontFamily: 'Montserrat, sans-serif',
                }}
              >
                PDF Extractor
              </Typography>
            </Box>
            <Typography
              sx={{
                color: 'text.secondary',
                fontSize: '14px',
                mb: 1,
              }}
            >
              Already have an account?{' '}
              <Link
                component={RouterLink}
                to="/login"
                sx={{
                  color: 'primary.main',
                  textDecoration: 'none',
                  fontWeight: 500,
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                Log In
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
                  mb: 1,
                  color: 'text.primary',
                }}
              >
                Get PDF Extractor free for 14 days
              </Typography>
              
              <Typography
                sx={{
                  textAlign: 'center',
                  color: 'text.secondary',
                  mb: 4,
                  fontSize: '14px',
                }}
              >
                Sign up with your work email
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
                  Continue with Google
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
                  Continue with Microsoft
                </Button>
              </Stack>

              {/* Divider */}
              <Box sx={{ display: 'flex', alignItems: 'center', my: 3 }}>
                <Divider sx={{ flex: 1 }} />
                <Typography
                  sx={{
                    px: 2,
                    color: 'text.secondary',
                    fontSize: '13px',
                    fontWeight: 500,
                  }}
                >
                  OR
                </Typography>
                <Divider sx={{ flex: 1 }} />
              </Box>

              {/* Registration Form */}
              <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
                <Stack spacing={3}>
                  <TextField
                    fullWidth
                    label="Full Name"
                    placeholder="Enter your full name"
                    {...register('fullName', {
                      required: 'Full name is required',
                      minLength: {
                        value: 2,
                        message: 'Full name must be at least 2 characters',
                      },
                    })}
                    error={!!errors.fullName}
                    helperText={errors.fullName?.message}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Person sx={{ color: theme.palette.text.secondary, fontSize: 20 }} />
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
                    label="Work Email"
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
                    placeholder="Create a strong password"
                    {...register('password', {
                      required: 'Password is required',
                      minLength: {
                        value: 8,
                        message: 'Password must be at least 8 characters',
                      },
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

                  {/* Password Strength Indicator */}
                  {password && (
                    <Box sx={{ mt: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={passwordStrength}
                        color={getPasswordStrengthColor(passwordStrength) as any}
                        sx={{
                          height: 4,
                          borderRadius: 2,
                          bgcolor: 'action.hover',
                        }}
                      />
                      <Typography
                        variant="caption"
                        sx={{
                          color: passwordStrength < 50 ? 'error.main' : passwordStrength < 75 ? 'warning.main' : 'success.main',
                          fontSize: '12px',
                          mt: 0.5,
                          display: 'block',
                        }}
                      >
                        Password strength: {getPasswordStrengthText(passwordStrength)}
                      </Typography>
                    </Box>
                  )}

                  <TextField
                    fullWidth
                    label="Confirm Password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Confirm your password"
                    {...register('confirmPassword', {
                      required: 'Please confirm your password',
                      validate: (value) =>
                        value === password || 'Passwords do not match',
                    })}
                    error={!!errors.confirmPassword}
                    helperText={errors.confirmPassword?.message}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Lock sx={{ color: theme.palette.text.secondary, fontSize: 20 }} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            edge="end"
                            size="small"
                            sx={{ color: theme.palette.text.secondary }}
                          >
                            {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
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

                  <FormControlLabel
                    control={
                      <Checkbox
                        {...register('acceptTerms', {
                          required: 'You must accept the terms and conditions',
                        })}
                        sx={{
                          color: theme.palette.primary.main,
                          '&.Mui-checked': {
                            color: theme.palette.primary.main,
                          },
                        }}
                      />
                    }
                    label={
                      <Typography sx={{ fontSize: '13px', color: theme.palette.text.secondary }}>
                        By clicking on "Get Started" you agree to the{' '}
                        <Link href="#" sx={{ color: theme.palette.primary.main, textDecoration: 'none' }}>
                          Terms of Service
                        </Link>{' '}
                        and{' '}
                        <Link href="#" sx={{ color: theme.palette.primary.main, textDecoration: 'none' }}>
                          Privacy Policy
                        </Link>
                        .
                      </Typography>
                    }
                    sx={{ alignItems: 'flex-start', mt: 1 }}
                  />
                  {errors.acceptTerms && (
                    <Typography color="error" variant="caption" sx={{ fontSize: '12px' }}>
                      {errors.acceptTerms.message}
                    </Typography>
                  )}

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
                    {isLoading ? 'Creating Account...' : 'Get Started'}
                  </Button>
                </Stack>
              </Box>
            </CardContent>
          </Card>

          {/* Footer */}
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <Typography
              sx={{
                color: 'text.secondary',
                fontSize: '13px',
              }}
            >
              Already have an account?{' '}
              <Link
                component={RouterLink}
                to="/login"
                sx={{
                  color: 'primary.main',
                  textDecoration: 'none',
                  fontWeight: 500,
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                Log In
              </Link>
            </Typography>
          </Box>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Register;