import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Email,
  Phone,
  LocationOn,
  AccessTime,
  Send,
  BugReport,
  Help,
  Feedback,
  Business,
  Security,
} from '@mui/icons-material';
import toast from 'react-hot-toast';

const Contact: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    category: '',
    message: '',
    urgency: 'medium'
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.message) {
      toast.error('Please fill in all required fields');
      return;
    }

    setSubmitting(true);
    
    try {
      const response = await fetch('http://localhost:9700/api/contact/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setSubmitted(true);
        toast.success(result.message);
        
        // Reset form
        setFormData({
          name: '',
          email: '',
          subject: '',
          category: '',
          message: '',
          urgency: 'medium'
        });
      } else {
        toast.error(result.message || 'Failed to send message. Please try again.');
      }
      
    } catch (error) {
      console.error('Contact form error:', error);
      toast.error('Failed to send message. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const contactInfo = [
    {
      icon: <Email />,
      title: 'Email Support',
      details: 'support@pdfextractor.com',
      description: 'General inquiries and support requests'
    },
    {
      icon: <BugReport />,
      title: 'Technical Issues',
      details: 'tech@pdfextractor.com',
      description: 'Bug reports and technical problems'
    },
    {
      icon: <Business />,
      title: 'Business Inquiries',
      details: 'business@pdfextractor.com',
      description: 'Enterprise plans and partnerships'
    },
    {
      icon: <Security />,
      title: 'Security & Privacy',
      details: 'security@pdfextractor.com',
      description: 'Security concerns and privacy questions'
    }
  ];

  const responseTime = [
    { urgency: 'Low', time: '2-3 business days', color: '#10b981' },
    { urgency: 'Medium', time: '12-24 hours', color: '#f59e0b' },
    { urgency: 'High', time: '4-6 hours', color: '#ef4444' },
    { urgency: 'Critical', time: '1-2 hours', color: '#dc2626' }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h3" component="h1" gutterBottom>
          Contact Support
        </Typography>
        <Typography variant="h6" color="text.secondary" mb={2}>
          Get help with PDF Table Extractor - we're here to assist you!
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Contact Form */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>
              Send us a Message
            </Typography>
            <Typography color="text.secondary" mb={3}>
              Fill out the form below and we'll respond according to your urgency level.
            </Typography>

            {submitted && (
              <Alert severity="success" sx={{ mb: 3 }}>
                <Typography fontWeight={600}>Message sent successfully!</Typography>
                <Typography>
                  We've received your message and will respond within our typical response time. 
                  Check your email for a confirmation.
                </Typography>
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Full Name"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    required
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    required
                    variant="outlined"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth variant="outlined">
                    <InputLabel>Category</InputLabel>
                    <Select
                      value={formData.category}
                      onChange={(e) => handleInputChange('category', e.target.value)}
                      label="Category"
                    >
                      <MenuItem value="">
                        <em>Select a category</em>
                      </MenuItem>
                      <MenuItem value="technical">Technical Support</MenuItem>
                      <MenuItem value="billing">Billing & Subscriptions</MenuItem>
                      <MenuItem value="feature">Feature Request</MenuItem>
                      <MenuItem value="bug">Bug Report</MenuItem>
                      <MenuItem value="api">API Support</MenuItem>
                      <MenuItem value="enterprise">Enterprise Inquiry</MenuItem>
                      <MenuItem value="other">Other</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth variant="outlined">
                    <InputLabel>Urgency Level</InputLabel>
                    <Select
                      value={formData.urgency}
                      onChange={(e) => handleInputChange('urgency', e.target.value)}
                      label="Urgency Level"
                    >
                      <MenuItem value="low">Low - General inquiry</MenuItem>
                      <MenuItem value="medium">Medium - Standard support</MenuItem>
                      <MenuItem value="high">High - Blocking issue</MenuItem>
                      <MenuItem value="critical">Critical - Service down</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Subject"
                    value={formData.subject}
                    onChange={(e) => handleInputChange('subject', e.target.value)}
                    variant="outlined"
                    placeholder="Brief description of your inquiry"
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Message"
                    multiline
                    rows={6}
                    value={formData.message}
                    onChange={(e) => handleInputChange('message', e.target.value)}
                    required
                    variant="outlined"
                    placeholder="Please describe your issue or question in detail..."
                  />
                </Grid>

                <Grid item xs={12}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={submitting}
                    startIcon={submitting ? undefined : <Send />}
                    sx={{ py: 1.5, px: 4 }}
                  >
                    {submitting ? 'Sending...' : 'Send Message'}
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </Grid>

        {/* Contact Information */}
        <Grid item xs={12} lg={4}>
          <Box>
            {/* Contact Methods */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Contact Information
              </Typography>
              
              {contactInfo.map((info, index) => (
                <Box key={index} mb={2}>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Box sx={{ color: 'primary.main', mr: 1 }}>
                      {info.icon}
                    </Box>
                    <Typography variant="subtitle1" fontWeight={600}>
                      {info.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="primary.main" mb={0.5}>
                    {info.details}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {info.description}
                  </Typography>
                  {index < contactInfo.length - 1 && <Divider sx={{ mt: 2 }} />}
                </Box>
              ))}
            </Paper>

            {/* Response Times */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                <AccessTime sx={{ mr: 1, verticalAlign: 'middle' }} />
                Response Times
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Expected response times based on urgency:
              </Typography>
              
              {responseTime.map((time, index) => (
                <Box key={index} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">{time.urgency}:</Typography>
                  <Typography variant="body2" fontWeight={600} sx={{ color: time.color }}>
                    {time.time}
                  </Typography>
                </Box>
              ))}
              
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Enterprise customers receive priority support with faster response times.
                </Typography>
              </Alert>
            </Paper>

            {/* Office Hours */}
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Support Hours
              </Typography>
              <List dense>
                <ListItem disablePadding>
                  <ListItemText 
                    primary="Monday - Friday"
                    secondary="9:00 AM - 6:00 PM EST"
                  />
                </ListItem>
                <ListItem disablePadding>
                  <ListItemText 
                    primary="Saturday"
                    secondary="10:00 AM - 4:00 PM EST"
                  />
                </ListItem>
                <ListItem disablePadding>
                  <ListItemText 
                    primary="Sunday"
                    secondary="Closed (Emergency only)"
                  />
                </ListItem>
              </List>
              
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Critical issues are monitored 24/7. We'll respond to urgent matters outside business hours.
                </Typography>
              </Alert>
            </Paper>
          </Box>
        </Grid>
      </Grid>

      {/* FAQ Link */}
      <Box textAlign="center" mt={6}>
        <Paper sx={{ p: 4, bgcolor: 'grey.50' }}>
          <Help sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Looking for Quick Answers?
          </Typography>
          <Typography color="text.secondary" mb={3}>
            Check our FAQ section for instant answers to common questions.
          </Typography>
          <Button variant="contained" size="large" href="/faq">
            Browse FAQ
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default Contact;