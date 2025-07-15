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
} from '@mui/material';

const TermsOfService: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Box textAlign="center" mb={4}>
          <Typography variant="h3" component="h1" gutterBottom>
            Terms of Service
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Last updated: {new Date().toLocaleDateString()}
          </Typography>
        </Box>

        <Divider sx={{ mb: 4 }} />

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            1. Acceptance of Terms
          </Typography>
          <Typography paragraph>
            By accessing and using PDF Table Extractor ("Service"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by these terms, please do not use this service.
          </Typography>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            2. Description of Service
          </Typography>
          <Typography paragraph>
            PDF Table Extractor is a SaaS platform that uses artificial intelligence to extract tables from PDF documents. Our service includes:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="AI-powered table extraction from PDF files" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Intelligent column mapping and data processing" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Export functionality in multiple formats (Excel, CSV)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="API access for automated processing" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Trial functionality for testing without registration" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            3. Trial Service
          </Typography>
          <Typography paragraph>
            We offer a trial service that allows users to test our platform without registration:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Maximum 3 files per session" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Limited to first 2 tables per document" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Maximum 10 rows per table displayed" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Email required for download" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Files automatically deleted after 1 hour" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            4. User Accounts and Registration
          </Typography>
          <Typography paragraph>
            To access the full service, you must register for an account. You agree to:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Provide accurate and complete registration information" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Maintain the security of your password and account" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Accept responsibility for all activities under your account" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Notify us immediately of any unauthorized use" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            5. Subscription Plans and Billing
          </Typography>
          <Typography paragraph>
            Our service offers multiple subscription tiers:
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="Free Tier: 5 files per month at no cost"
                secondary="No credit card required, full access to basic features"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Basic Plan: $9.99/month for 50 files"
                secondary="Includes API access and priority support"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Pro Plan: $29.99/month for 200 files"
                secondary="Advanced features and faster processing"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Enterprise Plan: $99.99/month for unlimited files"
                secondary="Dedicated support and custom integrations"
              />
            </ListItem>
          </List>
          <Typography paragraph>
            Billing occurs monthly in advance. You may cancel your subscription at any time through your account dashboard.
          </Typography>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            6. Acceptable Use Policy
          </Typography>
          <Typography paragraph>
            You agree not to use the service for:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Processing illegal, copyrighted, or confidential content without authorization" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Attempting to reverse engineer or compromise our systems" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Uploading malware, viruses, or malicious code" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Violating any applicable laws or regulations" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Sharing account credentials with unauthorized parties" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            7. Data Privacy and Security
          </Typography>
          <Typography paragraph>
            We take your privacy seriously:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="All uploaded files are encrypted in transit and at rest" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Files are automatically deleted after 30 days (trial files after 1 hour)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="We do not share your data with third parties" />
            </ListItem>
            <ListItem>
              <ListItemText primary="You retain all rights to your uploaded content" />
            </ListItem>
          </List>
          <Typography paragraph>
            For detailed information, please review our{' '}
            <Link href="/privacy-policy" color="primary">
              Privacy Policy
            </Link>.
          </Typography>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            8. Service Availability
          </Typography>
          <Typography paragraph>
            While we strive for 99.9% uptime, we cannot guarantee uninterrupted service. We reserve the right to:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Perform maintenance and updates" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Suspend service for security or technical reasons" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Modify features and functionality with notice" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            9. Limitations of Liability
          </Typography>
          <Typography paragraph>
            Our service is provided "as is" without warranties. We are not liable for:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Accuracy of extracted data" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Loss of data or business interruption" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Indirect, incidental, or consequential damages" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Issues arising from third-party integrations" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            10. Termination
          </Typography>
          <Typography paragraph>
            Either party may terminate this agreement at any time:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="You may cancel your subscription through your account dashboard" />
            </ListItem>
            <ListItem>
              <ListItemText primary="We may terminate accounts for violation of these terms" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Upon termination, access to the service will cease immediately" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Data will be deleted according to our retention policy" />
            </ListItem>
          </List>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            11. Changes to Terms
          </Typography>
          <Typography paragraph>
            We reserve the right to modify these terms at any time. We will notify users of significant changes via email or through the service. Continued use of the service after changes constitutes acceptance of the new terms.
          </Typography>
        </Box>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            12. Contact Information
          </Typography>
          <Typography paragraph>
            For questions about these terms, please contact us:
          </Typography>
          <Typography paragraph>
            Email: legal@pdfextractor.com<br />
            Address: PDF Table Extractor, Inc.<br />
            [Your Company Address]
          </Typography>
        </Box>

        <Divider sx={{ my: 4 }} />

        <Box textAlign="center">
          <Typography variant="body2" color="text.secondary">
            By using PDF Table Extractor, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default TermsOfService;