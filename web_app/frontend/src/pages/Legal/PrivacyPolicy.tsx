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
  Link,
  Alert,
} from '@mui/material';

const PrivacyPolicy: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Box textAlign="center" mb={4}>
          <Typography variant="h3" component="h1" gutterBottom>
            Privacy Policy
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Last updated: {new Date().toLocaleDateString()}
          </Typography>
        </Box>

        <Alert severity="info" sx={{ mb: 4 }}>
          <Typography variant="body2">
            <strong>Quick Summary:</strong> We don't sell your data. We encrypt everything. We delete your files automatically. You're in control.
          </Typography>
        </Alert>

        <Divider sx={{ mb: 4 }} />

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            1. Information We Collect
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            1.1 Account Information
          </Typography>
          <Typography paragraph>
            When you create an account, we collect:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Email address (for login and communications)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Full name (for account personalization)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Password (encrypted and never stored in plain text)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Subscription and billing information (processed by Stripe)" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            1.2 Trial Usage (No Registration)
          </Typography>
          <Typography paragraph>
            For trial users, we collect:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Email address (only when requesting downloads)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Session data (temporary, stored for 1 hour only)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Basic usage analytics (file count, processing time)" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            1.3 File Data
          </Typography>
          <Typography paragraph>
            When you upload PDF files, we temporarily store:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="The original PDF file (encrypted)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Extracted table data" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Processing metadata (file size, processing time, table count)" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            1.4 Usage Analytics
          </Typography>
          <Typography paragraph>
            We collect anonymized usage data to improve our service:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Feature usage patterns" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Error rates and performance metrics" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Browser and device information" />
            </ListItem>
            <ListItem>
              <ListItemText primary="IP addresses (for security and analytics)" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            2. How We Use Your Information
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            2.1 Service Provision
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Process your PDF files and extract table data" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Provide you with extracted results in your preferred format" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Manage your account and subscription" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Provide customer support and technical assistance" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            2.2 Communication
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Send you account-related notifications" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Notify you about service updates and new features" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Send usage limit warnings (when approaching tier limits)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Provide subscription and billing communications" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            2.3 Service Improvement
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Analyze usage patterns to improve our AI algorithms" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Identify and fix technical issues" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Develop new features based on user needs" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            3. Data Security and Encryption
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            3.1 Encryption
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="All data is encrypted in transit using TLS 1.3" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Files are encrypted at rest using AES-256 encryption" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Database is encrypted with industry-standard protocols" />
            </ListItem>
            <ListItem>
              <ListItemText primary="API communications are secured with JWT tokens" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            3.2 Access Controls
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Multi-factor authentication for admin access" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Role-based access control for our team" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Regular security audits and penetration testing" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Automated monitoring for suspicious activities" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            4. Data Retention and Deletion
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            4.1 File Retention
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="Trial files: Automatically deleted after 1 hour"
                secondary="No exceptions - trial data is never retained"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Registered user files: Automatically deleted after 30 days"
                secondary="You can delete files manually at any time"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Processing results: Stored for the same duration as original files"
                secondary="Includes extracted tables and metadata"
              />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            4.2 Account Data
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Account information retained while account is active" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Billing records retained for 7 years (legal requirement)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Usage analytics anonymized after 2 years" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Account deletion available upon request" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            5. Third-Party Services
          </Typography>
          
          <Typography paragraph>
            We use carefully selected third-party services to provide our functionality:
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            5.1 Payment Processing
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="Stripe: Handles all payment processing and billing"
                secondary="Subject to Stripe's privacy policy - we never store full credit card information"
              />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            5.2 Email Services
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="SendGrid: Delivers transactional emails"
                secondary="Only receives email addresses and message content"
              />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            5.3 Infrastructure
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="Cloud hosting providers with SOC 2 compliance"
                secondary="Data stored in secure, encrypted data centers"
              />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            6. Your Rights and Controls
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            6.1 Data Access and Portability
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Download all your processed files and data" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Request a copy of your account information" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Export your data in standard formats (JSON, CSV)" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            6.2 Data Control
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Delete individual files at any time" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Update your account information" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Opt out of non-essential communications" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Request complete account deletion" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            6.3 GDPR Rights (EU Users)
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Right to be forgotten (complete data deletion)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Right to data portability" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Right to rectification (data correction)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Right to restrict processing" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            7. Cookies and Tracking
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            7.1 Essential Cookies
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Authentication tokens (required for login)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Session management (trial and registered users)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Security features (CSRF protection)" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            7.2 Analytics Cookies
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Anonymous usage analytics (can be disabled)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Performance monitoring" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Error tracking for service improvement" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            8. Children's Privacy
          </Typography>
          <Typography paragraph>
            Our service is not intended for children under 13. We do not knowingly collect personal information from children under 13. If we become aware that we have collected such information, we will delete it immediately.
          </Typography>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            9. International Data Transfers
          </Typography>
          <Typography paragraph>
            Your data may be processed in countries other than your own. We ensure adequate protection through:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Standard Contractual Clauses (SCCs)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Adequacy decisions where applicable" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Strong encryption during transfer and storage" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            10. Changes to This Policy
          </Typography>
          <Typography paragraph>
            We may update this privacy policy to reflect changes in our practices or legal requirements. We will:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Notify you via email for significant changes" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Post updates on our website" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Provide 30 days notice for material changes" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Maintain previous versions for reference" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            11. Contact Us
          </Typography>
          <Typography paragraph>
            For privacy-related questions or to exercise your rights:
          </Typography>
          <Typography paragraph>
            <strong>Privacy Officer:</strong> privacy@pdfextractor.com<br />
            <strong>General Contact:</strong> support@pdfextractor.com<br />
            <strong>Data Protection:</strong> dpo@pdfextractor.com
          </Typography>
          <Typography paragraph>
            <strong>Mailing Address:</strong><br />
            PDF Table Extractor, Inc.<br />
            Attn: Privacy Officer<br />
            [Your Company Address]
          </Typography>
        </Box>

        <Divider sx={{ my: 4 }} />

        <Box textAlign="center">
          <Typography variant="body2" color="text.secondary" mb={2}>
            We are committed to protecting your privacy and maintaining transparency about our data practices. This policy is written in plain language to help you understand exactly how we handle your information.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Questions? Contact us anytime at{' '}
            <Link href="mailto:privacy@pdfextractor.com" color="primary">
              privacy@pdfextractor.com
            </Link>
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default PrivacyPolicy;