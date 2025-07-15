import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Chip,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  CloudUpload,
  FolderOpen,
  Person,
  Api,
  Logout,
  Settings,
  Help,
  Notifications,
  Payment,
  AdminPanelSettings,
  Receipt,
  AutoAwesome,
  Business,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import ThemeToggle from '../ThemeToggle/ThemeToggle';
import Footer from '../Footer/Footer';

const drawerWidth = 240;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const theme = useTheme();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isAdmin = user?.email === 'admin@pdfextractor.com' || 
                  user?.email === 'admin@test.com' || 
                  user?.email === 'admin@duehub.app' ||
                  user?.id === 1 || user?.id === 2 ||
                  user?.tier === 'enterprise';

  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
    { text: 'Upload Files', icon: <CloudUpload />, path: '/upload' },
    { text: 'File Manager', icon: <FolderOpen />, path: '/files' },
    { text: 'Enterprise Integrations', icon: <Business />, path: '/enterprise-integrations' },
    { text: 'Subscription', icon: <Payment />, path: '/subscription' },
    { text: 'API Documentation', icon: <Api />, path: '/api-docs' },
    ...(isAdmin ? [
      { text: 'Admin Panel', icon: <AdminPanelSettings />, path: '/management' },
      { text: 'User Management', icon: <Person />, path: '/management/users' },
      { text: 'Transaction History', icon: <Receipt />, path: '/management/transactions' }
    ] : []),
  ];

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'free': return theme.palette.text.secondary;
      case 'basic': return theme.palette.primary.main;
      case 'pro': return theme.palette.primary.main;
      case 'enterprise': return theme.palette.primary.main;
      default: return theme.palette.text.secondary;
    }
  };

  const getTierLabel = (tier: string) => {
    return tier.charAt(0).toUpperCase() + tier.slice(1);
  };

  const drawer = (
    <div>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ 
              flexGrow: 1, 
              fontWeight: 600,
              color: 'text.primary',
            }}
          >
            PDF Extractor
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      
      {/* User Info */}
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ mr: 2, bgcolor: 'text.secondary', width: 32, height: 32, fontSize: '0.875rem' }}>
            {user?.full_name?.charAt(0).toUpperCase()}
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography 
              variant="body2" 
              noWrap
              sx={{ 
                fontWeight: 500,
                color: 'text.primary',
                fontSize: '0.875rem',
              }}
            >
              {user?.full_name}
            </Typography>
            <Typography 
              variant="caption" 
              color="text.secondary"
              noWrap
              sx={{ fontSize: '0.75rem' }}
            >
              {user?.email}
            </Typography>
          </Box>
        </Box>
        
        <Chip
          label={getTierLabel(user?.tier || 'free')}
          size="small"
          variant="outlined"
          sx={{
            borderColor: 'divider',
            color: 'text.secondary',
            fontWeight: 500,
            mb: 1,
            fontSize: '0.75rem',
            height: 24,
          }}
        />
        
        <Typography 
          variant="caption" 
          display="block" 
          sx={{ 
            color: 'text.disabled',
            fontSize: '0.75rem',
          }}
        >
          {user?.files_processed_this_month || 0} files this month
        </Typography>
      </Box>
      
      <Divider />
      
      <List sx={{ px: 1, py: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 1,
                py: 1,
                px: 2,
                minHeight: 36,
                '&.Mui-selected': {
                  bgcolor: 'action.selected',
                  '& .MuiListItemIcon-root': {
                    color: 'text.primary',
                  },
                  '& .MuiListItemText-primary': {
                    color: 'text.primary',
                    fontWeight: 500,
                  },
                },
                '&:hover': {
                  bgcolor: 'action.hover',
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 32, color: 'text.secondary' }}>
                <Box sx={{ '& svg': { fontSize: 18 } }}>
                  {item.icon}
                </Box>
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                sx={{
                  '& .MuiListItemText-primary': {
                    fontSize: '0.875rem',
                    fontWeight: 400,
                    color: 'text.secondary',
                  }
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          bgcolor: 'background.default',
          color: 'text.primary',
          boxShadow: 'none',
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ 
              flexGrow: 1,
              fontWeight: 500,
              color: 'text.primary',
              fontSize: '1rem',
            }}
          >
            {menuItems.find(item => item.path === location.pathname)?.text || 'Dashboard'}
          </Typography>
          
          <ThemeToggle />
          
          <IconButton
            onClick={handleProfileMenuOpen}
            size="small"
            sx={{ ml: 1 }}
            aria-controls="profile-menu"
            aria-haspopup="true"
          >
            <Avatar sx={{ width: 28, height: 28, bgcolor: 'text.secondary', fontSize: '0.75rem' }}>
              {user?.full_name?.charAt(0).toUpperCase()}
            </Avatar>
          </IconButton>
        </Toolbar>
      </AppBar>
      
      {/* Profile Menu */}
      <Menu
        id="profile-menu"
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        onClick={handleProfileMenuClose}
        PaperProps={{
          elevation: 0,
          sx: {
            mt: 1,
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
            minWidth: 160,
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem 
          onClick={() => navigate('/profile')}
          sx={{ fontSize: '0.875rem', py: 1 }}
        >
          Profile
        </MenuItem>
        <MenuItem 
          onClick={() => navigate('/subscription')}
          sx={{ fontSize: '0.875rem', py: 1 }}
        >
          Subscription
        </MenuItem>
        <Divider sx={{ my: 0.5 }} />
        <MenuItem 
          onClick={handleLogout}
          sx={{ fontSize: '0.875rem', py: 1, color: 'text.secondary' }}
        >
          Sign out
        </MenuItem>
      </Menu>

      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="navigation menu"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: '64px',
          bgcolor: 'background.default',
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        <Box sx={{ flexGrow: 1, p: 2 }}>
          {children}
        </Box>
        <Footer />
      </Box>
    </Box>
  );
};

export default Layout;