import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Paper,
  Chip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Block as BlockIcon,
} from '@mui/icons-material';
import { blacklistAPI, BlacklistEntry } from '../services/api';

const Blacklist: React.FC = () => {
  const [blacklistEntries, setBlacklistEntries] = useState<BlacklistEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState<BlacklistEntry | null>(null);
  const [formData, setFormData] = useState({
    license_plate: '',
    reason: '',
    is_active: true,
  });

  useEffect(() => {
    fetchBlacklistEntries();
  }, []);

  const fetchBlacklistEntries = async () => {
    try {
      setLoading(true);
      const response = await blacklistAPI.getAll();
      setBlacklistEntries(response.data);
    } catch (error) {
      console.error('Error fetching blacklist entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (entry?: BlacklistEntry) => {
    if (entry) {
      setEditingEntry(entry);
      setFormData({
        license_plate: entry.license_plate,
        reason: entry.reason,
        is_active: entry.is_active,
      });
    } else {
      setEditingEntry(null);
      setFormData({
        license_plate: '',
        reason: '',
        is_active: true,
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingEntry(null);
  };

  const handleSubmit = async () => {
    try {
      if (editingEntry) {
        await blacklistAPI.update(editingEntry.id, formData);
      } else {
        await blacklistAPI.create(formData);
      }
      fetchBlacklistEntries();
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving blacklist entry:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this blacklist entry?')) {
      try {
        await blacklistAPI.delete(id);
        fetchBlacklistEntries();
      } catch (error) {
        console.error('Error deleting blacklist entry:', error);
      }
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading blacklist...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Blacklist Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add to Blacklist
        </Button>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Blacklisted License Plates ({blacklistEntries.length})
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>License Plate</TableCell>
                  <TableCell>Reason</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {blacklistEntries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>{entry.id}</TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <BlockIcon sx={{ mr: 1, color: 'error.main' }} />
                        <Typography variant="body1" fontWeight="bold">
                          {entry.license_plate}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{entry.reason}</TableCell>
                    <TableCell>
                      <Chip
                        label={entry.is_active ? 'Active' : 'Inactive'}
                        color={entry.is_active ? 'error' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(entry.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleOpenDialog(entry)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton onClick={() => handleDelete(entry.id)} color="error">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          {blacklistEntries.length === 0 && (
            <Box textAlign="center" py={4}>
              <Typography color="textSecondary">
                No blacklisted license plates found.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingEntry ? 'Edit Blacklist Entry' : 'Add to Blacklist'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="License Plate"
            fullWidth
            variant="outlined"
            value={formData.license_plate}
            onChange={(e) => setFormData({ ...formData, license_plate: e.target.value.toUpperCase() })}
            sx={{ mb: 2 }}
            placeholder="e.g., ABC123"
          />
          <TextField
            margin="dense"
            label="Reason"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={formData.reason}
            onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
            sx={{ mb: 2 }}
            placeholder="Reason for blacklisting..."
          />
          <FormControlLabel
            control={
              <Switch
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
            }
            label="Active"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="error">
            {editingEntry ? 'Update' : 'Add to Blacklist'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Blacklist;