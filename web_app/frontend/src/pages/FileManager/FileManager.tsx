import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
  Menu,
  MenuItem,
  TextField,
  InputAdornment,
  Grid,
  Avatar,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  Checkbox,
  Container,
} from '@mui/material';
import {
  MoreVert,
  Download,
  Delete,
  Search,
  Refresh,
  TableChart,
  DeleteOutline,
  GetApp,
  SelectAll,
  Clear,
  Info,
  Edit,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import api from '../../services/api';
import axios from 'axios';
import { extractApiErrorMessage } from '../../utils/errorUtils';
import TableEditor from '../../components/TableEditor';

interface ProcessedFile {
  id: number;
  original_filename: string | null;
  file_size: number;
  status: string;
  output_format: string | null;
  tables_found: number;
  total_rows: number;
  processing_time: number | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
  download_url: string | null;
}

const FileManager: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedFile, setSelectedFile] = useState<ProcessedFile | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<ProcessedFile | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<Set<number>>(new Set());
  const [bulkDeleteDialogOpen, setBulkDeleteDialogOpen] = useState(false);
  const [tableEditorOpen, setTableEditorOpen] = useState(false);
  const [fileToEdit, setFileToEdit] = useState<ProcessedFile | null>(null);
  const queryClient = useQueryClient();

  // Fetch files
  const { data: filesResponse, isLoading, refetch } = useQuery(
    ['files', searchTerm, statusFilter],
    async () => {
      const params = new URLSearchParams();
      if (statusFilter) params.append('status_filter', statusFilter);
      
      const response = await api.get(`/files/?${params.toString()}`);
      return response.data;
    },
    {
      refetchInterval: false, // Disable auto-refresh to improve performance
      staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    }
  );

  // Ensure files is always an array
  const files: ProcessedFile[] = Array.isArray(filesResponse) 
    ? filesResponse 
    : filesResponse?.files || [];

  // Delete file mutation
  const deleteMutation = useMutation(
    async (fileId: number) => {
      await api.delete(`/files/${fileId}`);
    },
    {
      onSuccess: () => {
        toast.success('File deleted successfully');
        queryClient.invalidateQueries(['files', searchTerm, statusFilter]);
        setDeleteDialogOpen(false);
        setFileToDelete(null);
      },
      onError: (error: any) => {
        toast.error(extractApiErrorMessage(error) || 'Failed to delete file');
      },
    }
  );

  // Bulk delete mutation
  const bulkDeleteMutation = useMutation(
    async (fileIds: number[]) => {
      const response = await api.post('/files/bulk-delete', { file_ids: fileIds });
      return response.data;
    },
    {
      onSuccess: (data) => {
        if (data.total_deleted > 0) {
          toast.success(`${data.total_deleted} file${data.total_deleted > 1 ? 's' : ''} deleted successfully`);
        }
        if (data.total_failed > 0) {
          toast.error(`${data.total_failed} file${data.total_failed > 1 ? 's' : ''} failed to delete`);
        }
        // Invalidate all file-related queries to force refresh
        queryClient.invalidateQueries(['files']);
        queryClient.refetchQueries(['files', searchTerm, statusFilter]);
        setBulkDeleteDialogOpen(false);
        setSelectedFiles(new Set());
      },
      onError: (error: any) => {
        toast.error(extractApiErrorMessage(error) || 'Failed to delete files');
      },
    }
  );

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, file: ProcessedFile) => {
    setAnchorEl(event.currentTarget);
    setSelectedFile(file);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedFile(null);
  };

  const handleEditTables = (file: ProcessedFile) => {
    setFileToEdit(file);
    setTableEditorOpen(true);
    handleMenuClose();
  };

  const apiBaseUrl = 'http://localhost:8000';

  const getAuthToken = () => {
    // Busca el token en auth-storage (persist:auth-storage)
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      try {
        const parsed = JSON.parse(authStorage);
        return parsed.state?.token || null;
      } catch {
        return null;
      }
    }
    return null;
  };

  const handleDownload = async (file: ProcessedFile) => {
    const token = getAuthToken();
    if (!token) {
      toast.error('You must be logged in to download files.');
      return;
    }
    if (file.download_url) {
      try {
        const downloadUrl = file.download_url.startsWith('http')
          ? file.download_url
          : `${apiBaseUrl}${file.download_url}`;
        const res = await axios.get(downloadUrl, {
          responseType: 'blob',
          headers: { Authorization: `Bearer ${token}` },
        });
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', (file.original_filename || 'download').replace(/\.pdf$/i, (file.output_format === 'excel' ? '_tables.xlsx' : file.output_format === 'csv' ? '_tables.csv' : '_tables.zip')));
        document.body.appendChild(link);
        link.click();
        link.parentNode?.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (err: any) {
        if (err.response && err.response.status === 403) {
          toast.error('Session expired or unauthorized. Please log in again.');
        } else {
          toast.error('Download failed');
        }
      }
    }
    handleMenuClose();
  };

  const handleDelete = (file: ProcessedFile) => {
    setFileToDelete(file);
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  const handleSelectFile = (fileId: number) => {
    const newSelected = new Set(selectedFiles);
    if (newSelected.has(fileId)) {
      newSelected.delete(fileId);
    } else {
      newSelected.add(fileId);
    }
    setSelectedFiles(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedFiles.size === filteredFiles.length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(filteredFiles.map(f => f.id)));
    }
  };

  const handleBulkDelete = () => {
    setBulkDeleteDialogOpen(true);
  };

  const handleBulkDownload = async () => {
    const selectedFilesArray = filteredFiles.filter(f => selectedFiles.has(f.id) && f.download_url);
    
    if (selectedFilesArray.length === 0) {
      toast.error('No downloadable files selected');
      return;
    }

    toast.success(`Starting download of ${selectedFilesArray.length} files...`);
    
    for (const file of selectedFilesArray) {
      try {
        await handleDownload(file);
        // Small delay between downloads to avoid overwhelming the browser
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (error) {
        console.error(`Failed to download ${file.original_filename}:`, error);
      }
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'info';
      case 'failed': return 'error';
      case 'uploaded': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'processing': return '⏳';
      case 'failed': return '❌';
      case 'uploaded': return '📤';
      default: return '📄';
    }
  };

  const filteredFiles = files.filter(file => 
    file.original_filename?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false
  );

  // Clear selection when filters change
  React.useEffect(() => {
    setSelectedFiles(new Set());
  }, [searchTerm, statusFilter]);

  // Keyboard shortcuts
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      const isInputField = target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA');
      
      // Ctrl/Cmd + A to select all
      if ((event.ctrlKey || event.metaKey) && event.key === 'a' && !isInputField) {
        event.preventDefault();
        handleSelectAll();
      }
      // Delete key to delete selected files
      if (event.key === 'Delete' && selectedFiles.size > 0 && !isInputField) {
        event.preventDefault();
        handleBulkDelete();
      }
      // Escape to clear selection
      if (event.key === 'Escape' && selectedFiles.size > 0) {
        setSelectedFiles(new Set());
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedFiles.size, filteredFiles.length]);

  const getStats = () => {
    const total = filteredFiles.length;
    const completed = filteredFiles.filter(f => f.status === 'completed').length;
    const processing = filteredFiles.filter(f => f.status === 'processing').length;
    const failed = filteredFiles.filter(f => f.status === 'failed').length;
    
    return { total, completed, processing, failed };
  };

  const stats = getStats();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading files...</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        File Manager
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Manage your uploaded files and download extracted tables
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mt: 2, mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Avatar sx={{ bgcolor: '#667eea', mx: 'auto', mb: 1 }}>
                  <TableChart />
                </Avatar>
                <Typography variant="h4" fontWeight={700} color="primary">
                  {stats.total}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Files
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Avatar sx={{ bgcolor: '#10b981', mx: 'auto', mb: 1 }}>
                  ✅
                </Avatar>
                <Typography variant="h4" fontWeight={700} color="success.main">
                  {stats.completed}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Completed
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Avatar sx={{ bgcolor: '#3b82f6', mx: 'auto', mb: 1 }}>
                  ⏳
                </Avatar>
                <Typography variant="h4" fontWeight={700} color="info.main">
                  {stats.processing}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Processing
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Avatar sx={{ bgcolor: '#ef4444', mx: 'auto', mb: 1 }}>
                  ❌
                </Avatar>
                <Typography variant="h4" fontWeight={700} color="error.main">
                  {stats.failed}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Failed
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Filters and Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  placeholder="Search files..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  select
                  label="Filter by status"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  SelectProps={{ native: true }}
                >
                  <option value="">All</option>
                  <option value="uploaded">Uploaded</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </TextField>
              </Grid>
              <Grid item xs={12} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={() => refetch()}
                >
                  Refresh
                </Button>
              </Grid>
            </Grid>
            
            {/* Bulk Actions Bar */}
            {selectedFiles.size > 0 && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <Box sx={{ 
                  mt: 2, 
                  p: 2.5, 
                  bgcolor: 'primary.light',
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: 'primary.main',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={6}>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Info color="primary" fontSize="small" />
                        <Typography variant="body1" color="primary.main" fontWeight={700}>
                          {selectedFiles.size} file{selectedFiles.size > 1 ? 's' : ''} selected
                        </Typography>
                        <Chip 
                          label={`${filteredFiles.filter(f => selectedFiles.has(f.id) && f.download_url).length} downloadable`}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Box display="flex" gap={1} justifyContent={{ xs: 'flex-start', md: 'flex-end' }}>
                        <Button
                          size="medium"
                          variant="contained"
                          startIcon={<GetApp />}
                          onClick={handleBulkDownload}
                          disabled={!filteredFiles.some(f => selectedFiles.has(f.id) && f.download_url)}
                          sx={{ 
                            bgcolor: 'success.main',
                            '&:hover': { bgcolor: 'success.dark' }
                          }}
                        >
                          Download ({filteredFiles.filter(f => selectedFiles.has(f.id) && f.download_url).length})
                        </Button>
                        <Button
                          size="medium"
                          variant="contained"
                          color="error"
                          startIcon={<DeleteOutline />}
                          onClick={handleBulkDelete}
                        >
                          Delete ({selectedFiles.size})
                        </Button>
                        <Button
                          size="medium"
                          variant="outlined"
                          startIcon={<Clear />}
                          onClick={() => setSelectedFiles(new Set())}
                          sx={{ 
                            borderColor: 'grey.400',
                            color: 'grey.600',
                            '&:hover': { 
                              borderColor: 'grey.600',
                              bgcolor: 'grey.50'
                            }
                          }}
                        >
                          Clear
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              </motion.div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Selection Helper */}
      {filteredFiles.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.45 }}
        >
          <Card sx={{ mb: 2, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box display="flex" alignItems="center" gap={2}>
                  <Checkbox
                    checked={selectedFiles.size === filteredFiles.length && filteredFiles.length > 0}
                    indeterminate={selectedFiles.size > 0 && selectedFiles.size < filteredFiles.length}
                    onChange={handleSelectAll}
                    size="medium"
                    color="primary"
                  />
                  <Box>
                    <Typography variant="body1" fontWeight={600}>
                      {selectedFiles.size === 0 
                        ? 'Select files for bulk actions'
                        : selectedFiles.size === filteredFiles.length
                        ? 'All files selected'
                        : `${selectedFiles.size} of ${filteredFiles.length} files selected`
                      }
                    </Typography>
                    {selectedFiles.size === 0 && (
                      <Typography variant="caption" color="text.secondary">
                        Use checkboxes to select multiple files for batch operations
                        <br />
                        <strong>Shortcuts:</strong> Ctrl+A (Select All) • Delete (Delete Selected) • Esc (Clear Selection)
                      </Typography>
                    )}
                  </Box>
                </Box>
                
                <Box display="flex" gap={1}>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<SelectAll />}
                    onClick={handleSelectAll}
                    disabled={filteredFiles.length === 0}
                  >
                    {selectedFiles.size === filteredFiles.length ? 'Deselect All' : 'Select All'}
                  </Button>
                  {selectedFiles.size > 0 && (
                    <Button
                      size="small"
                      variant="text"
                      startIcon={<Clear />}
                      onClick={() => setSelectedFiles(new Set())}
                    >
                      Clear
                    </Button>
                  )}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Files Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <Card>
          <CardContent sx={{ p: 0 }}>
            {filteredFiles.length === 0 ? (
              <Box textAlign="center" py={6}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No files found
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {searchTerm || statusFilter 
                    ? 'Try adjusting your search or filter criteria'
                    : 'Upload your first PDF to get started'
                  }
                </Typography>
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedFiles.size === filteredFiles.length && filteredFiles.length > 0}
                          indeterminate={selectedFiles.size > 0 && selectedFiles.size < filteredFiles.length}
                          onChange={handleSelectAll}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>File</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Tables</TableCell>
                      <TableCell>Rows</TableCell>
                      <TableCell>Format</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredFiles.map((file) => (
                      <TableRow 
                        key={file.id} 
                        hover
                        selected={selectedFiles.has(file.id)}
                        sx={{
                          bgcolor: selectedFiles.has(file.id) ? 'action.selected' : 'inherit'
                        }}
                      >
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={selectedFiles.has(file.id)}
                            onChange={() => handleSelectFile(file.id)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={2}>
                            <Avatar sx={{ width: 32, height: 32, fontSize: '1rem' }}>
                              {getStatusIcon(file.status)}
                            </Avatar>
                            <Box>
                              <Typography variant="subtitle2" fontWeight={600}>
                                {file.original_filename}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {formatFileSize(file.file_size)}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        
                        <TableCell>
                          <Chip
                            label={file.status}
                            color={getStatusColor(file.status)}
                            size="small"
                          />
                          {file.status === 'processing' && (
                            <LinearProgress sx={{ mt: 1, width: 100 }} />
                          )}
                          {file.status === 'failed' && file.error_message && (
                            <Typography variant="caption" color="error" display="block">
                              {file.error_message}
                            </Typography>
                          )}
                        </TableCell>
                        
                        <TableCell>
                          <Typography variant="body2" fontWeight={600}>
                            {file.tables_found || 0}
                          </Typography>
                        </TableCell>
                        
                        <TableCell>
                          <Typography variant="body2">
                            {file.total_rows ? file.total_rows.toLocaleString() : '-'}
                          </Typography>
                        </TableCell>
                        
                        <TableCell>
                          <Chip
                            label={file.output_format?.toUpperCase() || 'UNKNOWN'}
                            variant="outlined"
                            size="small"
                          />
                        </TableCell>
                        
                        <TableCell>
                          <Typography variant="body2">
                            {format(new Date(file.created_at), 'MMM dd, yyyy')}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {format(new Date(file.created_at), 'HH:mm')}
                          </Typography>
                        </TableCell>
                        
                        <TableCell>
                          <Box display="flex" gap={1}>
                            {file.download_url && (
                              <Tooltip title="Download file (reflects current state of edited tables)">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDownload(file)}
                                  color="primary"
                                >
                                  <Download />
                                </IconButton>
                              </Tooltip>
                            )}
                            <IconButton
                              size="small"
                              onClick={(e) => handleMenuOpen(e, file)}
                            >
                              <MoreVert />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        {selectedFile?.status === 'completed' && selectedFile?.tables_found > 0 && (
          <MenuItem onClick={() => handleEditTables(selectedFile)}>
            <Edit sx={{ mr: 1 }} />
            Edit Tables
          </MenuItem>
        )}
        <MenuItem onClick={() => handleDelete(selectedFile!)}>
          <Delete sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete File</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{fileToDelete?.original_filename}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => deleteMutation.mutate(fileToDelete!.id)}
            color="error"
            disabled={deleteMutation.isLoading}
          >
            {deleteMutation.isLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Delete Confirmation Dialog */}
      <Dialog
        open={bulkDeleteDialogOpen}
        onClose={() => setBulkDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Multiple Files</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Are you sure you want to delete {selectedFiles.size} selected file{selectedFiles.size > 1 ? 's' : ''}?
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This action cannot be undone. The following files will be permanently deleted:
          </Typography>
          <Box sx={{ mt: 2, maxHeight: 200, overflowY: 'auto' }}>
            {filteredFiles
              .filter(f => selectedFiles.has(f.id))
              .map(file => (
                <Typography key={file.id} variant="body2" sx={{ py: 0.5 }}>
                  • {file.original_filename}
                </Typography>
              ))
            }
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => bulkDeleteMutation.mutate(Array.from(selectedFiles))}
            color="error"
            disabled={bulkDeleteMutation.isLoading}
            variant="contained"
          >
            {bulkDeleteMutation.isLoading ? 'Deleting...' : `Delete ${selectedFiles.size} Files`}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Table Editor Dialog */}
      {fileToEdit && (
        <TableEditor
          open={tableEditorOpen}
          onClose={() => {
            setTableEditorOpen(false);
            setFileToEdit(null);
          }}
          fileId={fileToEdit.id}
          filename={fileToEdit.original_filename || 'Unknown File'}
        />
      )}
    </Container>
  );
};

export default FileManager;