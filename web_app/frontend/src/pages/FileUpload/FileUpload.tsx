import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Alert,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Collapse,
  Checkbox,
  Fab,
  Tooltip,
  Container,
} from '@mui/material';
import {
  Description,
  ExpandMore,
  Download,
  Visibility,
  PlayArrow,
  CheckBox,
  CheckBoxOutlineBlank,
  SelectAll,
  Clear,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import api, { fileApi } from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import { extractApiErrorMessage } from '../../utils/errorUtils';

interface UploadedFile {
  id: number;
  original_filename: string;
  file_size: number;
  status: string;
  created_at: string;
  download_url?: string; // Puede venir del backend si el archivo está COMPLETED
}

interface PreviewData {
  tables_found: number;
  tables: Array<{
    table_number: number;
    rows: number;
    columns: string[];
    sample_data: Record<string, any>[];
  }>;
  file_info: {
    id: number;
    filename: string;
    size: number;
    uploaded_at: string;
  };
  processing_suggestions: {
    recommended_format: string;
    complexity_score: string;
    estimated_time: string;
    tips: string[];
  };
}

const FileUpload: React.FC = () => {
  const [outputFormat, setOutputFormat] = useState('excel');
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [expandedTable, setExpandedTable] = useState<number | null>(null);
  const [processingFiles, setProcessingFiles] = useState<Set<number>>(new Set());
  const [showModelDownload, setShowModelDownload] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<Set<number>>(new Set());
  const [batchProcessing, setBatchProcessing] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const queryClient = useQueryClient();

  // React Query for files list with longer stale time to reduce requests
  const { data: filesResponse, isLoading: filesLoading, error: filesError } = useQuery(
    'files',
    async () => {
      const { token } = useAuthStore.getState();
      const response = await api.get('/files', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      return response.data;
    },
    {
      staleTime: 30000, // 30 seconds before considering data stale
      cacheTime: 300000, // 5 minutes cache
      refetchOnWindowFocus: false, // Don't refetch on window focus
      retry: (failureCount, error: any) => {
        // Retry hasta 2 veces, pero no si es un error de autenticación
        if (error?.response?.status === 401) return false;
        return failureCount < 2;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 5000), // Exponential backoff
      onError: (error: any) => {
        if (error?.code === 'ECONNABORTED') {
          console.log('Files query timed out, will retry automatically');
        }
      },
    }
  );

  // Ensure uploadedFiles is always an array
  const uploadedFiles: UploadedFile[] = Array.isArray(filesResponse) 
    ? filesResponse 
    : filesResponse?.files || [];

  // Upload mutation - using fileApi with extended timeout and progress
  const uploadMutation = useMutation(
    async (file: File) => {
      const { token } = useAuthStore.getState();
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fileApi.post('/files/upload', formData, {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            Math.round((progressEvent.loaded * 100) / progressEvent.total);
            // TODO: Implement progress tracking
            // setUploadProgress(prev => ({ ...prev, [file.name]: progress }));
          }
        },
      });
      return { data: response.data, fileName: file.name };
    },
    {
      onSuccess: async (uploadResponse, file) => {
        toast.success(`${file.name} uploaded successfully!`);
        queryClient.invalidateQueries('files');
        if (uploadResponse?.data?.id) {
          // Espera activa a que el archivo esté en la lista antes de mostrar preview
          const found = await waitForFileInList(uploadResponse.data.id);
          if (found) {
            previewMutation.mutate(uploadResponse.data.id);
          } else {
            toast.error('El archivo fue subido pero no aparece en la lista. Refresca la página.');
          }
        }
      },
      onError: (error: any, file) => {
        // setUploadProgress(prev => {
        //   const newProgress = { ...prev };
        //   delete newProgress[file.name];
        //   return newProgress;
        // });
        if (error.code === 'ECONNABORTED') {
          toast.error(`Upload timeout for ${file.name}. File might be too large or connection too slow.`);
        } else {
          toast.error(extractApiErrorMessage(error) || `Upload failed for ${file.name}`);
        }
      },
    }
  );

  // Preview mutation - using fileApi with extended timeout
  const previewMutation = useMutation(
    async (fileId: number) => {
      const { token } = useAuthStore.getState();
      const response = await api.get(`/files/${fileId}/preview`, {
        timeout: 300000, // 5 minutes for preview (same as file uploads)
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
      return response.data;
    },
    {
      onSuccess: (data) => {
        setPreviewData(data);
        setPreviewOpen(true);
      },
      onError: (error: any) => {
        toast.error(extractApiErrorMessage(error) || 'Preview failed');
      },
    }
  );

  // Process mutation - using fileApi with extended timeout for processing
  const processMutation = useMutation(
    async ({ fileId, format }: { fileId: number; format: string }) => {
      const { token } = useAuthStore.getState();
      const response = await fileApi.post(`/files/${fileId}/process`, {
        output_format: format,
      }, {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          'Content-Type': 'application/json',
        },
        timeout: 45 * 600000, // 45x timeout: ~450 minutes for file processing
      });
      return response.data;
    },
    {
      onSuccess: (_data, variables) => {
        toast.success('Processing started! You\'ll be notified when complete.');
        setProcessingFiles(prev => new Set(prev).add(variables.fileId));
        
        // Start polling for status after a brief delay
        setTimeout(() => {
          pollFileStatus(variables.fileId);
        }, 2000); // Wait 2 seconds before starting to poll
      },
      onError: (error: any) => {
        toast.error(extractApiErrorMessage(error) || 'Processing failed');
      },
    }
  );

  // Batch process mutation - uses the new bulk processing endpoint
  const batchProcessMutation = useMutation(
    async ({ fileIds, format }: { fileIds: number[]; format: string }) => {
      setBatchProcessing(true);
      const { token } = useAuthStore.getState();
      
      const response = await fileApi.post('/files/bulk-process', {
        file_ids: fileIds,
        output_format: format,
      }, {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          'Content-Type': 'application/json',
        },
        timeout: 45 * 900000, // 45x timeout: ~675 minutes for bulk processing
      });
      
      return response.data;
    },
    {
      onSuccess: (data) => {
        if (data.total_queued > 0) {
          toast.success(`${data.total_queued} file${data.total_queued > 1 ? 's' : ''} queued for processing! They will be processed automatically.`);
          
          // Add all queued files to the processing set
          const queuedFileIds = data.queued_files.map((f: any) => f.file_id);
          setProcessingFiles(prev => {
            const newSet = new Set(prev);
            queuedFileIds.forEach((id: number) => newSet.add(id));
            return newSet;
          });
          
          // Start polling for all queued files
          queuedFileIds.forEach((fileId: number) => {
            setTimeout(() => {
              pollFileStatus(fileId);
            }, 3000); // Start polling after 3 seconds
          });
        }
        
        if (data.total_failed > 0) {
          toast.error(`${data.total_failed} file${data.total_failed > 1 ? 's' : ''} failed to queue`);
          console.warn('Failed files:', data.failed_files);
        }
        
        setSelectedFiles(new Set());
        setBatchProcessing(false);
        
        // Refresh the file list to show updated statuses
        queryClient.invalidateQueries('files');
      },
      onError: (error: any) => {
        toast.error(extractApiErrorMessage(error) || 'Batch processing failed');
        setBatchProcessing(false);
      },
    }
  );

  // Enhanced polling with extended timeout for batch processing
  const pollFileStatus = useCallback(async (fileId: number) => {
    let pollCount = 0;
    const maxPolls = 300; // Maximum 300 polls (15 minutes total) - much more time for complex PDFs
    
    const checkStatus = async (): Promise<boolean> => {
      pollCount++;
      
      // Show different messages at different stages
      if (pollCount === 60) { // After 3 minutes
        toast(`Still processing file ${fileId}. Complex PDFs may take several minutes...`, { 
          duration: 6000,
          icon: 'ℹ️',
          style: { background: '#e3f2fd', color: '#1976d2' }
        });
      } else if (pollCount === 120) { // After 6 minutes
        toast(`File ${fileId} is taking longer than usual. This is normal for large or complex PDFs.`, { 
          duration: 8000,
          icon: 'ℹ️',
          style: { background: '#e3f2fd', color: '#1976d2' }
        });
      } else if (pollCount === 240) { // After 12 minutes
        toast(`File ${fileId} processing is taking very long. You can continue using the app - we'll notify you when it's done.`, { 
          duration: 10000,
          icon: '⚠️',
          style: { background: '#fff3e0', color: '#f57c00' }
        });
      }
      
      if (pollCount > maxPolls) {
        // Don't remove from processing - just show a message that it's still running
        toast(`File ${fileId} is still processing in the background. Check the File Manager periodically for updates.`, { 
          duration: 12000,
          icon: '⚠️',
          style: { background: '#fff3e0', color: '#f57c00' }
        });
        return true; // Stop polling but keep in processing state
      }
      
      try {
        // Create a controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout
        
        const response = await api.get(`/files/${fileId}/status`, {
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        const data = response.data;
        const status = data.status;
        
        if (status === 'COMPLETED' || status === 'completed') {
          setProcessingFiles(prev => {
            const newSet = new Set(prev);
            newSet.delete(fileId);
            return newSet;
          });
          toast.success('File processed successfully!');
          queryClient.invalidateQueries('files'); // Refresh file list
          return true; // Stop polling
        } else if (status === 'FAILED' || status === 'failed') {
          setProcessingFiles(prev => {
            const newSet = new Set(prev);
            newSet.delete(fileId);
            return newSet;
          });
          toast.error('File processing failed');
          return true; // Stop polling
        }
        
        return false; // Continue polling
      } catch (error: any) {
        console.error(`Error checking file status (poll ${pollCount}):`, error);
        
        // Don't show error for timeouts, just continue polling
        if (error.name === 'AbortError') {
          console.log('Status check timed out, continuing...');
        }
        
        return false; // Continue polling
      }
    };

    const poll = async () => {
      const shouldStop = await checkStatus();
      if (!shouldStop) {
        // Dynamic polling interval - faster at first, slower later
        let interval = 3000; // Default 3 seconds
        if (pollCount > 60) interval = 5000;  // After 3 minutes: every 5 seconds
        if (pollCount > 120) interval = 10000; // After 6 minutes: every 10 seconds
        if (pollCount > 180) interval = 15000; // After 9 minutes: every 15 seconds
        
        setTimeout(poll, interval);
      }
    };

    poll();
  }, [queryClient]);

  // Helper: Espera activa hasta que el archivo subido aparezca en la lista
  const waitForFileInList = async (fileId: number, timeoutMs = 8000) => {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      // Refresca la lista y espera a que React Query la actualice
      await queryClient.invalidateQueries('files');
      await new Promise(res => setTimeout(res, 400)); // Espera a que la cache se actualice
      const filesResponse = queryClient.getQueryData('files');
      const files: UploadedFile[] = Array.isArray(filesResponse) 
        ? filesResponse 
        : (filesResponse as any)?.files || [];
      if (files.some(f => f.id === fileId)) return true;
    }
    return false;
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach(file => {
      uploadMutation.mutate(file);
    });
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/bmp': ['.bmp'],
      'image/tiff': ['.tiff'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true,
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const canUploadMore = () => {
    if (!user) return false;
    
    const limits = {
      free: 5,
      basic: 50,
      pro: 200,
      enterprise: -1,
    };
    
    const limit = limits[user.tier as keyof typeof limits] || 5;
    return limit === -1 || user.files_processed_this_month < limit;
  };

  // File selection handlers
  const handleSelectFile = (fileId: number) => {
    setSelectedFiles(prev => {
      const newSet = new Set(prev);
      if (newSet.has(fileId)) {
        newSet.delete(fileId);
      } else {
        newSet.add(fileId);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    const processableFiles = uploadedFiles.filter((f: UploadedFile) => 
      f.status !== 'completed' && f.status !== 'processing' && !processingFiles.has(f.id)
    );
    
    if (selectedFiles.size === processableFiles.length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(processableFiles.map((f: UploadedFile) => f.id)));
    }
  };

  const handleBatchProcess = () => {
    if (selectedFiles.size === 0) {
      toast.error('Please select files to process');
      return;
    }
    
    batchProcessMutation.mutate({
      fileIds: Array.from(selectedFiles),
      format: outputFormat
    });
  };

  // Get processable files count
  const processableFiles = uploadedFiles.filter((f: UploadedFile) => 
    f.status !== 'completed' && f.status !== 'processing' && !processingFiles.has(f.id)
  );

  const selectedProcessableFiles = uploadedFiles.filter((f: UploadedFile) => selectedFiles.has(f.id));

  // Detectar timeout y mostrar mensaje especial
  React.useEffect(() => {
    if (
      uploadMutation.isError &&
      uploadMutation.error &&
      typeof (uploadMutation.error as any).message === 'string' &&
      (uploadMutation.error as any).message.includes('timeout')
    ) {
      setShowModelDownload(true);
    }
  }, [uploadMutation.isError, uploadMutation.error]);


  // Limpia el estado de preview al cerrar el diálogo
  const handleClosePreview = () => {
    setPreviewOpen(false);
    setPreviewData(null);
    setExpandedTable(null);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {showModelDownload && (
        <Alert severity="info" sx={{ mb: 2 }}>
          El sistema está descargando modelos de IA para procesar PDFs escaneados. Esto puede demorar varios minutos la primera vez.<br />
          Por favor, espera y vuelve a intentar la subida si ves este mensaje.
        </Alert>
      )}

      <Typography variant="h4" fontWeight={700} gutterBottom>
        Upload Documents
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Upload your documents (PDF, Word, Excel) and images to extract tables with AI precision
      </Typography>

      <Grid container spacing={3} mt={2}>
        {/* Upload Area */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card>
              <CardContent>
                {!canUploadMore() ? (
                  <Alert severity="warning" sx={{ mb: 3 }}>
                    You've reached your monthly upload limit. 
                    <Button
                      variant="text"
                      onClick={() => navigate('/pricing')}
                      sx={{ ml: 1 }}
                    >
                      Upgrade to continue
                    </Button>
                  </Alert>
                ) : (
                  <Box
                    {...getRootProps()}
                    sx={{
                      border: '2px dashed',
                      borderColor: isDragActive ? 'primary.main' : 'grey.300',
                      borderRadius: 2,
                      p: 6,
                      textAlign: 'center',
                      cursor: 'pointer',
                      bgcolor: isDragActive ? 'rgba(102, 126, 234, 0.05)' : 'transparent',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: 'primary.main',
                        bgcolor: 'rgba(102, 126, 234, 0.05)',
                      },
                    }}
                  >
                    <input {...getInputProps()} />
                    <Description sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      {isDragActive ? 'Drop documents or images here' : 'Drag & drop documents or images here'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      or click to browse files
                    </Typography>
                    <Button variant="contained" sx={{ mt: 2 }}>
                      Choose Files
                    </Button>
                    <Typography variant="caption" display="block" sx={{ mt: 2 }}>
                      Supports PDF, Word (.doc/.docx), Excel (.xls/.xlsx), JPG, PNG, BMP, TIFF files up to 50MB each
                    </Typography>
                  </Box>
                )}

                {uploadMutation.isLoading && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="body2" gutterBottom>
                      Uploading...
                    </Typography>
                    <LinearProgress />
                  </Box>
                )}

                {/* Processing Queue Status */}
                {processingFiles.size > 0 && (
                  <Alert 
                    severity="info" 
                    sx={{ mt: 3 }}
                    action={
                      <Button
                        size="small"
                        onClick={() => {
                          // Restart polling for all processing files
                          processingFiles.forEach(fileId => {
                            setTimeout(() => pollFileStatus(fileId), 1000);
                          });
                          toast('Refreshing status for all processing files...', {
                            icon: 'ℹ️',
                            style: { background: '#e3f2fd', color: '#1976d2' }
                          });
                        }}
                      >
                        Refresh Status
                      </Button>
                    }
                  >
                    <Typography variant="body2" fontWeight={600} gutterBottom>
                      ⚡ Processing Queue Active ({processingFiles.size} files)
                    </Typography>
                    <Typography variant="caption">
                      Files are being processed by our AI system. Large or complex PDFs may take 5-15 minutes.
                      <br />
                      <strong>Tip:</strong> You can close this page and come back later - processing continues in the background!
                    </Typography>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Loading State */}
          {filesLoading && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <LinearProgress sx={{ flexGrow: 1 }} />
                  <Typography variant="body2">Loading files...</Typography>
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Error State */}
          {filesError && !filesLoading && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Alert 
                  severity="warning" 
                  action={
                    <Button
                      color="inherit"
                      size="small"
                      onClick={() => queryClient.invalidateQueries('files')}
                    >
                      Retry
                    </Button>
                  }
                >
                  <Typography variant="body2">
                    Connection issues detected. Files may not be up to date.
                    {(filesError as any)?.code === 'ECONNABORTED' && ' (Backend timeout)'}
                  </Typography>
                </Alert>
              </CardContent>
            </Card>
          )}

          {/* Uploaded Files */}
          {!filesLoading && uploadedFiles.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Card sx={{ mt: 3 }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6" fontWeight={600}>
                      Uploaded Files ({uploadedFiles.length})
                    </Typography>
                    
                    {processableFiles.length > 0 && (
                      <Box display="flex" alignItems="center" gap={1}>
                        <Checkbox
                          checked={selectedFiles.size === processableFiles.length && processableFiles.length > 0}
                          indeterminate={selectedFiles.size > 0 && selectedFiles.size < processableFiles.length}
                          onChange={handleSelectAll}
                          size="small"
                        />
                        <Typography variant="body2" color="text.secondary">
                          Select All Processable ({processableFiles.length})
                        </Typography>
                      </Box>
                    )}
                  </Box>
                  
                  {/* Batch Action Bar */}
                  {selectedFiles.size > 0 && (
                    <Alert 
                      severity="success" 
                      sx={{ mb: 2 }}
                      action={
                        <Box display="flex" gap={1}>
                          <Button
                            size="small"
                            variant="contained"
                            color="success"
                            startIcon={batchProcessing ? null : <PlayArrow />}
                            onClick={handleBatchProcess}
                            disabled={batchProcessing || selectedFiles.size === 0}
                          >
                            {batchProcessing ? (
                              <Box display="flex" alignItems="center" gap={1}>
                                <LinearProgress sx={{ width: 60, height: 4 }} />
                                <Typography variant="caption">Queueing...</Typography>
                              </Box>
                            ) : (
                              `Process ${selectedFiles.size} Files`
                            )}
                          </Button>
                          <Button
                            size="small"
                            startIcon={<Clear />}
                            onClick={() => setSelectedFiles(new Set())}
                            disabled={batchProcessing}
                          >
                            Clear
                          </Button>
                        </Box>
                      }
                    >
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          🚀 Batch Processing Ready: {selectedFiles.size} file{selectedFiles.size > 1 ? 's' : ''} selected
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Files will be processed automatically in queue - no need to wait!
                        </Typography>
                      </Box>
                    </Alert>
                  )}
                  
                  <Grid container spacing={2}>
                    {uploadedFiles.map((file: UploadedFile) => (
                      <Grid item xs={12} key={file.id}>
                        <Paper
                          elevation={1}
                          sx={{
                            p: 2,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 2,
                            bgcolor: selectedFiles.has(file.id) ? 'action.selected' : 'background.paper',
                            border: selectedFiles.has(file.id) ? '2px solid' : '1px solid',
                            borderColor: selectedFiles.has(file.id) ? 'primary.main' : 'divider',
                          }}
                        >
                          {/* Selection checkbox for processable files */}
                          {(file.status !== 'completed' && file.status !== 'processing' && !processingFiles.has(file.id)) && (
                            <Checkbox
                              checked={selectedFiles.has(file.id)}
                              onChange={() => handleSelectFile(file.id)}
                              size="small"
                            />
                          )}
                          <Description color="primary" />
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography variant="subtitle2" fontWeight={600}>
                              {file.original_filename}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {formatFileSize(file.file_size)}
                            </Typography>
                          </Box>
                          <Chip
                            label={file.status}
                            color={file.status === 'uploaded' ? 'success' : file.status === 'completed' ? 'info' : 'default'}
                            size="small"
                          />
                          <Button
                            size="small"
                            startIcon={<Visibility />}
                            onClick={() => previewMutation.mutate(file.id)}
                            disabled={previewMutation.isLoading}
                          >
                            Preview
                          </Button>
                          {file.status === 'completed' && file.download_url ? (
                            <Button
                              size="small"
                              variant="outlined"
                              startIcon={<Download />}
                              onClick={async () => {
                                if (!file.download_url) return;
                                const { token } = useAuthStore.getState();
                                try {
                                  const res = await fileApi.get(file.download_url, {
                                    responseType: 'blob',
                                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                                  });
                                  const url = window.URL.createObjectURL(new Blob([res.data]));
                                  const link = document.createElement('a');
                                  link.href = url;
                                  link.setAttribute('download', file.original_filename);
                                  document.body.appendChild(link);
                                  link.click();
                                  link.parentNode?.removeChild(link);
                                  window.URL.revokeObjectURL(url);
                                } catch (err) {
                                  toast.error('Download failed');
                                }
                              }}
                            >
                              Download
                            </Button>
                          ) : (
                            <Button
                              size="small"
                              variant={selectedFiles.has(file.id) ? "outlined" : "contained"}
                              onClick={() => processMutation.mutate({ 
                                fileId: file.id, 
                                format: outputFormat 
                              })}
                              disabled={processingFiles.has(file.id) || processMutation.isLoading || file.status === 'completed' || file.status === 'processing'}
                            >
                              {processingFiles.has(file.id) ? 'Processing...' : 'Extract'}
                            </Button>
                          )}
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </Grid>

        {/* Settings */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Output Settings
                </Typography>
                
                <FormControl component="fieldset" sx={{ mt: 2 }}>
                  <FormLabel component="legend">Output Format</FormLabel>
                  <RadioGroup
                    value={outputFormat}
                    onChange={(e) => setOutputFormat(e.target.value)}
                  >
                    <FormControlLabel
                      value="excel"
                      control={<Radio />}
                      label="Excel (.xlsx)"
                    />
                    <FormControlLabel
                      value="csv"
                      control={<Radio />}
                      label="CSV (.csv)"
                    />
                    <FormControlLabel
                      value="both"
                      control={<Radio />}
                      label="Both formats"
                    />
                  </RadioGroup>
                </FormControl>

                <Alert severity="info" sx={{ mt: 3 }}>
                  <Typography variant="body2">
                    <strong>Smart Features:</strong><br />
                    • Intelligent column mapping<br />
                    • Multi-page table detection<br />
                    • Automatic data validation
                  </Typography>
                </Alert>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Floating Action Button for Batch Processing */}
      {selectedFiles.size > 0 && (
        <Tooltip title={`Process ${selectedFiles.size} selected files`}>
          <Fab
            color="primary"
            sx={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 1000,
            }}
            onClick={handleBatchProcess}
            disabled={batchProcessing}
          >
            {batchProcessing ? (
              <LinearProgress sx={{ width: 40, height: 40, borderRadius: '50%' }} />
            ) : (
              <PlayArrow />
            )}
          </Fab>
        </Tooltip>
      )}

      {/* Preview Dialog */}
      <Dialog
        open={previewOpen}
        onClose={handleClosePreview}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="between" alignItems="center">
            <Typography variant="h6">
              Table Preview: {previewData?.file_info?.filename || 'Unknown File'}
            </Typography>
            <IconButton onClick={handleClosePreview}>
              ×
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {previewData && (
            <Box>
              {/* Summary */}
              <Alert severity="info" sx={{ mb: 3 }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Tables Found:</strong> {previewData.tables_found || 0}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Complexity:</strong> {previewData.processing_suggestions?.complexity_score || 'Unknown'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Estimated Time:</strong> {previewData.processing_suggestions?.estimated_time || 'Unknown'}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Recommended:</strong> {previewData.processing_suggestions?.recommended_format || 'Unknown'}
                    </Typography>
                  </Grid>
                </Grid>
              </Alert>

              {/* Tips */}
              {previewData.processing_suggestions?.tips?.length > 0 && (
                <Alert severity="success" sx={{ mb: 3 }}>
                  <Typography variant="body2" fontWeight={600} gutterBottom>
                    AI Suggestions:
                  </Typography>
                  {previewData.processing_suggestions?.tips?.map((tip, index) => (
                    <Typography key={index} variant="body2">
                      • {tip}
                    </Typography>
                  ))}
                </Alert>
              )}

              {/* Tables */}
              {previewData.tables?.map((table) => (
                <Card key={table.table_number} sx={{ mb: 2 }}>
                  <CardContent>
                    <Box
                      display="flex"
                      justifyContent="between"
                      alignItems="center"
                      sx={{ cursor: 'pointer' }}
                      onClick={() => setExpandedTable(
                        expandedTable === table.table_number ? null : table.table_number
                      )}
                    >
                      <Typography variant="h6">
                        Table {table.table_number} ({table.rows} rows, {table.columns.length} columns)
                      </Typography>
                      <IconButton>
                        <ExpandMore
                          sx={{
                            transform: expandedTable === table.table_number 
                              ? 'rotate(180deg)' : 'rotate(0deg)',
                            transition: 'transform 0.3s',
                          }}
                        />
                      </IconButton>
                    </Box>
                    
                    <Collapse in={expandedTable === table.table_number}>
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Columns: {Array.isArray(table.columns) ? table.columns.join(', ') : 'No columns available'}
                        </Typography>
                        
                        {table.sample_data.length > 0 && (
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                {Array.isArray(table.columns) ? table.columns.map((col) => (
                                  <TableCell key={col}>{col}</TableCell>
                                )) : (
                                  <TableCell>No columns available</TableCell>
                                )}
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {table.sample_data.slice(0, 5).map((row, index) => (
                                <TableRow key={index}>
                                  {Array.isArray(table.columns) ? table.columns.map((col) => (
                                    <TableCell key={col}>
                                      {row[col] || '-'}
                                    </TableCell>
                                  )) : (
                                    <TableCell>No data available</TableCell>
                                  )}
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        )}
                      </Box>
                    </Collapse>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClosePreview}>
            Close
          </Button>
          {previewData && (
            <Button
              variant="contained"
              onClick={() => {
                if (previewData?.file_info?.id) {
                  processMutation.mutate({ 
                    fileId: previewData.file_info.id, 
                    format: outputFormat 
                  });
                  setPreviewOpen(false);
                }
              }}
            >
              Process This File
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FileUpload;