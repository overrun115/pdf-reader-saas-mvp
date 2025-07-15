import React from 'react';
import { Box, Typography, Link, Container, Grid, Divider } from '@mui/material';
import { useTheme } from '@mui/material/styles';

const Footer: React.FC = () => {
  const theme = useTheme();

  return (
    <Box
      component="footer"
      sx={{
        mt: 'auto',
        py: 3,
        px: 2,
        bgcolor: 'background.paper',
        borderTop: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          {/* Company Info */}
          <Grid item xs={12} md={4}>
            <Typography variant="h6" color="text.primary" gutterBottom>
              PDF Reader
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Professional PDF processing and data extraction for businesses.
            </Typography>
          </Grid>

          {/* Product Links */}
          <Grid item xs={12} md={2}>
            <Typography variant="subtitle1" color="text.primary" gutterBottom>
              Product
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link href="/features" color="text.secondary" underline="hover">
                Features
              </Link>
              <Link href="/pricing" color="text.secondary" underline="hover">
                Pricing
              </Link>
              <Link href="/api-docs" color="text.secondary" underline="hover">
                API
              </Link>
            </Box>
          </Grid>

          {/* Support Links */}
          <Grid item xs={12} md={2}>
            <Typography variant="subtitle1" color="text.primary" gutterBottom>
              Support
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link href="/faq" color="text.secondary" underline="hover">
                FAQ
              </Link>
              <Link href="/contact" color="text.secondary" underline="hover">
                Contact
              </Link>
              <Link href="/help" color="text.secondary" underline="hover">
                Help Center
              </Link>
            </Box>
          </Grid>

          {/* Legal Links */}
          <Grid item xs={12} md={2}>
            <Typography variant="subtitle1" color="text.primary" gutterBottom>
              Legal
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link href="/legal/privacy" color="text.secondary" underline="hover">
                Privacy Policy
              </Link>
              <Link href="/legal/terms" color="text.secondary" underline="hover">
                Terms of Service
              </Link>
              <Link href="/legal/cookies" color="text.secondary" underline="hover">
                Cookie Policy
              </Link>
            </Box>
          </Grid>

          {/* Company Links */}
          <Grid item xs={12} md={2}>
            <Typography variant="subtitle1" color="text.primary" gutterBottom>
              Company
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link href="/about" color="text.secondary" underline="hover">
                About
              </Link>
              <Link href="/careers" color="text.secondary" underline="hover">
                Careers
              </Link>
              <Link href="/blog" color="text.secondary" underline="hover">
                Blog
              </Link>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 2,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} PDF Reader. All rights reserved.
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 3 }}>
            <Link href="/legal/privacy" color="text.secondary" underline="hover">
              Privacy
            </Link>
            <Link href="/legal/terms" color="text.secondary" underline="hover">
              Terms
            </Link>
            <Link href="/legal/cookies" color="text.secondary" underline="hover">
              Cookies
            </Link>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;