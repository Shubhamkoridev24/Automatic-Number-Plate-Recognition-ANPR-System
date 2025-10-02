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
  Grid,
  IconButton,
  TextField,
  Typography,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Videocam as VideocamIcon,
} from '@mui/icons-material';
import { cameraAPI, Camera } from '../services/api';

const Cameras: React.FC = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCamera, setEditingCamera] = useState<Camera | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    rtsp_url: '',
    is_active: true,
  });

  useEffect(() => {
    fetchCameras();
  }, []);

  const fetchCameras = async () => {
    try {
      setLoading(true);
      const response = await cameraAPI.getAll();
      setCameras(response.data);
    } catch (error) {
      console.error('Error fetching cameras:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (camera?: Camera) => {
    if (camera) {
      setEditingCamera(camera);
      setFormData({
        name: camera.name,
        location: camera.location,
        rtsp_url: camera.rtsp_url,
        is_active: camera.is_active,
      });
    } else {
      setEditingCamera(null);
      setFormData({
        name: '',
        location: '',
        rtsp_url: '',
        is_active: true,
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingCamera(null);
  };

  const handleSubmit = async () => {
    try {
      console.log("Submitting camera data:", formData);
      
      // Ensure RTSP URL has proper format
      let updatedFormData = {...formData};
      if (updatedFormData.rtsp_url && !updatedFormData.rtsp_url.startsWith('rtsp://') && !updatedFormData.rtsp_url.startsWith('http://') && !updatedFormData.rtsp_url.startsWith('https://')) {
        updatedFormData.rtsp_url = 'rtsp://' + updatedFormData.rtsp_url;
      }
      
      if (editingCamera) {
        await cameraAPI.update(editingCamera.id, updatedFormData);
      } else {
        const response = await fetch('http://127.0.0.1:8000/api/cameras/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updatedFormData)
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(JSON.stringify(errorData));
        }
      }
      fetchCameras();
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving camera:', error);
      alert('Error saving camera. Please check console for details.');
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this camera?')) {
      try {
        await cameraAPI.delete(id);
        fetchCameras();
      } catch (error) {
        console.error('Error deleting camera:', error);
      }
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading cameras...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Cameras</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Camera
        </Button>
      </Box>

      <Grid container spacing={3}>
        {cameras.map((camera) => (
          <Grid item xs={12} sm={6} md={4} key={camera.id}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <VideocamIcon sx={{ mr: 1, color: camera.is_active ? 'green' : 'gray' }} />
                  <Typography variant="h6">{camera.name}</Typography>
                </Box>
                <Typography color="textSecondary" gutterBottom>
                  Location: {camera.location}
                </Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  RTSP URL: {camera.rtsp_url}
                </Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  Status: {camera.is_active ? 'Active' : 'Inactive'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Created: {new Date(camera.created_at).toLocaleDateString()}
                </Typography>
                <Box display="flex" justifyContent="flex-end" mt={2}>
                  <IconButton onClick={() => handleOpenDialog(camera)}>
                    <EditIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDelete(camera.id)} color="error">
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingCamera ? 'Edit Camera' : 'Add New Camera'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Camera Name"
            fullWidth
            variant="outlined"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Location"
            fullWidth
            variant="outlined"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="RTSP URL"
            fullWidth
            variant="outlined"
            value={formData.rtsp_url}
            onChange={(e) => setFormData({ ...formData, rtsp_url: e.target.value })}
            sx={{ mb: 2 }}
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
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            color="primary"
          >
            {editingCamera ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Cameras;