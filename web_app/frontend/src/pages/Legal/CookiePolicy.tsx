import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';

const CookiePolicy: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Box textAlign="center" mb={4}>
          <Typography variant="h3" component="h1" gutterBottom>
            Cookie Policy
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Last updated: {new Date().toLocaleDateString()}
          </Typography>
        </Box>

        <Alert severity="info" sx={{ mb: 4 }}>
          <Typography variant="body2">
            <strong>Quick Summary:</strong> We use essential cookies for functionality and optional cookies for analytics. You can control them through your browser settings.
          </Typography>
        </Alert>

        <Divider sx={{ mb: 4 }} />

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            1. What Are Cookies?
          </Typography>
          <Typography paragraph>
            Cookies are small text files placed on your device when you visit our website. They help us provide you with a better experience by remembering your preferences and improving our service.
          </Typography>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            2. Types of Cookies We Use
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            2.1 Essential Cookies (Always Active)
          </Typography>
          <Typography paragraph>
            These cookies are necessary for the website to function and cannot be switched off:
          </Typography>
          
          <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Cookie Name</strong></TableCell>
                  <TableCell><strong>Purpose</strong></TableCell>
                  <TableCell><strong>Duration</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>sessionId</TableCell>
                  <TableCell>User session identification</TableCell>
                  <TableCell>Session</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>auth_token</TableCell>
                  <TableCell>User authentication</TableCell>
                  <TableCell>30 days</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>csrf_token</TableCell>
                  <TableCell>Security protection</TableCell>
                  <TableCell>Session</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>trial_session</TableCell>
                  <TableCell>Trial user tracking</TableCell>
                  <TableCell>1 hour</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            2.2 Performance Cookies (Optional)
          </Typography>
          <Typography paragraph>
            These cookies help us understand how visitors use our website:
          </Typography>
          
          <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Cookie Name</strong></TableCell>
                  <TableCell><strong>Purpose</strong></TableCell>
                  <TableCell><strong>Duration</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>analytics_session</TableCell>
                  <TableCell>Anonymous usage statistics</TableCell>
                  <TableCell>30 days</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>performance_metrics</TableCell>
                  <TableCell>Page load times and errors</TableCell>
                  <TableCell>7 days</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>feature_usage</TableCell>
                  <TableCell>Track feature adoption</TableCell>
                  <TableCell>90 days</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            2.3 Preference Cookies (Optional)
          </Typography>
          <Typography paragraph>
            These cookies remember your choices and preferences:
          </Typography>
          
          <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Cookie Name</strong></TableCell>
                  <TableCell><strong>Purpose</strong></TableCell>
                  <TableCell><strong>Duration</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>theme_preference</TableCell>
                  <TableCell>Dark/light mode setting</TableCell>
                  <TableCell>1 year</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>language_preference</TableCell>
                  <TableCell>Language selection</TableCell>
                  <TableCell>1 year</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>dashboard_layout</TableCell>
                  <TableCell>Dashboard customization</TableCell>
                  <TableCell>1 year</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            3. Third-Party Cookies
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            3.1 Stripe (Payment Processing)
          </Typography>
          <Typography paragraph>
            When you make a payment, Stripe may set cookies for secure transaction processing:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Used for fraud prevention and security" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Required for payment processing" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Governed by Stripe's privacy policy" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            3.2 CDN and Infrastructure
          </Typography>
          <Typography paragraph>
            Our hosting providers may set cookies for:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Load balancing and performance optimization" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Security and DDoS protection" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Geographic content delivery" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            4. Managing Your Cookie Preferences
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            4.1 Browser Settings
          </Typography>
          <Typography paragraph>
            You can control cookies through your browser settings:
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="Chrome: Settings → Privacy and Security → Cookies"
                secondary="chrome://settings/cookies"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Firefox: Settings → Privacy & Security → Cookies"
                secondary="about:preferences#privacy"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Safari: Preferences → Privacy → Cookies"
                secondary="Develop menu → Disable Cookies"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Edge: Settings → Privacy → Cookies"
                secondary="edge://settings/privacy"
              />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            4.2 Cookie Banner
          </Typography>
          <Typography paragraph>
            When you first visit our site, you'll see a cookie banner with options to:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Accept all cookies" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Accept only essential cookies" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Customize your preferences" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            4.3 Consequences of Disabling Cookies
          </Typography>
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>Important:</strong> Disabling essential cookies may prevent the website from functioning properly.
            </Typography>
          </Alert>
          <List>
            <ListItem>
              <ListItemText 
                primary="Essential cookies disabled: Login and core features won't work"
                secondary="You won't be able to access your account or process files"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Performance cookies disabled: We can't improve the service"
                secondary="No impact on functionality"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Preference cookies disabled: Settings won't be remembered"
                secondary="You'll need to set preferences each visit"
              />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            5. Data Protection and Privacy
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            5.1 Personal Data in Cookies
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Essential cookies contain unique identifiers, not personal information" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Analytics cookies use anonymous data only" />
            </ListItem>
            <ListItem>
              <ListItemText primary="No sensitive data is stored in cookies" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            5.2 Cookie Security
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="All cookies are transmitted over HTTPS" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Secure and HttpOnly flags set where appropriate" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Regular security audits of cookie usage" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            6. Legal Compliance
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            6.1 GDPR Compliance (EU Users)
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Explicit consent for non-essential cookies" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Right to withdraw consent at any time" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Clear information about cookie purposes" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            6.2 CCPA Compliance (California Users)
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Transparency about data collection" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Right to opt-out of data sharing" />
            </ListItem>
            <ListItem>
              <ListItemText primary="No sale of personal information" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            7. Changes to This Policy
          </Typography>
          <Typography paragraph>
            We may update this Cookie Policy to reflect changes in our practices or legal requirements. We will:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Post updates on our website" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Notify you of significant changes" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Update the 'Last updated' date" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            8. Contact Us
          </Typography>
          <Typography paragraph>
            For questions about our cookie practices:
          </Typography>
          <Typography paragraph>
            <strong>Email:</strong> privacy@pdfextractor.com<br />
            <strong>Subject:</strong> Cookie Policy Inquiry<br />
            <strong>Response Time:</strong> Within 5 business days
          </Typography>
        </Box>

        <Divider sx={{ my: 4 }} />

        <Box textAlign="center">
          <Typography variant="body2" color="text.secondary">
            This Cookie Policy works in conjunction with our Privacy Policy and Terms of Service to provide you with complete information about our data practices.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default CookiePolicy;