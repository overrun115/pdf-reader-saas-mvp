import React, { useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Chip,
  Divider,
  Container,
  useTheme,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Switch,
  FormControlLabel,
  Tab,
  Tabs,
} from '@mui/material';
import {
  Business,
  CloudUpload,
  Api,
  Security,
  Sync,
  CheckCircle,
  Error,
  Warning,
  Settings,
  Add,
  Link,
  Storage,
  Cloud,
  Widgets,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../store/authStore';
import toast from 'react-hot-toast';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

const EnterpriseIntegrations: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [configDialog, setConfigDialog] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<any>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleConfigureIntegration = (integration: any) => {
    setSelectedIntegration(integration);
    setConfigDialog(true);
  };

  const handleSaveConfiguration = () => {
    toast.success(`${selectedIntegration?.name} integration configured successfully!`);
    setConfigDialog(false);
    setSelectedIntegration(null);
  };

  const crmIntegrations = [
    {
      name: 'Salesforce',
      description: 'Sync documents with Salesforce CRM records',
      icon: '☁️',
      status: 'connected',
      features: ['Auto-sync documents', 'Lead attachments', 'Opportunity files'],
      color: 'primary.main'
    },
    {
      name: 'HubSpot',
      description: 'Integrate with HubSpot marketing and sales',
      icon: '🟠',
      status: 'available',
      features: ['Contact documents', 'Deal attachments', 'Marketing materials'],
      color: 'warning.main'
    },
    {
      name: 'Pipedrive',
      description: 'Connect with Pipedrive sales pipeline',
      icon: '🟢',
      status: 'available',
      features: ['Pipeline documents', 'Activity files', 'Contact sheets'],
      color: 'success.main'
    }
  ];

  const erpIntegrations = [
    {
      name: 'SAP',
      description: 'Enterprise resource planning integration',
      icon: '🔷',
      status: 'enterprise',
      features: ['Invoice processing', 'Purchase orders', 'Financial reports'],
      color: 'info.main'
    },
    {
      name: 'Oracle',
      description: 'Oracle ERP and database connectivity',
      icon: '🔴',
      status: 'enterprise',
      features: ['Data extraction', 'Report generation', 'Document workflow'],
      color: 'error.main'
    },
    {
      name: 'NetSuite',
      description: 'Cloud business management suite',
      icon: '🟡',
      status: 'available',
      features: ['Financial docs', 'Customer records', 'Inventory reports'],
      color: 'warning.main'
    }
  ];

  const cloudIntegrations = [
    {
      name: 'Google Workspace',
      description: 'Google Drive, Docs, and Sheets integration',
      icon: '🟦',
      status: 'connected',
      features: ['Drive sync', 'Docs conversion', 'Sheets export'],
      color: 'info.main'
    },
    {
      name: 'Microsoft 365',
      description: 'Office 365 and OneDrive connectivity',
      icon: '🟪',
      status: 'connected',
      features: ['OneDrive sync', 'Teams integration', 'Office conversion'],
      color: 'primary.main'
    },
    {
      name: 'AWS S3',
      description: 'Amazon S3 storage integration',
      icon: '🟧',
      status: 'available',
      features: ['Bucket sync', 'Auto backup', 'Archive storage'],
      color: 'warning.main'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'success';
      case 'available': return 'info';
      case 'enterprise': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'connected': return 'Connected';
      case 'available': return 'Available';
      case 'enterprise': return 'Enterprise Only';
      case 'error': return 'Error';
      default: return 'Unknown';
    }
  };

  const renderIntegrationGrid = (integrations: any[], title: string) => (
    <Grid container spacing={3}>
      {integrations.map((integration, index) => (
        <Grid item xs={12} md={6} lg={4} key={index}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 * index }}
          >
            <Card sx={{ height: '100%', position: 'relative' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Avatar sx={{ 
                      width: 48, 
                      height: 48, 
                      bgcolor: 'background.paper',
                      border: `2px solid ${integration.color}`,
                      fontSize: '1.5rem'
                    }}>
                      {integration.icon}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" fontWeight={600}>
                        {integration.name}
                      </Typography>
                      <Chip 
                        label={getStatusText(integration.status)}
                        size="small"
                        color={getStatusColor(integration.status)}
                      />
                    </Box>
                  </Box>
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {integration.description}
                </Typography>
                
                <Box mb={3}>
                  <Typography variant="caption" color="text.secondary" fontWeight={600}>
                    FEATURES:
                  </Typography>
                  <List dense sx={{ py: 0 }}>
                    {integration.features.map((feature: string, featureIndex: number) => (
                      <ListItem key={featureIndex} sx={{ px: 0, py: 0.5 }}>
                        <ListItemAvatar sx={{ minWidth: 20 }}>
                          <CheckCircle sx={{ fontSize: 14, color: 'success.main' }} />
                        </ListItemAvatar>
                        <ListItemText 
                          primary={
                            <Typography variant="body2" fontSize="0.8rem">
                              {feature}
                            </Typography>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
                
                <Button
                  fullWidth
                  variant={integration.status === 'connected' ? 'outlined' : 'contained'}
                  size="small"
                  onClick={() => handleConfigureIntegration(integration)}
                  disabled={integration.status === 'enterprise' && user?.tier !== 'enterprise'}
                  startIcon={integration.status === 'connected' ? <Settings /> : <Add />}
                >
                  {integration.status === 'connected' ? 'Configure' : 'Connect'}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      ))}
    </Grid>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box mb={4}>
          <Typography 
            variant="h4" 
            fontWeight={700} 
            gutterBottom
            sx={{ 
              color: 'text.primary',
              fontFamily: 'Montserrat, sans-serif',
            }}
          >
            Enterprise Integrations 🔗
          </Typography>
          <Typography 
            variant="body1" 
            color="text.secondary" 
            gutterBottom
          >
            Connect your document processing with business systems and cloud platforms
          </Typography>
        </Box>
      </motion.div>

      {/* Integration Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Active Integrations
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      3
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      Connected
                    </Typography>
                  </Box>
                  <Link sx={{ fontSize: 40, color: 'primary.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Available
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      25+
                    </Typography>
                    <Typography variant="body2" color="info.main">
                      Ready to connect
                    </Typography>
                  </Box>
                  <Widgets sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Data Synced
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      1.2K
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      Documents
                    </Typography>
                  </Box>
                  <Sync sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Uptime
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      99.9%
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      This month
                    </Typography>
                  </Box>
                  <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Navigation Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <Box sx={{ mb: 3 }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange}
            sx={{
              '& .MuiTabs-indicator': {
                height: 3,
                borderRadius: 1,
              }
            }}
          >
            <Tab label="CRM Systems" icon={<Business />} iconPosition="start" />
            <Tab label="ERP Systems" icon={<Storage />} iconPosition="start" />
            <Tab label="Cloud Platforms" icon={<Cloud />} iconPosition="start" />
          </Tabs>
        </Box>
      </motion.div>

      <TabPanel value={tabValue} index={0}>
        <Box mb={3}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Customer Relationship Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Integrate with leading CRM platforms to sync documents with customer records
          </Typography>
        </Box>
        {renderIntegrationGrid(crmIntegrations, 'CRM')}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Box mb={3}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Enterprise Resource Planning
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Connect with ERP systems for automated document processing and data extraction
          </Typography>
        </Box>
        {renderIntegrationGrid(erpIntegrations, 'ERP')}
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Box mb={3}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Cloud Storage & Productivity
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sync with cloud storage and productivity platforms for seamless document management
          </Typography>
        </Box>
        {renderIntegrationGrid(cloudIntegrations, 'Cloud')}
      </TabPanel>

      {/* Configuration Dialog */}
      <Dialog 
        open={configDialog} 
        onClose={() => setConfigDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Configure {selectedIntegration?.name} Integration
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                Configure your {selectedIntegration?.name} integration settings. This will enable automatic document synchronization.
              </Typography>
            </Alert>
            
            <TextField
              fullWidth
              label="API Key"
              placeholder="Enter your API key"
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              label="Endpoint URL"
              placeholder="https://api.example.com"
              sx={{ mb: 2 }}
            />
            
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="Enable automatic sync"
            />
            
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="Sync document metadata"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleSaveConfiguration}
          >
            Save Configuration
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default EnterpriseIntegrations;