import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
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
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Divider,
  IconButton,
  AppBar,
  Toolbar
} from '@mui/material';
import {
  CloudUpload,
  Description,
  TableChart,
  TextSnippet,
  Download,
  ExpandMore,
  Visibility,
  CheckBox,
  CheckBoxOutlineBlank,
  FilePresent,
  Analytics
} from '@mui/icons-material';
import toast from 'react-hot-toast';
import api from '../../services/api';
import { extractApiErrorMessage } from '../../utils/errorUtils';

interface TableData {
  table_id: number;
  page: number;
  confidence: number;
  columns: string[];
  sample_data: string[][];
  total_rows: number;
  table_type: string;
  suggested_name: string;
}

interface TextBlock {
  block_id: number;
  text: string;
  type: string;
  word_count: number;
  preview: string;
}

interface PDFAnalysis {
  file_id: string;
  filename: string;
  total_pages: number;
  total_tables_found: number;
  tables: TableData[];
  text_blocks: TextBlock[];
  processing_time: number;
}

interface QueueStatus {
  queue_length: number;
  running_tasks: number;
  max_concurrent: number;
  max_queue_size: number;
  your_tasks: string[];
}

interface TaskStatus {
  task_id: string;
  status: string;
  filename: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress_message: string;
  error?: string;
  result?: PDFAnalysis;
}

const PDFViewer: React.FC = () => {
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<PDFAnalysis | null>(null);
  const [uploading, setUploading] = useState(false);
  const [selectedTables, setSelectedTables] = useState<number[]>([]);
  const [selectedTextBlocks, setSelectedTextBlocks] = useState<number[]>([]);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [exportFormat, setExportFormat] = useState('excel');
  const [includeHeaders, setIncludeHeaders] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Only PDF files are allowed');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      toast.error('File size must be less than 50MB');
      return;
    }

    setUploading(true);
    setAnalysis(null);
    setTaskId(null);
    setTaskStatus(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      // Upload to queue-based system
      const response = await api.post('/pdf-viewer/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });

      const result = response.data;
      setTaskId(result.task_id);
      
      toast.success(`PDF uploaded! Position in queue: ${result.queue_position}`);
      
      // Start polling for task status
      startPolling(result.task_id);

    } catch (error: any) {
      console.error('Upload error:', error);
      toast.error(extractApiErrorMessage(error) || 'Upload failed');
      setUploading(false);
    }
  }, []);

  const startPolling = useCallback((taskId: string) => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }
    
    const interval = setInterval(async () => {
      try {
        // Check task status
        const taskResponse = await api.get(`/pdf-viewer/task/${taskId}`);
        const task = taskResponse.data;
        setTaskStatus(task);
        
        // Check queue status
        const queueResponse = await api.get('/pdf-viewer/queue/status');
        setQueueStatus(queueResponse.data);
        
        if (task.status === 'completed' && task.result) {
          // Task completed successfully
          setAnalysis(task.result);
          setSelectedTables(task.result.tables && Array.isArray(task.result.tables) ? task.result.tables.map((_: any, index: number) => index) : []);
          setSelectedTextBlocks([]);
          setUploading(false);
          clearInterval(interval);
          setPollingInterval(null);
          toast.success(`Analysis complete! Found ${task.result.total_tables_found} tables and ${task.result.text_blocks.length} text blocks.`);
        } else if (task.status === 'failed' || task.status === 'timeout') {
          // Task failed
          setUploading(false);
          clearInterval(interval);
          setPollingInterval(null);
          toast.error(task.error || 'Analysis failed');
        }
      } catch (error: any) {
        console.error('Polling error:', error);
        // Continue polling unless it's a 404 (task not found)
        if (error.response?.status === 404) {
          clearInterval(interval);
          setPollingInterval(null);
          setUploading(false);
          toast.error('Task not found');
        }
      }
    }, 2000); // Poll every 2 seconds
    
    setPollingInterval(interval);
  }, [pollingInterval]);

  // Cleanup polling on unmount
  React.useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  const handleTableSelection = (tableId: number) => {
    setSelectedTables(prev => 
      prev.includes(tableId) 
        ? prev.filter(id => id !== tableId)
        : [...prev, tableId]
    );
  };

  const handleTextBlockSelection = (blockId: number) => {
    setSelectedTextBlocks(prev => 
      prev.includes(blockId) 
        ? prev.filter(id => id !== blockId)
        : [...prev, blockId]
    );
  };

  const handleExport = async () => {
    if (!analysis || (selectedTables.length === 0 && selectedTextBlocks.length === 0)) {
      toast.error('Please select at least one table or text block to export');
      return;
    }

    setExporting(true);
    
    try {
      const response = await api.post('/pdf-viewer/extract', {
        file_id: analysis.file_id,
        selected_tables: selectedTables,
        selected_text_blocks: selectedTextBlocks,
        include_headers: includeHeaders,
        output_format: exportFormat
      });

      const result = response.data;
      
      // Download the file
      const downloadUrl = `http://localhost:9700${result.download_url}`;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = result.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast.success('Export completed! Check your downloads folder.');
      setShowExportDialog(false);

    } catch (error: any) {
      console.error('Export error:', error);
      toast.error(extractApiErrorMessage(error) || 'Export failed');
    } finally {
      setExporting(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    disabled: uploading
  });

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'financial': return 'success';
      case 'temporal': return 'info';
      case 'inventory': return 'warning';
      default: return 'default';
    }
  };

  const getTextTypeColor = (type: string) => {
    switch (type) {
      case 'heading': return 'primary';
      case 'summary': return 'success';
      case 'short_text': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ bgcolor: '#FFFFFF', minHeight: '100vh' }}>
      {/* Header with DueHub Logo */}
      <AppBar 
        position="static" 
        elevation={0}
        sx={{ 
          bgcolor: '#FFFFFF',
          borderBottom: '1px solid rgba(0, 0, 0, 0.06)',
          color: '#1a202c'
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center',
              cursor: 'pointer',
              '&:hover': {
                opacity: 0.8
              }
            }}
            onClick={() => navigate('/')}
          >
            <Box
              component="img"
              src="/logo-duehub.svg"
              alt="DueHub"
              sx={{
                height: 40,
                width: 'auto',
                mr: 2,
                color: '#0066FF'
              }}
            />
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 700,
                color: '#0066FF',
                fontFamily: 'Montserrat, sans-serif',
              }}
            >
              PDF Extractor
            </Typography>
          </Box>
          <Button
            variant="outlined"
            size="small"
            onClick={() => navigate('/')}
            sx={{
              color: '#6B7280',
              borderColor: '#E5E7EB',
              '&:hover': {
                borderColor: '#0066FF',
                color: '#0066FF',
              }
            }}
          >
            Back to Home
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 6 }}>
        {/* Page Header */}
        <Box textAlign="center" mb={6}>
          <Typography 
            variant="h3" 
            component="h1" 
            sx={{
              fontWeight: 700,
              color: '#1a202c',
              mb: 2,
              fontFamily: 'Montserrat, sans-serif',
            }}
          >
            Advanced PDF Analyzer
          </Typography>
          <Typography 
            variant="h6" 
            sx={{
              color: '#6B7280',
              mb: 4,
              maxWidth: 600,
              mx: 'auto',
              lineHeight: 1.6,
            }}
          >
            Upload a PDF to analyze its structure, preview tables and text, then extract exactly what you need
          </Typography>
          <Box display="flex" justifyContent="center" gap={2} mb={4}>
            <Chip 
              icon={<Analytics />} 
              label="AI-Powered Analysis" 
              sx={{
                bgcolor: 'rgba(0, 102, 255, 0.1)',
                color: '#0066FF',
                fontWeight: 600,
              }}
            />
            <Chip 
              icon={<Visibility />} 
              label="Visual Preview" 
              sx={{
                bgcolor: 'rgba(16, 185, 129, 0.1)',
                color: '#10B981',
                fontWeight: 600,
              }}
            />
            <Chip 
              icon={<TableChart />} 
              label="Smart Table Detection" 
              sx={{
                bgcolor: 'rgba(245, 158, 11, 0.1)',
                color: '#F59E0B',
                fontWeight: 600,
              }}
            />
          </Box>
        </Box>

      {!analysis ? (
        /* Upload Area */
        <Box sx={{ maxWidth: 600, mx: 'auto' }}>
          <Paper 
            {...getRootProps()} 
            elevation={0}
            sx={{ 
              p: 8, 
              textAlign: 'center', 
              cursor: uploading ? 'not-allowed' : 'pointer',
              border: '2px dashed',
              borderColor: isDragActive ? '#0066FF' : '#E5E7EB',
              bgcolor: isDragActive ? 'rgba(0, 102, 255, 0.02)' : '#FFFFFF',
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                borderColor: uploading ? '#E5E7EB' : '#0066FF',
                bgcolor: uploading ? '#FFFFFF' : 'rgba(0, 102, 255, 0.02)',
              },
              opacity: uploading ? 0.7 : 1
            }}
          >
            <input {...getInputProps()} />
            
            {uploading ? (
              <>
                <Box sx={{ mb: 3 }}>
                  <CloudUpload sx={{ fontSize: 64, color: '#0066FF', mb: 2 }} />
                </Box>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    fontWeight: 600,
                    color: '#1a202c',
                    mb: 2,
                    fontFamily: 'Montserrat, sans-serif',
                  }}
                >
                  {taskStatus?.status === 'pending' ? 'PDF Queued for Processing...' : 
                   taskStatus?.status === 'running' ? 'Analyzing PDF Structure...' : 
                   'Processing PDF...'}
                </Typography>
                <Typography sx={{ color: '#6B7280', mb: 3, fontSize: '1.1rem' }}>
                  {taskStatus?.progress_message || 'This may take a few moments while we detect tables and text blocks'}
                </Typography>
                {queueStatus && (
                  <Box 
                    sx={{ 
                      bgcolor: 'rgba(0, 102, 255, 0.05)',
                      border: '1px solid rgba(0, 102, 255, 0.2)',
                      borderRadius: 2,
                      p: 2,
                      mb: 3,
                      maxWidth: 400,
                      mx: 'auto'
                    }}
                  >
                    <Typography variant="body2" sx={{ color: '#374151', fontWeight: 500 }}>
                      Queue Status: {queueStatus.running_tasks}/{queueStatus.max_concurrent} running, 
                      {queueStatus.queue_length} waiting
                    </Typography>
                  </Box>
                )}
                <LinearProgress 
                  sx={{ 
                    mt: 2, 
                    maxWidth: 400, 
                    mx: 'auto',
                    height: 8,
                    borderRadius: 4,
                    bgcolor: 'rgba(0, 102, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: '#0066FF',
                    }
                  }} 
                />
                {taskStatus && (
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      mt: 3, 
                      display: 'block',
                      color: '#9CA3AF',
                      fontSize: '0.75rem'
                    }}
                  >
                    Task ID: {taskStatus.task_id} • Status: {taskStatus.status}
                    {taskStatus.created_at && (
                      <> • Started: {new Date(taskStatus.created_at).toLocaleTimeString()}</>
                    )}
                  </Typography>
                )}
              </>
            ) : (
              <>
                <Box sx={{ mb: 3 }}>
                  <CloudUpload sx={{ fontSize: 64, color: '#0066FF', mb: 2 }} />
                </Box>
                <Typography 
                  variant="h5" 
                  sx={{
                    fontWeight: 600,
                    color: '#1a202c',
                    mb: 2,
                    fontFamily: 'Montserrat, sans-serif',
                  }}
                >
                  {isDragActive ? 'Drop your PDF here' : 'Drag & drop your PDF file'}
                </Typography>
                <Typography sx={{ color: '#6B7280', mb: 4, fontSize: '1.1rem' }}>
                  or click to browse and select a file
                </Typography>
                <Button 
                  variant="contained" 
                  size="large"
                  sx={{
                    bgcolor: '#0066FF',
                    py: 1.5,
                    px: 4,
                    fontSize: '1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    borderRadius: 2,
                    boxShadow: 'none',
                    '&:hover': {
                      bgcolor: '#0052CC',
                      boxShadow: 'none',
                    }
                  }}
                >
                  Choose PDF File
                </Button>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    display: 'block',
                    mt: 3,
                    color: '#9CA3AF',
                    fontSize: '0.875rem'
                  }}
                >
                  Maximum file size: 50MB
                </Typography>
              </>
            )}
          </Paper>
        </Box>
      ) : (
        /* Analysis Results */
        <Grid container spacing={3}>
          {/* File Info */}
          <Grid item xs={12}>
            <Alert severity="success" sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Analysis Complete: {analysis.filename}
              </Typography>
              <Typography>
                Found {analysis.total_tables_found} tables and {analysis.text_blocks.length} text blocks 
                across {analysis.total_pages} page{analysis.total_pages !== 1 ? 's' : ''} 
                (processed in {analysis.processing_time.toFixed(2)}s)
              </Typography>
            </Alert>
          </Grid>

          {/* Tables Section */}
          <Grid item xs={12} lg={8}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5" gutterBottom>
                  <TableChart sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Tables ({analysis.tables ? analysis.tables.length : 0})
                </Typography>
                <Box>
                  <Button 
                    size="small" 
                    onClick={() => setSelectedTables(analysis.tables && Array.isArray(analysis.tables) ? analysis.tables.map(t => t.table_id) : [])}
                    sx={{ mr: 1 }}
                  >
                    Select All
                  </Button>
                  <Button 
                    size="small" 
                    onClick={() => setSelectedTables([])}
                    color="secondary"
                  >
                    Deselect All
                  </Button>
                </Box>
              </Box>

              {analysis.tables && Array.isArray(analysis.tables) && analysis.tables.map((table, index) => (
                <Accordion key={table.table_id} sx={{ mb: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box display="flex" alignItems="center" width="100%">
                      <IconButton
                        onClick={(e) => {
                          e.stopPropagation();
                          handleTableSelection(table.table_id);
                        }}
                        size="small"
                        sx={{ mr: 2 }}
                      >
                        {selectedTables.includes(table.table_id) ? <CheckBox /> : <CheckBoxOutlineBlank />}
                      </IconButton>
                      <Box flexGrow={1}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {table.suggested_name} (Page {table.page})
                        </Typography>
                        <Box display="flex" gap={1} mt={0.5}>
                          <Chip 
                            label={table.table_type} 
                            size="small" 
                            color={getTypeColor(table.table_type) as any}
                          />
                          <Chip 
                            label={`${table.total_rows} rows`} 
                            size="small" 
                            variant="outlined"
                          />
                          <Chip 
                            label={`${Math.round(table.confidence * 100)}% confidence`} 
                            size="small" 
                            variant="outlined"
                          />
                        </Box>
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      Preview (showing first 5 rows):
                    </Typography>
                    <Box sx={{ overflowX: 'auto', maxHeight: 300 }}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            {table.columns && Array.isArray(table.columns) && table.columns.map((column, colIndex) => (
                              <TableCell key={colIndex} sx={{ fontWeight: 600 }}>
                                {column || `Column ${colIndex + 1}`}
                              </TableCell>
                            ))}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {table.sample_data && Array.isArray(table.sample_data) && table.sample_data.slice(0, 5).map((row, rowIndex) => (
                            <TableRow key={rowIndex}>
                              {Array.isArray(row) ? row.map((cell, cellIndex) => (
                                <TableCell key={cellIndex}>{cell || ''}</TableCell>
                              )) : (
                                <TableCell>{String(row || '')}</TableCell>
                              )}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </Box>
                    {table.total_rows > 5 && (
                      <Typography variant="caption" color="text.secondary" mt={1}>
                        ... and {table.total_rows - 5} more rows
                      </Typography>
                    )}
                  </AccordionDetails>
                </Accordion>
              ))}
            </Paper>
          </Grid>

          {/* Text Blocks Section */}
          <Grid item xs={12} lg={4}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" gutterBottom>
                  <TextSnippet sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Text Blocks ({analysis.text_blocks ? analysis.text_blocks.length : 0})
                </Typography>
                <Box>
                  <Button 
                    size="small" 
                    onClick={() => setSelectedTextBlocks(analysis.text_blocks && Array.isArray(analysis.text_blocks) ? analysis.text_blocks.map(b => b.block_id) : [])}
                    sx={{ mr: 1 }}
                  >
                    All
                  </Button>
                  <Button 
                    size="small" 
                    onClick={() => setSelectedTextBlocks([])}
                    color="secondary"
                  >
                    None
                  </Button>
                </Box>
              </Box>

              <List dense>
                {analysis.text_blocks && Array.isArray(analysis.text_blocks) && analysis.text_blocks.slice(0, 10).map((block) => (
                  <ListItem 
                    key={block.block_id}
                    button
                    onClick={() => handleTextBlockSelection(block.block_id)}
                    sx={{ 
                      border: '1px solid #e0e0e0', 
                      borderRadius: 1, 
                      mb: 1,
                      bgcolor: selectedTextBlocks.includes(block.block_id) ? 'action.selected' : 'background.paper'
                    }}
                  >
                    <ListItemIcon>
                      {selectedTextBlocks.includes(block.block_id) ? <CheckBox /> : <CheckBoxOutlineBlank />}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body2" fontWeight={500}>
                            Block {block.block_id + 1}
                          </Typography>
                          <Chip 
                            label={block.type} 
                            size="small" 
                            color={getTextTypeColor(block.type) as any}
                          />
                        </Box>
                      }
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {block.preview} ({block.word_count} words)
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
              </List>
              {analysis.text_blocks && analysis.text_blocks.length > 10 && (
                <Typography variant="caption" color="text.secondary">
                  ... and {analysis.text_blocks.length - 10} more blocks
                </Typography>
              )}
            </Paper>

            {/* Export Section */}
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                <Download sx={{ mr: 1, verticalAlign: 'middle' }} />
                Export Selection
              </Typography>
              
              <Typography variant="body2" color="text.secondary" mb={2}>
                Selected: {selectedTables.length} tables, {selectedTextBlocks.length} text blocks
              </Typography>

              <Button 
                variant="contained" 
                fullWidth 
                size="large"
                disabled={selectedTables.length === 0 && selectedTextBlocks.length === 0}
                onClick={() => setShowExportDialog(true)}
                startIcon={<Download />}
              >
                Export Selected Content
              </Button>

              <Button 
                variant="outlined" 
                fullWidth 
                size="small"
                sx={{ mt: 2 }}
                onClick={() => {
                  setAnalysis(null);
                  setSelectedTables([]);
                  setSelectedTextBlocks([]);
                }}
              >
                Analyze Another PDF
              </Button>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Export Options Dialog */}
      <Dialog open={showExportDialog} onClose={() => setShowExportDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Export Options</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Configure your export settings:
          </Typography>
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Output Format</InputLabel>
            <Select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value)}
              label="Output Format"
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
                  <FilePresent sx={{ mr: 1, color: 'purple' }} />
                  Word (.docx) - Tables and text formatted
                </Box>
              </MenuItem>
            </Select>
          </FormControl>

          <FormControlLabel
            control={
              <Checkbox
                checked={includeHeaders}
                onChange={(e) => setIncludeHeaders(e.target.checked)}
              />
            }
            label="Include table headers"
            sx={{ mt: 2 }}
          />

          <Alert severity="info" sx={{ mt: 2 }}>
            You are exporting {selectedTables.length} table{selectedTables.length !== 1 ? 's' : ''} 
            {selectedTextBlocks.length > 0 && ` and ${selectedTextBlocks.length} text block${selectedTextBlocks.length !== 1 ? 's' : ''}`}.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowExportDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleExport} 
            variant="contained"
            disabled={exporting}
          >
            {exporting ? 'Exporting...' : `Export ${exportFormat.toUpperCase()}`}
          </Button>
        </DialogActions>
      </Dialog>
      </Container>
    </Box>
  );
};

export default PDFViewer;