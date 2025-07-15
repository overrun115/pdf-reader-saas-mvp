import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Tab,
  Tabs,
  IconButton,
  TextField,
  Alert,
  Chip,
  CircularProgress,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  InputAdornment,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import {
  Close as CloseIcon,
  Download as DownloadIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Restore as RestoreIcon,
  Undo as UndoIcon,
  CheckBox,
  CheckBoxOutlineBlank,
  SelectAll as SelectAllIcon,
  DeleteSweep as BulkDeleteIcon,
  Clear as ClearIcon,
  Save as SaveIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import api from '../../services/api';
import toast from 'react-hot-toast';

interface TableData {
  id: number;
  table_index: number;
  table_name: string;
  data: string[][];
  headers: string[];
  rows_count: number;
  columns_count: number;
  has_changes: boolean;
}

interface TableEditorProps {
  open: boolean;
  onClose: () => void;
  fileId: number;
  filename: string;
}

const TableEditor: React.FC<TableEditorProps> = ({
  open,
  onClose,
  fileId,
  filename,
}) => {
  const [tables, setTables] = useState<TableData[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingTableName, setEditingTableName] = useState<number | null>(null);
  const [newTableName, setNewTableName] = useState('');
  const [editingCell, setEditingCell] = useState<{tableIndex: number, rowIndex: number, colIndex: number} | null>(null);
  const [cellValue, setCellValue] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set());
  const [selectedColumns, setSelectedColumns] = useState<Set<number>>(new Set());
  const [selectionMode, setSelectionMode] = useState<'none' | 'rows' | 'columns'>('none');
  
  // New state for save functionality and confirmations
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [pendingChanges, setPendingChanges] = useState<Map<string, any>>(new Map());
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
    confirmText?: string;
    severity?: 'warning' | 'error';
  }>({
    open: false,
    title: '',
    message: '',
    onConfirm: () => {},
  });

  // Load tables data when dialog opens
  useEffect(() => {
    if (open && fileId) {
      loadTables();
    }
  }, [open, fileId]); // loadTables is defined inline, so it's okay to omit it

  const loadTables = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/files/${fileId}/tables?t=${Date.now()}`);
      
      if (response.data.length === 0) {
        toast.error('This file has no tables to edit. Please try with a file that contains tables.');
        onClose();
        return;
      }
      
      setTables(response.data);
      setActiveTab(0);
    } catch (error: any) {
      console.error('Error loading tables:', error);
      toast.error('Failed to load tables for editing');
      onClose();
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    // Clear selection when changing tables
    clearSelection();
  };

  const handleCellEdit = (tableIndex: number, rowIndex: number, colIndex: number, value: string) => {
    // Update local state immediately for better UX
    const updatedTables = [...tables];
    const table = updatedTables.find(t => t.table_index === tableIndex);
    if (table) {
      const originalValue = table.data[rowIndex][colIndex];
      table.data[rowIndex][colIndex] = value;
      table.has_changes = true;
      setTables(updatedTables);
      
      // Track this change in pending changes
      const changeKey = `${tableIndex}-${rowIndex}-${colIndex}`;
      const newPendingChanges = new Map(pendingChanges);
      newPendingChanges.set(changeKey, {
        tableIndex,
        rowIndex,
        colIndex,
        value,
        originalValue,
        type: 'cell'
      });
      setPendingChanges(newPendingChanges);
      setHasUnsavedChanges(true);
    }
  };

  const handleAddRow = async (tableIndex: number) => {
    try {
      setSaving(true);
      await api.post(`/files/${fileId}/tables/${tableIndex}/row`, {
        operation: 'add_row',
        index: tables[activeTab].data.length,
      });
      
      toast.success('Row added successfully');
      loadTables();
    } catch (error: any) {
      console.error('Error adding row:', error);
      toast.error('Failed to add row');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteRow = async (tableIndex: number, rowIndex: number) => {
    try {
      setSaving(true);
      await api.post(`/files/${fileId}/tables/${tableIndex}/row`, {
        operation: 'delete_row',
        index: rowIndex,
      });
      
      toast.success('Row deleted successfully');
      loadTables();
    } catch (error: any) {
      console.error('Error deleting row:', error);
      toast.error('Failed to delete row');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveTableName = async (tableIndex: number, newName: string) => {
    try {
      setSaving(true);
      await api.put(`/files/${fileId}/tables/${tableIndex}`, {
        table_name: newName,
      });
      
      toast.success('Table name updated successfully');
      setEditingTableName(null);
      loadTables();
    } catch (error: any) {
      console.error('Error updating table name:', error);
      toast.error('Failed to update table name');
    } finally {
      setSaving(false);
    }
  };

  const handleExport = async (format: string) => {
    try {
      setSaving(true);
      
      // The export endpoint now returns the file directly
      const response = await api.post(`/files/${fileId}/export-edited`, {
        format: format,
      }, {
        responseType: 'blob',
      });
      
      toast.success(`Export completed successfully`);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      // Use correct file extension
      const fileExtension = format === 'excel' ? 'xlsx' : format;
      link.download = `${filename}_edited.${fileExtension}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error: any) {
      console.error('Error exporting:', error);
      toast.error('Failed to export edited tables');
    } finally {
      setSaving(false);
    }
  };

  const handleCellClick = (tableIndex: number, rowIndex: number, colIndex: number, currentValue: string) => {
    setEditingCell({ tableIndex, rowIndex, colIndex });
    setCellValue(currentValue);
  };

  const handleCellSave = () => {
    if (!editingCell) return;
    
    handleCellEdit(editingCell.tableIndex, editingCell.rowIndex, editingCell.colIndex, cellValue);
    setEditingCell(null);
    setCellValue('');
  };

  const handleSaveAllChanges = async () => {
    if (pendingChanges.size === 0) {
      toast('No changes to save', { icon: 'ℹ️' });
      return;
    }

    try {
      setSaving(true);
      const changeArray = Array.from(pendingChanges.values());
      
      // Group changes by table and type
      const cellChanges = changeArray.filter(change => change.type === 'cell');
      
      // Save all cell changes
      for (const change of cellChanges) {
        await api.post(`/files/${fileId}/tables/${change.tableIndex}/cell`, {
          row_index: change.rowIndex,
          col_index: change.colIndex,
          value: change.value,
        });
      }
      
      // Clear pending changes
      setPendingChanges(new Map());
      setHasUnsavedChanges(false);
      
      toast.success(`Successfully saved ${changeArray.length} change${changeArray.length > 1 ? 's' : ''}`);
      
      // Reload to ensure we have the latest state
      await loadTables();
      
    } catch (error: any) {
      console.error('Error saving changes:', error);
      toast.error('Failed to save some changes. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleDiscardChanges = () => {
    setConfirmDialog({
      open: true,
      title: 'Discard Changes',
      message: `Are you sure you want to discard ${pendingChanges.size} unsaved change${pendingChanges.size > 1 ? 's' : ''}? This action cannot be undone.`,
      severity: 'warning',
      confirmText: 'Discard',
      onConfirm: () => {
        setPendingChanges(new Map());
        setHasUnsavedChanges(false);
        loadTables(); // Reload original data
        setConfirmDialog({ ...confirmDialog, open: false });
        toast('Changes discarded', { icon: 'ℹ️' });
      }
    });
  };

  const handleCellCancel = () => {
    setEditingCell(null);
    setCellValue('');
  };

  const handleResetTable = (tableIndex: number) => {
    const table = tables.find(t => t.table_index === tableIndex);
    setConfirmDialog({
      open: true,
      title: 'Reset Table to Original',
      message: `Are you sure you want to reset "${table?.table_name}" to its original state? This will discard ALL modifications made to this table and cannot be undone.`,
      severity: 'error',
      confirmText: 'Reset Table',
      onConfirm: async () => {
        try {
          setSaving(true);
          await api.post(`/files/${fileId}/tables/${tableIndex}/reset`);
          
          // Clear any pending changes for this table
          const newPendingChanges = new Map(pendingChanges);
          Array.from(pendingChanges.entries()).forEach(([key, change]) => {
            if (change.tableIndex === tableIndex) {
              newPendingChanges.delete(key);
            }
          });
          setPendingChanges(newPendingChanges);
          setHasUnsavedChanges(newPendingChanges.size > 0);
          
          toast.success('Table reset to original state successfully');
          loadTables(); // Reload to show reset data
        } catch (error: any) {
          console.error('Error resetting table:', error);
          toast.error('Failed to reset table to original state');
        } finally {
          setSaving(false);
        }
        setConfirmDialog({ ...confirmDialog, open: false });
      }
    });
  };

  const handleUndoLastChange = (tableIndex: number) => {
    const table = tables.find(t => t.table_index === tableIndex);
    setConfirmDialog({
      open: true,
      title: 'Undo Last Change',
      message: `Are you sure you want to undo the last change made to "${table?.table_name}"? This action will revert the table to its previous state and cannot be undone.`,
      severity: 'warning',
      confirmText: 'Undo Change',
      onConfirm: async () => {
        try {
          setSaving(true);
          await api.post(`/files/${fileId}/tables/${tableIndex}/undo`);
          
          // Clear any pending changes for this table since we're undoing
          const newPendingChanges = new Map(pendingChanges);
          Array.from(pendingChanges.entries()).forEach(([key, change]) => {
            if (change.tableIndex === tableIndex) {
              newPendingChanges.delete(key);
            }
          });
          setPendingChanges(newPendingChanges);
          setHasUnsavedChanges(newPendingChanges.size > 0);
          
          toast.success('Last change undone successfully');
          loadTables(); // Reload to show undone state
        } catch (error: any) {
          console.error('Error undoing last change:', error);
          if (error.response?.status === 400) {
            toast.error('No previous state available for undo');
          } else {
            toast.error('Failed to undo last change');
          }
        } finally {
          setSaving(false);
        }
        setConfirmDialog({ ...confirmDialog, open: false });
      }
    });
  };

  const handleRowSelection = (rowIndex: number) => {
    const newSelectedRows = new Set(selectedRows);
    if (newSelectedRows.has(rowIndex)) {
      newSelectedRows.delete(rowIndex);
    } else {
      newSelectedRows.add(rowIndex);
    }
    setSelectedRows(newSelectedRows);
  };

  const handleColumnSelection = (colIndex: number) => {
    const newSelectedColumns = new Set(selectedColumns);
    if (newSelectedColumns.has(colIndex)) {
      newSelectedColumns.delete(colIndex);
    } else {
      newSelectedColumns.add(colIndex);
    }
    setSelectedColumns(newSelectedColumns);
  };

  const handleSelectAllRows = () => {
    if (!currentTable) return;
    const filteredData = filterTableData(currentTable);
    if (selectedRows.size === filteredData.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(filteredData.map((_, index) => index)));
    }
  };

  const handleSelectAllColumns = () => {
    if (!currentTable) return;
    if (selectedColumns.size === currentTable.headers.length) {
      setSelectedColumns(new Set());
    } else {
      setSelectedColumns(new Set(currentTable.headers.map((_, index) => index)));
    }
  };

  const handleBulkDeleteRows = async () => {
    if (selectedRows.size === 0 || !currentTable) return;
    
    try {
      setSaving(true);
      const filteredData = filterTableData(currentTable);
      const realRowIndices = Array.from(selectedRows).map(filteredIndex => {
        const filteredRow = filteredData[filteredIndex];
        return currentTable.data.findIndex(originalRow => 
          JSON.stringify(originalRow) === JSON.stringify(filteredRow)
        );
      }).filter(index => index !== -1).sort((a, b) => b - a); // Sort descending for proper deletion

      for (const rowIndex of realRowIndices) {
        await api.post(`/files/${fileId}/tables/${currentTable.table_index}/row`, {
          operation: 'delete_row',
          index: rowIndex,
        });
      }
      
      toast.success(`${selectedRows.size} rows deleted successfully`);
      setSelectedRows(new Set());
      setSelectionMode('none');
      loadTables();
    } catch (error: any) {
      console.error('Error deleting rows:', error);
      toast.error('Failed to delete selected rows');
    } finally {
      setSaving(false);
    }
  };

  const handleBulkDeleteColumns = async () => {
    if (selectedColumns.size === 0 || !currentTable) return;
    
    try {
      setSaving(true);
      await api.post(`/files/${fileId}/tables/${currentTable.table_index}/columns/bulk-delete`, {
        column_indices: Array.from(selectedColumns).sort((a, b) => b - a), // Sort descending
      });
      
      toast.success(`${selectedColumns.size} columns deleted successfully`);
      setSelectedColumns(new Set());
      setSelectionMode('none');
      loadTables();
    } catch (error: any) {
      console.error('Error deleting columns:', error);
      toast.error('Failed to delete selected columns');
    } finally {
      setSaving(false);
    }
  };

  const clearSelection = () => {
    setSelectedRows(new Set());
    setSelectedColumns(new Set());
    setSelectionMode('none');
  };

  const handleCloseDialog = () => {
    if (hasUnsavedChanges) {
      setConfirmDialog({
        open: true,
        title: 'Unsaved Changes',
        message: `You have ${pendingChanges.size} unsaved change${pendingChanges.size > 1 ? 's' : ''}. Are you sure you want to close without saving? Your changes will be lost.`,
        severity: 'warning',
        confirmText: 'Close Without Saving',
        onConfirm: () => {
          setPendingChanges(new Map());
          setHasUnsavedChanges(false);
          clearSelection();
          setConfirmDialog({ ...confirmDialog, open: false });
          onClose();
        }
      });
    } else {
      clearSelection();
      onClose();
    }
  };

  const filterTableData = (table: TableData) => {
    if (!searchTerm) return table.data;
    
    return table.data.filter(row => 
      row.some(cell => 
        cell.toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  };

  const currentTable = tables[activeTab];
  const filteredData = currentTable ? filterTableData(currentTable) : [];

  return (
    <Dialog
      open={open}
      onClose={handleCloseDialog}
      maxWidth="xl"
      fullWidth
      PaperProps={{
        sx: { height: '90vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Edit Tables - {filename}
          </Typography>
          <IconButton onClick={handleCloseDialog}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Table Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
              <Tabs
                value={activeTab}
                onChange={handleTabChange}
                variant="scrollable"
                scrollButtons="auto"
              >
                {tables.map((table, index) => (
                  <Tab
                    key={table.table_index}
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {editingTableName === table.table_index ? (
                          <TextField
                            value={newTableName}
                            onChange={(e) => setNewTableName(e.target.value)}
                            onBlur={() => handleSaveTableName(table.table_index, newTableName)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                handleSaveTableName(table.table_index, newTableName);
                              }
                            }}
                            size="small"
                            sx={{ minWidth: 100 }}
                          />
                        ) : (
                          <>
                            <span>{table.table_name}</span>
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                setEditingTableName(table.table_index);
                                setNewTableName(table.table_name);
                              }}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </>
                        )}
                        {table.has_changes && (
                          <Chip
                            label="Modified"
                            size="small"
                            color="warning"
                            sx={{ height: 16, fontSize: 10 }}
                          />
                        )}
                      </Box>
                    }
                  />
                ))}
              </Tabs>
            </Box>

            {/* Table Content */}
            {currentTable && (
              <Box sx={{ p: 2, height: 'calc(100% - 64px)' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    {currentTable.table_name}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {/* Save/Discard buttons for unsaved changes */}
                    {hasUnsavedChanges && (
                      <>
                        <Tooltip title={`Save ${pendingChanges.size} pending change${pendingChanges.size > 1 ? 's' : ''}`}>
                          <Button
                            onClick={handleSaveAllChanges}
                            color="success"
                            variant="contained"
                            disabled={saving}
                            startIcon={saving ? <CircularProgress size={16} /> : <SaveIcon />}
                            size="small"
                          >
                            Save ({pendingChanges.size})
                          </Button>
                        </Tooltip>
                        <Tooltip title="Discard all unsaved changes">
                          <Button
                            onClick={handleDiscardChanges}
                            color="warning"
                            variant="outlined"
                            disabled={saving}
                            startIcon={<WarningIcon />}
                            size="small"
                          >
                            Discard
                          </Button>
                        </Tooltip>
                      </>
                    )}
                    
                    <Tooltip title="Add Row">
                      <IconButton
                        onClick={() => handleAddRow(currentTable.table_index)}
                        color="primary"
                        disabled={saving || hasUnsavedChanges}
                      >
                        <AddIcon />
                      </IconButton>
                    </Tooltip>
                    
                    {/* Selection Mode Buttons */}
                    <Tooltip title="Select Rows">
                      <IconButton
                        onClick={() => setSelectionMode(selectionMode === 'rows' ? 'none' : 'rows')}
                        color={selectionMode === 'rows' ? 'primary' : 'default'}
                        disabled={saving}
                      >
                        <CheckBoxOutlineBlank />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Select Columns">
                      <IconButton
                        onClick={() => setSelectionMode(selectionMode === 'columns' ? 'none' : 'columns')}
                        color={selectionMode === 'columns' ? 'primary' : 'default'}
                        disabled={saving}
                      >
                        <SelectAllIcon />
                      </IconButton>
                    </Tooltip>
                    
                    {/* Bulk Actions */}
                    {(selectedRows.size > 0 || selectedColumns.size > 0) && (
                      <>
                        <Tooltip title="Clear Selection">
                          <IconButton
                            onClick={clearSelection}
                            color="default"
                            disabled={saving}
                          >
                            <ClearIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Selected">
                          <IconButton
                            onClick={selectedRows.size > 0 ? handleBulkDeleteRows : handleBulkDeleteColumns}
                            color="error"
                            disabled={saving}
                          >
                            <BulkDeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </>
                    )}
                    
                    <Tooltip title={hasUnsavedChanges ? "Save changes first" : "Undo Last Change"}>
                      <IconButton
                        onClick={() => handleUndoLastChange(currentTable.table_index)}
                        color="warning"
                        disabled={saving || hasUnsavedChanges}
                      >
                        <UndoIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={hasUnsavedChanges ? "Save changes first" : "Reset to Original"}>
                      <IconButton
                        onClick={() => handleResetTable(currentTable.table_index)}
                        color="error"
                        disabled={saving || hasUnsavedChanges}
                      >
                        <RestoreIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Refresh">
                      <IconButton 
                        onClick={loadTables}
                        disabled={saving}
                      >
                        <RefreshIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>

                <Alert severity={hasUnsavedChanges ? "warning" : "info"} sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    {hasUnsavedChanges ? (
                      <>
                        <strong>You have {pendingChanges.size} unsaved change{pendingChanges.size > 1 ? 's' : ''}.</strong> Click "Save" to apply changes or "Discard" to cancel.
                      </>
                    ) : (
                      'Click on any cell to edit. Make your changes and click "Save" to apply them.'
                    )}
                    <br />
                    Rows: {currentTable.rows_count} | Columns: {currentTable.columns_count}
                    {selectionMode === 'rows' && ` | Row Selection Mode: ${selectedRows.size} selected`}
                    {selectionMode === 'columns' && ` | Column Selection Mode: ${selectedColumns.size} selected`}
                  </Typography>
                </Alert>

                {/* Selection Controls */}
                {selectionMode === 'rows' && (
                  <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={selectedRows.size === filterTableData(currentTable).length && selectedRows.size > 0}
                          indeterminate={selectedRows.size > 0 && selectedRows.size < filterTableData(currentTable).length}
                          onChange={handleSelectAllRows}
                        />
                      }
                      label={`Select All Rows (${selectedRows.size}/${filterTableData(currentTable).length})`}
                    />
                  </Box>
                )}

                {selectionMode === 'columns' && (
                  <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={selectedColumns.size === currentTable.headers.length && selectedColumns.size > 0}
                          indeterminate={selectedColumns.size > 0 && selectedColumns.size < currentTable.headers.length}
                          onChange={handleSelectAllColumns}
                        />
                      }
                      label={`Select All Columns (${selectedColumns.size}/${currentTable.headers.length})`}
                    />
                  </Box>
                )}

                {/* Search Box */}
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Search table data..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mb: 2 }}
                />

                {/* Table */}
                <TableContainer 
                  component={Paper} 
                  sx={{ 
                    maxHeight: 'calc(100vh - 400px)', 
                    overflowY: 'auto',
                    overflowX: 'auto',
                    border: '1px solid #e0e0e0'
                  }}
                >
                  <Table stickyHeader size="small">
                    <TableHead>
                      <TableRow>
                        {/* Row selection header */}
                        {selectionMode === 'rows' && (
                          <TableCell 
                            sx={{ 
                              backgroundColor: 'primary.main',
                              color: 'primary.contrastText',
                              fontWeight: 'bold',
                              width: 60
                            }}
                          >
                            <Checkbox
                              checked={selectedRows.size === filterTableData(currentTable).length && selectedRows.size > 0}
                              indeterminate={selectedRows.size > 0 && selectedRows.size < filterTableData(currentTable).length}
                              onChange={handleSelectAllRows}
                              sx={{ color: 'primary.contrastText' }}
                            />
                          </TableCell>
                        )}

                        {currentTable.headers.map((header, colIndex) => (
                          <TableCell 
                            key={colIndex}
                            sx={{ 
                              backgroundColor: selectionMode === 'columns' && selectedColumns.has(colIndex) ? 'warning.main' : 'primary.main',
                              color: 'primary.contrastText',
                              fontWeight: 'bold',
                              minWidth: 120,
                              cursor: selectionMode === 'columns' ? 'pointer' : 'default'
                            }}
                            onClick={() => selectionMode === 'columns' && handleColumnSelection(colIndex)}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {selectionMode === 'columns' && (
                                <Checkbox
                                  checked={selectedColumns.has(colIndex)}
                                  onChange={() => handleColumnSelection(colIndex)}
                                  sx={{ color: 'primary.contrastText' }}
                                />
                              )}
                              {header}
                            </Box>
                          </TableCell>
                        ))}
                        <TableCell 
                          sx={{ 
                            backgroundColor: 'primary.main',
                            color: 'primary.contrastText',
                            fontWeight: 'bold',
                            width: 80
                          }}
                        >
                          Actions
                        </TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {filteredData.map((row, filteredRowIndex) => {
                        // Find the real row index in the original data
                        const realRowIndex = currentTable.data.findIndex(originalRow => 
                          JSON.stringify(originalRow) === JSON.stringify(row)
                        );
                        return (
                        <TableRow 
                          key={filteredRowIndex} 
                          hover 
                          sx={{
                            backgroundColor: selectionMode === 'rows' && selectedRows.has(filteredRowIndex) ? 'action.selected' : 'inherit'
                          }}
                        >
                          {/* Row selection checkbox */}
                          {selectionMode === 'rows' && (
                            <TableCell sx={{ width: 60 }}>
                              <Checkbox
                                checked={selectedRows.has(filteredRowIndex)}
                                onChange={() => handleRowSelection(filteredRowIndex)}
                              />
                            </TableCell>
                          )}

                          {row.map((cell, colIndex) => (
                            <TableCell 
                              key={colIndex}
                              onClick={() => selectionMode !== 'columns' && handleCellClick(currentTable.table_index, realRowIndex, colIndex, cell)}
                              sx={{ 
                                cursor: selectionMode === 'columns' ? 'default' : 'pointer',
                                backgroundColor: selectionMode === 'columns' && selectedColumns.has(colIndex) ? 'action.selected' : 'inherit',
                                '&:hover': {
                                  backgroundColor: selectionMode === 'columns' ? 'inherit' : 'action.hover'
                                },
                                border: '1px solid #e0e0e0',
                                position: 'relative'
                              }}
                            >
                              {editingCell && 
                               editingCell.tableIndex === currentTable.table_index &&
                               editingCell.rowIndex === realRowIndex && 
                               editingCell.colIndex === colIndex ? (
                                <TextField
                                  value={cellValue}
                                  onChange={(e) => setCellValue(e.target.value)}
                                  onBlur={handleCellSave}
                                  onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                      handleCellSave();
                                    } else if (e.key === 'Escape') {
                                      handleCellCancel();
                                    }
                                  }}
                                  autoFocus
                                  size="small"
                                  fullWidth
                                  variant="standard"
                                />
                              ) : (
                                <Typography variant="body2" noWrap>
                                  {cell || '-'}
                                </Typography>
                              )}
                            </TableCell>
                          ))}
                          <TableCell>
                            <Tooltip title="Delete Row">
                              <IconButton
                                size="small"
                                onClick={() => handleDeleteRow(currentTable.table_index, realRowIndex)}
                                color="error"
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleCloseDialog} disabled={saving}>
          {hasUnsavedChanges ? 'Close' : 'Cancel'}
        </Button>
        <Tooltip title={hasUnsavedChanges ? "Save changes first before exporting" : ""}>
          <span>
            <Button
              onClick={() => handleExport('csv')}
              disabled={saving || hasUnsavedChanges}
              startIcon={saving ? <CircularProgress size={16} /> : <DownloadIcon />}
            >
              Export CSV
            </Button>
          </span>
        </Tooltip>
        <Tooltip title={hasUnsavedChanges ? "Save changes first before exporting" : ""}>
          <span>
            <Button
              onClick={() => handleExport('excel')}
              disabled={saving || hasUnsavedChanges}
              startIcon={saving ? <CircularProgress size={16} /> : <DownloadIcon />}
              variant="contained"
            >
              Export Excel
            </Button>
          </span>
        </Tooltip>
      </DialogActions>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ ...confirmDialog, open: false })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {confirmDialog.severity === 'error' ? (
            <WarningIcon color="error" />
          ) : (
            <WarningIcon color="warning" />
          )}
          {confirmDialog.title}
        </DialogTitle>
        <DialogContent>
          <Typography>
            {confirmDialog.message}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setConfirmDialog({ ...confirmDialog, open: false })}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button
            onClick={confirmDialog.onConfirm}
            color={confirmDialog.severity === 'error' ? 'error' : 'warning'}
            variant="contained"
            disabled={saving}
            startIcon={saving ? <CircularProgress size={16} /> : undefined}
          >
            {confirmDialog.confirmText || 'Confirm'}
          </Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};

export default TableEditor;