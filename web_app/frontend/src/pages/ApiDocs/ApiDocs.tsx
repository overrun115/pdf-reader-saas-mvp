import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Grid,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Button,
  IconButton,
  Container,
} from '@mui/material';
import { ContentCopy, OpenInNew } from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { motion } from 'framer-motion';
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
      id={`api-tabpanel-${index}`}
      aria-labelledby={`api-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const ApiDocs: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const endpoints = [
    {
      method: 'POST',
      path: '/api/files/upload',
      description: 'Upload a PDF file for processing',
      parameters: [
        { name: 'file', type: 'File', required: true, description: 'PDF file to upload (max 50MB)' },
      ],
      response: {
        id: 123,
        original_filename: 'document.pdf',
        file_size: 1024576,
        status: 'uploaded',
        created_at: '2024-01-15T10:30:00Z',
      },
    },
    {
      method: 'GET',
      path: '/api/files/{file_id}/preview',
      description: 'Get a preview of tables in the uploaded PDF',
      parameters: [
        { name: 'file_id', type: 'integer', required: true, description: 'ID of the uploaded file' },
      ],
      response: {
        tables_found: 2,
        tables: [
          {
            table_number: 1,
            rows: 10,
            columns: ['Name', 'Age', 'City'],
            sample_data: [
              { Name: 'John', Age: 30, City: 'New York' },
              { Name: 'Jane', Age: 25, City: 'Los Angeles' },
            ],
          },
        ],
        processing_suggestions: {
          recommended_format: 'excel',
          complexity_score: 'medium',
          estimated_time: '2-5 minutes',
          tips: ['Intelligent column mapping will be applied'],
        },
      },
    },
    {
      method: 'POST',
      path: '/api/files/{file_id}/process',
      description: 'Start processing a PDF file to extract tables',
      parameters: [
        { name: 'file_id', type: 'integer', required: true, description: 'ID of the uploaded file' },
        { name: 'output_format', type: 'string', required: false, description: 'excel, csv, or both (default: excel)' },
      ],
      response: {
        message: 'File processing started',
        file_id: 123,
        status: 'processing',
        estimated_time: '2-5 minutes',
      },
    },
    {
      method: 'GET',
      path: '/api/files/{file_id}/status',
      description: 'Get processing status of a file',
      parameters: [
        { name: 'file_id', type: 'integer', required: true, description: 'ID of the file' },
      ],
      response: {
        id: 123,
        status: 'completed',
        tables_found: 3,
        total_rows: 150,
        processing_time: 45.2,
        download_url: '/api/files/123/download',
      },
    },
    {
      method: 'GET',
      path: '/api/files/{file_id}/download',
      description: 'Download the processed file',
      parameters: [
        { name: 'file_id', type: 'integer', required: true, description: 'ID of the processed file' },
      ],
      response: 'Binary file download (Excel/CSV/ZIP)',
    },
  ];

  const codeExamples = {
    curl: `# Upload a PDF file
curl -X POST "https://api.pdfextractor.com/api/files/upload" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -F "file=@document.pdf"

# Preview tables
curl -X GET "https://api.pdfextractor.com/api/files/123/preview" \\
  -H "Authorization: Bearer YOUR_API_KEY"

# Process the file
curl -X POST "https://api.pdfextractor.com/api/files/123/process" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"output_format": "excel"}'

# Check status
curl -X GET "https://api.pdfextractor.com/api/files/123/status" \\
  -H "Authorization: Bearer YOUR_API_KEY"

# Download result
curl -X GET "https://api.pdfextractor.com/api/files/123/download" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -o "extracted_tables.xlsx"`,

    python: `import requests
import time

API_KEY = "your_api_key_here"
BASE_URL = "https://api.pdfextractor.com/api"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Upload PDF
with open("document.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/files/upload",
        headers=headers,
        files={"file": f}
    )
    file_data = response.json()
    file_id = file_data["id"]

# Preview tables
preview = requests.get(
    f"{BASE_URL}/files/{file_id}/preview",
    headers=headers
).json()

print(f"Found {preview['tables_found']} tables")

# Process file
process_response = requests.post(
    f"{BASE_URL}/files/{file_id}/process",
    headers=headers,
    json={"output_format": "excel"}
)

# Poll for completion
while True:
    status = requests.get(
        f"{BASE_URL}/files/{file_id}/status",
        headers=headers
    ).json()
    
    if status["status"] == "completed":
        download_url = status["download_url"]
        break
    elif status["status"] == "failed":
        print("Processing failed")
        break
    
    time.sleep(5)

# Download result
result = requests.get(f"{BASE_URL}{download_url}", headers=headers)
with open("extracted_tables.xlsx", "wb") as f:
    f.write(result.content)`,

    javascript: `const API_KEY = 'your_api_key_here';
const BASE_URL = 'https://api.pdfextractor.com/api';

const headers = {
    'Authorization': \`Bearer \${API_KEY}\`
};

// Upload PDF
async function uploadPDF(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(\`\${BASE_URL}/files/upload\`, {
        method: 'POST',
        headers: headers,
        body: formData
    });
    
    return response.json();
}

// Preview tables
async function previewTables(fileId) {
    const response = await fetch(\`\${BASE_URL}/files/\${fileId}/preview\`, {
        headers: headers
    });
    
    return response.json();
}

// Process file
async function processFile(fileId, outputFormat = 'excel') {
    const response = await fetch(\`\${BASE_URL}/files/\${fileId}/process\`, {
        method: 'POST',
        headers: {
            ...headers,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ output_format: outputFormat })
    });
    
    return response.json();
}

// Poll for completion
async function waitForCompletion(fileId) {
    while (true) {
        const status = await fetch(\`\${BASE_URL}/files/\${fileId}/status\`, {
            headers: headers
        }).then(r => r.json());
        
        if (status.status === 'completed') {
            return status.download_url;
        } else if (status.status === 'failed') {
            throw new Error('Processing failed');
        }
        
        await new Promise(resolve => setTimeout(resolve, 5000));
    }
}

// Complete workflow
async function extractTables(file) {
    const uploadResult = await uploadPDF(file);
    const preview = await previewTables(uploadResult.id);
    
    console.log(\`Found \${preview.tables_found} tables\`);
    
    await processFile(uploadResult.id);
    const downloadUrl = await waitForCompletion(uploadResult.id);
    
    // Download the file
    window.open(\`\${BASE_URL}\${downloadUrl}\`);
}`,
  };

  const webhookExample = `{
  "event": "processing.completed",
  "file_id": 123,
  "user_id": 456,
  "status": "completed",
  "tables_found": 3,
  "total_rows": 150,
  "processing_time": 45.2,
  "download_url": "https://api.pdfextractor.com/api/files/123/download",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:31:15Z"
}`;

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        API Documentation
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Integrate PDF table extraction into your applications with our REST API
      </Typography>

      <Alert severity="info" sx={{ mt: 3, mb: 3 }}>
        <Typography variant="body2">
          <strong>API Access:</strong> Available on Pro and Enterprise plans. 
          <Button variant="text" size="small" sx={{ ml: 1 }}>
            View Pricing
          </Button>
        </Typography>
      </Alert>

      <Card sx={{ mt: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Overview" />
            <Tab label="Endpoints" />
            <Tab label="Code Examples" />
            <Tab label="Webhooks" />
          </Tabs>
        </Box>

        {/* Overview Tab */}
        <TabPanel value={tabValue} index={0}>
          <CardContent>
            <Grid container spacing={4}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Getting Started
                </Typography>
                <Typography variant="body2" paragraph>
                  Our REST API allows you to integrate PDF table extraction into your applications.
                  All requests require authentication using API keys.
                </Typography>
                
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                  Base URL
                </Typography>
                <Paper sx={{ p: 2, bgcolor: 'action.hover', mb: 2 }}>
                  <Typography variant="body2" fontFamily="monospace">
                    https://api.pdfextractor.com/api
                  </Typography>
                </Paper>

                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                  Authentication
                </Typography>
                <Typography variant="body2" paragraph>
                  Include your API key in the Authorization header:
                </Typography>
                <Paper sx={{ p: 2, bgcolor: 'action.hover' }}>
                  <Typography variant="body2" fontFamily="monospace">
                    Authorization: Bearer YOUR_API_KEY
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Rate Limits
                </Typography>
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Plan</TableCell>
                        <TableCell>Requests/Month</TableCell>
                        <TableCell>Rate Limit</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>Pro</TableCell>
                        <TableCell>10,000</TableCell>
                        <TableCell>100/hour</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Enterprise</TableCell>
                        <TableCell>Unlimited</TableCell>
                        <TableCell>1,000/hour</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>

                <Typography variant="h6" fontWeight={600} gutterBottom sx={{ mt: 3 }}>
                  Response Format
                </Typography>
                <Typography variant="body2" paragraph>
                  All responses are in JSON format. Successful responses include the requested data,
                  while errors return details about what went wrong.
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </TabPanel>

        {/* Endpoints Tab */}
        <TabPanel value={tabValue} index={1}>
          <CardContent>
            {endpoints.map((endpoint, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Paper sx={{ p: 3, mb: 3, border: 1, borderColor: 'grey.200' }}>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Chip
                      label={endpoint.method}
                      color={endpoint.method === 'GET' ? 'success' : 'primary'}
                      size="small"
                    />
                    <Typography variant="h6" fontFamily="monospace">
                      {endpoint.path}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" paragraph>
                    {endpoint.description}
                  </Typography>

                  {endpoint.parameters.length > 0 && (
                    <>
                      <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                        Parameters
                      </Typography>
                      <TableContainer sx={{ mb: 2 }}>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Name</TableCell>
                              <TableCell>Type</TableCell>
                              <TableCell>Required</TableCell>
                              <TableCell>Description</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {endpoint.parameters.map((param, idx) => (
                              <TableRow key={idx}>
                                <TableCell sx={{ fontFamily: 'monospace' }}>{param.name}</TableCell>
                                <TableCell>{param.type}</TableCell>
                                <TableCell>{param.required ? 'Yes' : 'No'}</TableCell>
                                <TableCell>{param.description}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </>
                  )}

                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                    Response
                  </Typography>
                  <Box position="relative">
                    <SyntaxHighlighter
                      language="json"
                      style={tomorrow}
                      customStyle={{ borderRadius: 8, fontSize: '0.875rem' }}
                    >
                      {typeof endpoint.response === 'string' 
                        ? endpoint.response 
                        : JSON.stringify(endpoint.response, null, 2)
                      }
                    </SyntaxHighlighter>
                    <IconButton
                      size="small"
                      sx={{ position: 'absolute', top: 8, right: 8 }}
                      onClick={() => copyToClipboard(
                        typeof endpoint.response === 'string' 
                          ? endpoint.response 
                          : JSON.stringify(endpoint.response, null, 2)
                      )}
                    >
                      <ContentCopy fontSize="small" />
                    </IconButton>
                  </Box>
                </Paper>
              </motion.div>
            ))}
          </CardContent>
        </TabPanel>

        {/* Code Examples Tab */}
        <TabPanel value={tabValue} index={2}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Complete Integration Examples
            </Typography>
            <Typography variant="body2" paragraph>
              Here are complete examples showing how to integrate our API in different languages.
            </Typography>

            <Tabs value={0} sx={{ mb: 3 }}>
              <Tab label="cURL" />
              <Tab label="Python" />
              <Tab label="JavaScript" />
            </Tabs>

            {Object.entries(codeExamples).map(([language, code], index) => (
              <Box key={language} sx={{ mb: 4 }}>
                <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                  <Typography variant="subtitle1" fontWeight={600} textTransform="capitalize">
                    {language}
                  </Typography>
                  <IconButton onClick={() => copyToClipboard(code)}>
                    <ContentCopy />
                  </IconButton>
                </Box>
                <SyntaxHighlighter
                  language={language === 'curl' ? 'bash' : language}
                  style={tomorrow}
                  customStyle={{ borderRadius: 8 }}
                >
                  {code}
                </SyntaxHighlighter>
              </Box>
            ))}
          </CardContent>
        </TabPanel>

        {/* Webhooks Tab */}
        <TabPanel value={tabValue} index={3}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Webhook Integration
            </Typography>
            <Typography variant="body2" paragraph>
              Receive real-time notifications when file processing is complete. Configure webhook URLs in your account settings.
            </Typography>

            <Alert severity="info" sx={{ mb: 3 }}>
              Webhooks are sent as POST requests with a JSON payload to your configured URL.
            </Alert>

            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Webhook Events
            </Typography>
            <TableContainer component={Paper} sx={{ mb: 3 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Event</TableCell>
                    <TableCell>Description</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>processing.started</TableCell>
                    <TableCell>File processing has begun</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>processing.completed</TableCell>
                    <TableCell>File processing completed successfully</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>processing.failed</TableCell>
                    <TableCell>File processing failed</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>

            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Example Payload
            </Typography>
            <Box position="relative">
              <SyntaxHighlighter
                language="json"
                style={tomorrow}
                customStyle={{ borderRadius: 8 }}
              >
                {webhookExample}
              </SyntaxHighlighter>
              <IconButton
                size="small"
                sx={{ position: 'absolute', top: 8, right: 8 }}
                onClick={() => copyToClipboard(webhookExample)}
              >
                <ContentCopy fontSize="small" />
              </IconButton>
            </Box>
          </CardContent>
        </TabPanel>
      </Card>

      {/* Footer Links */}
      <Box mt={4} textAlign="center">
        <Button
          variant="outlined"
          startIcon={<OpenInNew />}
          href="https://api.pdfextractor.com/docs"
          target="_blank"
          sx={{ mr: 2 }}
        >
          Interactive API Explorer
        </Button>
        <Button
          variant="contained"
          onClick={() => window.open('/profile', '_blank')}
        >
          Generate API Key
        </Button>
      </Box>
    </Container>
  );
};

export default ApiDocs;