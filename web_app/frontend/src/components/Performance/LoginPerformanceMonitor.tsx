import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Alert,
  Button,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Speed,
  NetworkCheck,
  Refresh,
} from '@mui/icons-material';
import api from '../../services/api';

interface PerformanceMetrics {
  apiHealth: {
    status: 'good' | 'slow' | 'error';
    responseTime: number;
    timestamp: Date;
  };
  authEndpoint: {
    status: 'good' | 'slow' | 'error';
    responseTime: number;
    timestamp: Date;
  };
  userEndpoint: {
    status: 'good' | 'slow' | 'error';
    responseTime: number;
    timestamp: Date;
  };
  networkLatency: number;
}

const LoginPerformanceMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    apiHealth: { status: 'good', responseTime: 0, timestamp: new Date() },
    authEndpoint: { status: 'good', responseTime: 0, timestamp: new Date() },
    userEndpoint: { status: 'good', responseTime: 0, timestamp: new Date() },
    networkLatency: 0,
  });
  const [isChecking, setIsChecking] = useState(false);
  const [lastCheck, setLastCheck] = useState<Date>(new Date());

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return 'success';
      case 'slow': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good': return <CheckCircle color="success" />;
      case 'slow': return <Warning color="warning" />;
      case 'error': return <Error color="error" />;
      default: return <NetworkCheck />;
    }
  };

  const getStatusFromTime = (responseTime: number) => {
    if (responseTime < 1000) return 'good';
    if (responseTime < 3000) return 'slow';
    return 'error';
  };

  const measureEndpoint = async (url: string, method: 'GET' | 'POST' = 'GET', data?: any) => {
    const start = performance.now();
    try {
      if (method === 'POST') {
        await api.post(url, data);
      } else {
        await api.get(url);
      }
      const end = performance.now();
      const responseTime = end - start;
      return {
        status: getStatusFromTime(responseTime) as 'good' | 'slow' | 'error',
        responseTime: Math.round(responseTime),
        timestamp: new Date(),
      };
    } catch (error) {
      const end = performance.now();
      const responseTime = end - start;
      return {
        status: 'error' as const,
        responseTime: Math.round(responseTime),
        timestamp: new Date(),
      };
    }
  };

  const runPerformanceCheck = async () => {
    setIsChecking(true);
    
    try {
      // Test API health endpoint
      const healthCheck = await measureEndpoint('/health');
      
      // Test CORS functionality
      const corsCheck = await measureEndpoint('/cors-test');
      
      // Test user endpoint (if authenticated)
      const token = localStorage.getItem('auth-storage');
      let userCheck: {
        status: 'good' | 'slow' | 'error';
        responseTime: number;
        timestamp: Date;
      } = { status: 'good', responseTime: 0, timestamp: new Date() };
      
      if (token) {
        try {
          const authData = JSON.parse(token);
          if (authData.state?.token) {
            userCheck = await measureEndpoint('/users/me');
          }
        } catch (e) {
          // Token parsing failed
        }
      }

      // Measure network latency with a simple ping-like request
      const latencyStart = performance.now();
      try {
        await fetch('http://127.0.0.1:8001/api/health', { 
          method: 'HEAD',
          mode: 'cors',
          headers: {
            'Origin': window.location.origin
          }
        });
        const latencyEnd = performance.now();
        const networkLatency = Math.round(latencyEnd - latencyStart);

        setMetrics({
          apiHealth: healthCheck,
          authEndpoint: corsCheck,
          userEndpoint: userCheck,
          networkLatency,
        });
      } catch (error) {
        setMetrics(prev => ({
          ...prev,
          apiHealth: healthCheck,
          authEndpoint: corsCheck,
          userEndpoint: userCheck,
          networkLatency: 0,
        }));
      }

      setLastCheck(new Date());
    } catch (error) {
      console.error('Performance check failed:', error);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    runPerformanceCheck();
    // Auto-check every 30 seconds
    const interval = setInterval(runPerformanceCheck, 30000);
    return () => clearInterval(interval);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const getOverallStatus = () => {
    if (metrics.apiHealth.status === 'error' || metrics.authEndpoint.status === 'error' || metrics.userEndpoint.status === 'error') {
      return 'error';
    }
    if (metrics.apiHealth.status === 'slow' || metrics.authEndpoint.status === 'slow' || metrics.userEndpoint.status === 'slow') {
      return 'slow';
    }
    return 'good';
  };

  const getRecommendations = () => {
    const recommendations = [];
    
    if (metrics.apiHealth.responseTime > 2000) {
      recommendations.push('Backend response is slow. Check if the backend server is running properly.');
    }
    
    if (metrics.authEndpoint.responseTime > 2000) {
      recommendations.push('CORS/Auth endpoint is slow. This may cause delays during login.');
    } else if (metrics.authEndpoint.status === 'error') {
      recommendations.push('CORS issues detected. Check that frontend and backend URLs are properly configured.');
    }
    
    if (metrics.userEndpoint.responseTime > 2000) {
      recommendations.push('User authentication is slow. This may cause delays during login.');
    }
    
    if (metrics.networkLatency > 1000) {
      recommendations.push('High network latency detected. Check your internet connection.');
    }
    
    if (recommendations.length === 0) {
      recommendations.push('All systems are operating normally. Login should be fast.');
    }
    
    return recommendations;
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" fontWeight={600}>
            Login Performance Monitor
          </Typography>
          <Button
            size="small"
            startIcon={isChecking ? <CircularProgress size={16} /> : <Refresh />}
            onClick={runPerformanceCheck}
            disabled={isChecking}
          >
            {isChecking ? 'Checking...' : 'Check Now'}
          </Button>
        </Box>

        <Alert 
          severity={getOverallStatus() === 'good' ? 'success' : getOverallStatus() === 'slow' ? 'warning' : 'error'}
          sx={{ mb: 2 }}
        >
          <Typography variant="body2">
            Overall Status: <strong>{getOverallStatus().toUpperCase()}</strong>
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Last checked: {lastCheck.toLocaleTimeString()}
          </Typography>
        </Alert>

        <List dense>
          <ListItem>
            <ListItemIcon>
              {getStatusIcon(metrics.apiHealth.status)}
            </ListItemIcon>
            <ListItemText
              primary="API Health"
              secondary={`${metrics.apiHealth.responseTime}ms`}
            />
            <Chip 
              label={metrics.apiHealth.status.toUpperCase()} 
              color={getStatusColor(metrics.apiHealth.status)}
              size="small"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              {getStatusIcon(metrics.authEndpoint.status)}
            </ListItemIcon>
            <ListItemText
              primary="CORS & Auth Endpoint"
              secondary={`${metrics.authEndpoint.responseTime}ms`}
            />
            <Chip 
              label={metrics.authEndpoint.status.toUpperCase()} 
              color={getStatusColor(metrics.authEndpoint.status)}
              size="small"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              {getStatusIcon(metrics.userEndpoint.status)}
            </ListItemIcon>
            <ListItemText
              primary="User Authentication"
              secondary={`${metrics.userEndpoint.responseTime}ms`}
            />
            <Chip 
              label={metrics.userEndpoint.status.toUpperCase()} 
              color={getStatusColor(metrics.userEndpoint.status)}
              size="small"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <Speed color={metrics.networkLatency > 1000 ? 'error' : metrics.networkLatency > 500 ? 'warning' : 'success'} />
            </ListItemIcon>
            <ListItemText
              primary="Network Latency"
              secondary={`${metrics.networkLatency}ms`}
            />
            <Chip 
              label={metrics.networkLatency > 1000 ? 'SLOW' : 'OK'} 
              color={metrics.networkLatency > 1000 ? 'error' : 'success'}
              size="small"
            />
          </ListItem>
        </List>

        <Box mt={3}>
          <Typography variant="subtitle2" fontWeight={600} mb={1}>
            Recommendations:
          </Typography>
          {getRecommendations().map((rec, index) => (
            <Alert key={index} severity="info" sx={{ mb: 1 }}>
              <Typography variant="body2">{rec}</Typography>
            </Alert>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default LoginPerformanceMonitor;
