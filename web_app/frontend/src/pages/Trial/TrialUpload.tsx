import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  LinearProgress,
  Alert,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText
} from '@mui/material';
import {
  CloudUpload,
  Description,
  CheckCircle,
  Download,
  Email,
  Visibility,
  TableChart,
  Schedule,
  Star,
  CheckBox,
  CheckBoxOutlineBlank
} from '@mui/icons-material';
import toast from 'react-hot-toast';
import api from '../../services/api';
import { extractApiErrorMessage } from '../../utils/errorUtils';

interface TrialFile {
  id: string;
  filename: string;
  status: 'uploaded' | 'processing' | 'completed' | 'error';
  uploadedAt: string;
  result?: any;
}

interface TrialSession {
  sessionId: string;
  filesUploaded: number;
  remainingUploads: number;
  files: TrialFile[];
}

const TrialUpload: React.FC = () => {
  const [session, setSession] = useState<TrialSession | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<TrialFile | null>(null);
  const [showEmailDialog, setShowEmailDialog] = useState(false);
  const [email, setEmail] = useState('');
  const [downloadFormat, setDownloadFormat] = useState('excel');
  const [downloadingFile, setDownloadingFile] = useState<string | null>(null);
  const [selectedTables, setSelectedTables] = useState<number[]>([]);

  // Generate or retrieve session ID
  const getSessionId = () => {
    let sessionId = localStorage.getItem('trial-session-id');
    if (!sessionId) {
      sessionId = Math.random().toString(36).substring(2) + Date.now().toString(36);
      localStorage.setItem('trial-session-id', sessionId);
    }
    return sessionId;
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file
    const supportedExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx'];
    const supportedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    const hasValidExtension = supportedExtensions.some(ext => 
      file.name.toLowerCase().endsWith(ext)
    );
    const hasValidType = supportedTypes.includes(file.type);
    
    if (!hasValidExtension && !hasValidType) {
      toast.error('Only PDF, Word, and Excel files are allowed');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB for trial');
      return;
    }

    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const sessionId = getSessionId();

      const response = await api.post('/trial/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-Session-ID': sessionId
        }
      });

      const result = response.data;
      toast.success(result.message);

      // Update session state
      setSession(prev => ({
        sessionId: result.session_id,
        filesUploaded: prev ? prev.filesUploaded + 1 : 1,
        remainingUploads: result.remaining_uploads,
        files: [
          ...(prev?.files || []),
          {
            id: result.file_id,
            filename: result.filename,
            status: 'uploaded',
            uploadedAt: new Date().toISOString()
          }
        ]
      }));

      // Auto-process the file
      await processFile(result.file_id);

    } catch (error: any) {
      console.error('Upload error:', error);
      toast.error(extractApiErrorMessage(error) || 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [session]);

  const processFile = async (fileId: string) => {
    setProcessing(fileId);
    
    try {
      const sessionId = getSessionId();
      
      const response = await api.post(`/trial/${fileId}/process`, {}, {
        headers: {
          'X-Session-ID': sessionId
        }
      });

      const result = response.data;

      // Update file status
      setSession(prev => ({
        ...prev!,
        files: prev!.files.map(file => 
          file.id === fileId 
            ? { ...file, status: 'completed', result }
            : file
        )
      }));

      toast.success(`Found ${result.total_tables_found} tables! ${result.trial_message || ''}`);

    } catch (error: any) {
      console.error('Processing error:', error);
      toast.error(extractApiErrorMessage(error) || 'Processing failed');
      
      // Update file status to error
      setSession(prev => ({
        ...prev!,
        files: prev!.files.map(file => 
          file.id === fileId 
            ? { ...file, status: 'error' }
            : file
        )
      }));
    } finally {
      setProcessing(null);
    }
  };

  const handlePreview = (file: TrialFile) => {
    setSelectedFile(file);
    // Initialize all tables as selected by default
    if (file.result?.tables) {
      const tableIndices = file.result.tables.map((_: any, index: number) => index);
      setSelectedTables(tableIndices);
    }
  };

  const handleDownload = (file: TrialFile) => {
    if (!session) return;
    
    setDownloadingFile(file.id);
    // Ensure we have selected tables
    if (selectedTables.length === 0 && file.result?.tables) {
      const tableIndices = file.result.tables.map((_: any, index: number) => index);
      setSelectedTables(tableIndices);
    }
    setShowEmailDialog(true);
  };

  const requestDownload = async () => {
    if (!email || !downloadingFile || !session) return;

    try {
      const sessionId = getSessionId();
      
      const response = await api.post(`/trial/${downloadingFile}/request-download`, 
        { email, format: downloadFormat, selected_tables: selectedTables },
        {
          headers: {
            'X-Session-ID': sessionId
          }
        }
      );

      const result = response.data;
      
      // Create download link
      const downloadUrl = `/api/trial/download/${result.download_token}`;
      const link = document.createElement('a');
      link.href = `http://localhost:9700${downloadUrl}`;
      
      // Set filename based on format
      const extensions: Record<string, string> = {
        'excel': '.xlsx',
        'csv': '.csv',
        'word': '.docx'
      };
      link.download = `trial_tables${extensions[downloadFormat] || '.xlsx'}`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast.success('Download started! Check your downloads folder.');
      setShowEmailDialog(false);
      setEmail('');
      setDownloadFormat('excel');
      setSelectedTables([]);

    } catch (error: any) {
      console.error('Download error:', error);
      toast.error(extractApiErrorMessage(error) || 'Download failed');
    } finally {
      setDownloadingFile(null);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxFiles: 1,
    disabled: uploading || (session ? session.remainingUploads <= 0 : false)
  });

  const canUploadMore = !session || session.remainingUploads > 0;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box textAlign="center" mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Try Document Table Extractor Free
        </Typography>
        <Typography variant="h6" color="text.secondary" mb={2}>
          Extract tables from your documents (PDF, Word, Excel) instantly - no registration required!
        </Typography>
        <Box display="flex" justifyContent="center" gap={2} mb={3}>
          <Chip icon={<TableChart />} label="AI-Powered Extraction" color="primary" />
          <Chip icon={<Schedule />} label="Instant Results" color="secondary" />
          <Chip icon={<Star />} label="No Registration" color="success" />
        </Box>
      </Box>

      <Grid container spacing={4}>
        {/* Upload Area */}
        <Grid item xs={12} md={6}>
          <Paper 
            {...getRootProps()} 
            sx={{ 
              p: 4, 
              textAlign: 'center', 
              cursor: canUploadMore ? 'pointer' : 'not-allowed',
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.300',
              bgcolor: isDragActive ? 'action.hover' : 'background.paper',
              opacity: canUploadMore ? 1 : 0.5
            }}
          >
            <input {...getInputProps()} />
            <CloudUpload sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            
            {uploading ? (
              <>
                <Typography variant="h6" gutterBottom>
                  Uploading...
                </Typography>
                <LinearProgress sx={{ mt: 2 }} />
              </>
            ) : canUploadMore ? (
              <>
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Drop your document here' : 'Drag & drop a document here'}
                </Typography>
                <Typography color="text.secondary" mb={2}>
                  or click to browse (PDF, Word, Excel)
                </Typography>
                <Button variant="contained" size="large">
                  Choose Document
                </Button>
              </>
            ) : (
              <>
                <Typography variant="h6" gutterBottom color="error">
                  Trial Limit Reached
                </Typography>
                <Typography color="text.secondary" mb={2}>
                  You've used all 3 trial uploads. Register for unlimited access!
                </Typography>
                <Button variant="contained" color="primary" size="large" href="/register">
                  Sign Up Now
                </Button>
              </>
            )}
          </Paper>

          {/* Trial Limitations */}
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Trial Limitations:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText primary="• Maximum 3 files per session" />
              </ListItem>
              <ListItem>
                <ListItemText primary="• First 2 tables only" />
              </ListItem>
              <ListItem>
                <ListItemText primary="• First 10 rows per table" />
              </ListItem>
              <ListItem>
                <ListItemText primary="• Email required for download" />
              </ListItem>
              <ListItem>
                <ListItemText primary="• Download in Excel, CSV, or Word format" />
              </ListItem>
            </List>
          </Alert>
        </Grid>

        {/* Results Area */}
        <Grid item xs={12} md={6}>
          {session && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Your Trial Session
              </Typography>
              <Typography color="text.secondary" mb={2}>
                Files uploaded: {session.filesUploaded}/3 • Remaining: {session.remainingUploads}
              </Typography>

              {session.files.length > 0 && (
                <List>
                  {session.files.map((file) => (
                    <ListItem key={file.id} divider>
                      <ListItemIcon>
                        <Description />
                      </ListItemIcon>
                      <ListItemText
                        primary={file.filename}
                        secondary={
                          <Box>
                            <Chip 
                              size="small" 
                              label={file.status} 
                              color={
                                file.status === 'completed' ? 'success' :
                                file.status === 'processing' ? 'warning' :
                                file.status === 'error' ? 'error' : 'default'
                              }
                            />
                            {file.status === 'processing' && processing === file.id && (
                              <LinearProgress sx={{ mt: 1 }} />
                            )}
                            {file.result && (
                              <Typography variant="caption" display="block">
                                {file.result.total_tables_found} tables found
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                      <Box>
                        {file.status === 'completed' && (
                          <>
                            <Button
                              size="small"
                              startIcon={<Visibility />}
                              onClick={() => handlePreview(file)}
                              sx={{ mr: 1 }}
                            >
                              Preview
                            </Button>
                            <Button
                              size="small"
                              startIcon={<Download />}
                              onClick={() => handleDownload(file)}
                              variant="contained"
                            >
                              Download
                            </Button>
                          </>
                        )}
                      </Box>
                    </ListItem>
                  ))}
                </List>
              )}
            </Paper>
          )}
        </Grid>
      </Grid>

      {/* Preview Dialog */}
      <Dialog 
        open={Boolean(selectedFile)} 
        onClose={() => setSelectedFile(null)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Preview: {selectedFile?.filename}
        </DialogTitle>
        <DialogContent>
          {selectedFile?.result?.tables?.map((table: any, index: number) => (
            <Card key={index} sx={{ mb: 2, border: selectedTables.includes(index) ? '2px solid' : '1px solid #ddd', borderColor: selectedTables.includes(index) ? 'primary.main' : '#ddd' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="h6" gutterBottom>
                    Table {index + 1}
                  </Typography>
                  <Button
                    startIcon={selectedTables.includes(index) ? <CheckBox /> : <CheckBoxOutlineBlank />}
                    onClick={() => {
                      setSelectedTables(prev => 
                        prev.includes(index) 
                          ? prev.filter(i => i !== index)
                          : [...prev, index]
                      );
                    }}
                    variant={selectedTables.includes(index) ? 'contained' : 'outlined'}
                    size="small"
                  >
                    {selectedTables.includes(index) ? 'Selected' : 'Select'}
                  </Button>
                </Box>
                {table.trial_message && (
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    {table.trial_message}
                  </Alert>
                )}
                <Box sx={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <tbody>
                      {table.data.slice(0, 10).map((row: string[], rowIndex: number) => (
                        <tr key={rowIndex}>
                          {row.map((cell: string, cellIndex: number) => (
                            <td 
                              key={cellIndex}
                              style={{ 
                                border: '1px solid #ddd', 
                                padding: '8px',
                                backgroundColor: rowIndex === 0 ? '#f5f5f5' : 'white'
                              }}
                            >
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Box>
              </CardContent>
            </Card>
          ))}
        </DialogContent>
        <DialogActions>
          <Box display="flex" alignItems="center" width="100%" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">
              {selectedTables.length} of {selectedFile?.result?.tables?.length || 0} tables selected
            </Typography>
            <Box>
              <Button 
                onClick={() => {
                  if (selectedFile?.result?.tables) {
                    const allIndices = selectedFile.result.tables.map((_: any, index: number) => index);
                    setSelectedTables(selectedTables.length === allIndices.length ? [] : allIndices);
                  }
                }}
                sx={{ mr: 1 }}
              >
                {selectedTables.length === selectedFile?.result?.tables?.length ? 'Deselect All' : 'Select All'}
              </Button>
              <Button onClick={() => setSelectedFile(null)}>Close</Button>
            </Box>
          </Box>
        </DialogActions>
      </Dialog>

      {/* Email Dialog */}
      <Dialog open={showEmailDialog} onClose={() => setShowEmailDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Email sx={{ mr: 1 }} />
          Choose Download Format
        </DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Please provide your email address and choose your preferred download format.
          </Typography>
          
          {selectedTables.length > 0 && (
            <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
              <Typography variant="body2">
                You have selected {selectedTables.length} table{selectedTables.length !== 1 ? 's' : ''} for download.
                {selectedTables.length < (selectedFile?.result?.tables?.length || 0) && 
                  ` To select different tables, close this dialog and use the preview.`
                }
              </Typography>
            </Alert>
          )}
          
          <TextField
            autoFocus
            margin="dense"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            sx={{ mt: 2, mb: 2 }}
          />

          <FormControl fullWidth variant="outlined">
            <InputLabel>Download Format</InputLabel>
            <Select
              value={downloadFormat}
              onChange={(e) => setDownloadFormat(e.target.value)}
              label="Download Format"
            >
              <MenuItem value="excel">
                <Box display="flex" alignItems="center">
                  <TableChart sx={{ mr: 1, color: 'green' }} />
                  Excel (.xlsx) - Tables in separate sheets
                </Box>
              </MenuItem>
              <MenuItem value="csv">
                <Box display="flex" alignItems="center">
                  <Description sx={{ mr: 1, color: 'blue' }} />
                  CSV (.csv) - All tables combined
                </Box>
              </MenuItem>
              <MenuItem value="word">
                <Box display="flex" alignItems="center">
                  <Description sx={{ mr: 1, color: 'purple' }} />
                  Word (.docx) - Formatted document with tables
                </Box>
              </MenuItem>
            </Select>
            <FormHelperText>
              {downloadFormat === 'excel' && 'Each table will be in a separate Excel sheet'}
              {downloadFormat === 'csv' && 'All tables will be combined into one CSV file'}
              {downloadFormat === 'word' && 'Tables will be formatted in a Word document'}
            </FormHelperText>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEmailDialog(false)}>Cancel</Button>
          <Button 
            onClick={requestDownload} 
            variant="contained"
            disabled={!email || !email.includes('@') || selectedTables.length === 0}
          >
            Download {selectedTables.length} Table{selectedTables.length !== 1 ? 's' : ''} ({downloadFormat.toUpperCase()})
          </Button>
        </DialogActions>
      </Dialog>

      {/* Call to Action */}
      <Box textAlign="center" mt={6}>
        <Paper sx={{ p: 4, bgcolor: 'primary.main', color: 'white' }}>
          <Typography variant="h5" gutterBottom>
            Ready for More?
          </Typography>
          <Typography variant="body1" mb={3}>
            Register now to process unlimited files, access all tables, and export in multiple formats!
          </Typography>
          <Button 
            variant="contained" 
            size="large" 
            sx={{ bgcolor: 'white', color: 'primary.main', mr: 2 }}
            href="/register"
          >
            Start Free Trial
          </Button>
          <Button 
            variant="outlined" 
            size="large" 
            sx={{ borderColor: 'white', color: 'white' }}
            href="/pricing"
          >
            View Pricing
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default TrialUpload;