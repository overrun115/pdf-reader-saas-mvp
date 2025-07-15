import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  InputAdornment,
  Chip,
  Grid,
  Card,
  CardContent,
  Button,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  ExpandMore,
  Search,
  Help,
  QuestionAnswer,
  Security,
  Payment,
  Api,
  BugReport,
  CheckCircle,
  Email,
} from '@mui/icons-material';

const FAQ: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', name: 'All Questions', icon: <Help />, count: 24 },
    { id: 'general', name: 'General', icon: <QuestionAnswer />, count: 8 },
    { id: 'trial', name: 'Trial & Demo', icon: <Help />, count: 5 },
    { id: 'billing', name: 'Billing & Plans', icon: <Payment />, count: 6 },
    { id: 'technical', name: 'Technical', icon: <BugReport />, count: 5 },
    { id: 'api', name: 'API', icon: <Api />, count: 3 },
    { id: 'security', name: 'Security', icon: <Security />, count: 4 },
  ];

  const faqs = [
    // General
    {
      category: 'general',
      question: 'What is PDF Table Extractor?',
      answer: 'PDF Table Extractor is an AI-powered SaaS platform that automatically extracts tables from PDF documents. Our unique intelligent column mapping feature ensures accurate data extraction even from complex multi-page documents.',
      popular: true
    },
    {
      category: 'general',
      question: 'How accurate is the table extraction?',
      answer: 'Our AI achieves 95%+ accuracy on most documents. The accuracy depends on the quality of the original PDF and table formatting. Our intelligent column mapping feature significantly improves accuracy for multi-page documents.',
      popular: true
    },
    {
      category: 'general',
      question: 'What file formats do you support?',
      answer: 'We currently support PDF files only. You can export extracted data in Excel (.xlsx), CSV (.csv), and Word (.docx) formats.',
      popular: false
    },
    {
      category: 'general',
      question: 'Is there a file size limit?',
      answer: 'Yes, file size limits vary by plan: Trial (10MB), Free/Basic (50MB), Pro (100MB), Enterprise (500MB). Contact us for larger file processing needs.',
      popular: false
    },
    
    // Trial & Demo
    {
      category: 'trial',
      question: 'How does the trial work?',
      answer: 'Our trial allows you to test the service without registration. You can upload up to 3 PDF files, see the first 2 tables with the first 10 rows of each. Email is required only for download.',
      popular: true
    },
    {
      category: 'trial',
      question: 'Do I need to provide a credit card for the trial?',
      answer: 'No! Our trial is completely free and requires no credit card. You only need to provide an email address when downloading results.',
      popular: true
    },
    {
      category: 'trial',
      question: 'Can I extend my trial period?',
      answer: 'The trial session lasts 1 hour and allows 3 files. However, you can register for a free account which includes 5 files per month with no time limits.',
      popular: false
    },
    {
      category: 'trial',
      question: 'What happens to my trial data?',
      answer: 'All trial data is automatically deleted after 1 hour for privacy and security. If you need to keep your results, please download them during the session.',
      popular: false
    },
    
    // Billing & Plans
    {
      category: 'billing',
      question: 'What are your pricing plans?',
      answer: 'We offer 4 plans: Free (5 files/month), Basic ($9.99/month, 50 files), Pro ($29.99/month, 200 files), and Enterprise ($99.99/month, unlimited files). All paid plans include API access.',
      popular: true
    },
    {
      category: 'billing',
      question: 'Can I cancel my subscription anytime?',
      answer: 'Yes! You can cancel your subscription at any time from your account dashboard. You\'ll continue to have access until the end of your current billing period.',
      popular: true
    },
    {
      category: 'billing',
      question: 'Do you offer refunds?',
      answer: 'We offer a 30-day money-back guarantee for all paid plans. If you\'re not satisfied, contact us within 30 days for a full refund.',
      popular: false
    },
    {
      category: 'billing',
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards (Visa, MasterCard, American Express) and PayPal through our secure payment processor, Stripe.',
      popular: false
    },
    {
      category: 'billing',
      question: 'Do you offer annual discounts?',
      answer: 'Yes! Save 20% when you pay annually. Annual plans also include priority support and additional features.',
      popular: false
    },
    
    // Technical
    {
      category: 'technical',
      question: 'Why isn\'t my PDF processing correctly?',
      answer: 'Common issues include: scanned PDFs (try OCR), password-protected files, or tables embedded as images. Our AI works best with native PDF tables. Contact support if you need help.',
      popular: true
    },
    {
      category: 'technical',
      question: 'How long does processing take?',
      answer: 'Most files process in 30-60 seconds. Processing time depends on file size, number of tables, and current system load. Enterprise users get priority processing.',
      popular: false
    },
    {
      category: 'technical',
      question: 'Can you handle scanned PDFs?',
      answer: 'Yes! Our system automatically detects scanned content and applies OCR (Optical Character Recognition) technology. However, accuracy may be lower than native PDF tables.',
      popular: false
    },
    {
      category: 'technical',
      question: 'What browsers do you support?',
      answer: 'We support all modern browsers: Chrome, Firefox, Safari, and Edge. For the best experience, we recommend using the latest version of Chrome or Firefox.',
      popular: false
    },
    
    // API
    {
      category: 'api',
      question: 'How do I use the API?',
      answer: 'API access is included with all paid plans. Visit your dashboard to generate API keys, then check our comprehensive API documentation for integration guides and examples.',
      popular: true
    },
    {
      category: 'api',
      question: 'What are the API rate limits?',
      answer: 'Rate limits vary by plan: Basic (10 requests/minute), Pro (50 requests/minute), Enterprise (unlimited). All plans include webhook support for async processing.',
      popular: false
    },
    {
      category: 'api',
      question: 'Do you support webhooks?',
      answer: 'Yes! Webhooks are available on all paid plans. Configure webhook URLs in your dashboard to receive notifications when file processing is complete.',
      popular: false
    },
    
    // Security
    {
      category: 'security',
      question: 'How secure is my data?',
      answer: 'We use enterprise-grade security: AES-256 encryption at rest, TLS 1.3 in transit, SOC 2 compliance, and automatic file deletion after 30 days (1 hour for trial files).',
      popular: true
    },
    {
      category: 'security',
      question: 'Do you store my files permanently?',
      answer: 'No. Files are automatically deleted after 30 days for registered users and after 1 hour for trial users. You can also manually delete files at any time.',
      popular: true
    },
    {
      category: 'security',
      question: 'Are you GDPR compliant?',
      answer: 'Yes, we are fully GDPR compliant. We provide data portability, right to deletion, and clear privacy controls. See our Privacy Policy for full details.',
      popular: false
    },
    {
      category: 'security',
      question: 'Can I delete my account and data?',
      answer: 'Yes, you can delete your account and all associated data at any time from your account settings. This action is permanent and cannot be undone.',
      popular: false
    },
  ];

  const filteredFaqs = faqs.filter(faq => {
    const matchesCategory = selectedCategory === 'all' || faq.category === selectedCategory;
    const matchesSearch = searchTerm === '' || 
      faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesCategory && matchesSearch;
  });

  const popularFaqs = faqs.filter(faq => faq.popular);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h3" component="h1" gutterBottom>
          Frequently Asked Questions
        </Typography>
        <Typography variant="h6" color="text.secondary" mb={4}>
          Get instant answers to common questions about PDF Table Extractor
        </Typography>

        {/* Search */}
        <Box maxWidth="md" mx="auto">
          <TextField
            fullWidth
            placeholder="Search for answers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            variant="outlined"
            sx={{ mb: 3 }}
          />
        </Box>
      </Box>

      <Grid container spacing={4}>
        {/* Categories Sidebar */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, position: 'sticky', top: 20 }}>
            <Typography variant="h6" gutterBottom>
              Categories
            </Typography>
            {categories.map((category) => (
              <Chip
                key={category.id}
                icon={category.icon}
                label={`${category.name} (${category.count})`}
                onClick={() => setSelectedCategory(category.id)}
                variant={selectedCategory === category.id ? 'filled' : 'outlined'}
                color={selectedCategory === category.id ? 'primary' : 'default'}
                sx={{ 
                  mb: 1, 
                  mr: 1, 
                  width: '100%',
                  justifyContent: 'flex-start',
                  '& .MuiChip-label': {
                    width: '100%',
                    textAlign: 'left',
                    pl: 1
                  }
                }}
              />
            ))}
          </Paper>

          {/* Popular Questions */}
          {selectedCategory === 'all' && (
            <Paper sx={{ p: 2, mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Popular Questions
              </Typography>
              <List dense>
                {popularFaqs.slice(0, 5).map((faq, index) => (
                  <ListItem key={index} disablePadding>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                    </ListItemIcon>
                    <ListItemText 
                      primary={faq.question}
                      primaryTypographyProps={{ 
                        variant: 'body2',
                        sx: { cursor: 'pointer', '&:hover': { color: 'primary.main' } }
                      }}
                      onClick={() => {
                        setSelectedCategory(faq.category);
                        setSearchTerm(faq.question);
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
        </Grid>

        {/* FAQ Content */}
        <Grid item xs={12} md={9}>
          {filteredFaqs.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No questions found
              </Typography>
              <Typography color="text.secondary" mb={2}>
                Try adjusting your search terms or browse different categories.
              </Typography>
              <Button 
                variant="outlined" 
                onClick={() => {
                  setSearchTerm('');
                  setSelectedCategory('all');
                }}
              >
                Show All Questions
              </Button>
            </Paper>
          ) : (
            <Box>
              {/* Results count */}
              <Typography variant="body2" color="text.secondary" mb={2}>
                Showing {filteredFaqs.length} question{filteredFaqs.length !== 1 ? 's' : ''}
                {selectedCategory !== 'all' && ` in ${categories.find(c => c.id === selectedCategory)?.name}`}
                {searchTerm && ` matching "${searchTerm}"`}
              </Typography>

              {/* FAQ Accordions */}
              {filteredFaqs.map((faq, index) => (
                <Accordion key={index} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box display="flex" alignItems="center" width="100%">
                      <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                        {faq.question}
                      </Typography>
                      {faq.popular && (
                        <Chip 
                          label="Popular" 
                          size="small" 
                          color="success" 
                          sx={{ ml: 2 }}
                        />
                      )}
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography color="text.secondary">
                      {faq.answer}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </Grid>
      </Grid>

      {/* Still need help section */}
      <Box mt={8}>
        <Alert severity="info" sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Still need help?
          </Typography>
          <Typography mb={2}>
            Can't find the answer you're looking for? Our support team is here to help you get the most out of PDF Table Extractor.
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap">
            <Button 
              variant="contained" 
              startIcon={<Email />}
              href="/contact"
            >
              Contact Support
            </Button>
            <Button 
              variant="outlined"
              href="/try-demo"
            >
              Try Demo
            </Button>
            <Button 
              variant="outlined"
              href="mailto:support@pdfextractor.com"
            >
              Email Us
            </Button>
          </Box>
        </Alert>
      </Box>
    </Container>
  );
};

export default FAQ;