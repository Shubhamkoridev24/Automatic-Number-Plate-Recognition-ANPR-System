import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { detectionAPI, Detection } from '../services/api';

const Detections: React.FC = () => {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => {
    fetchDetections();
  }, []);

  const fetchDetections = async () => {
    try {
      setLoading(true);
      const params: any = {};
      
      if (searchTerm) {
        params.plate_number = searchTerm;
      }
      
      if (filterStatus !== 'all') {
        params.blacklist_flag = filterStatus === 'blacklisted';
      }
      
      if (dateFrom) {
        params.date_from = dateFrom;
      }
      
      if (dateTo) {
        params.date_to = dateTo;
      }

      const response = await detectionAPI.getAll(params);
      setDetections(response.data);
    } catch (error) {
      console.error('Error fetching detections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    fetchDetections();
  };

  const handleReset = () => {
    setSearchTerm('');
    setFilterStatus('all');
    setDateFrom('');
    setDateTo('');
    fetchDetections();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading detections...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        License Plate Detections
      </Typography>

      {/* Search and Filter Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Search License Plate"
                variant="outlined"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSearch();
                  }
                }}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  label="Status"
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="normal">Normal</MenuItem>
                  <MenuItem value="blacklisted">Blacklisted</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                label="From Date"
                type="date"
                variant="outlined"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                label="To Date"
                type="date"
                variant="outlined"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={1}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleSearch}
                startIcon={<FilterIcon />}
              >
                Filter
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={handleReset}
              >
                Reset
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Detections Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Detection Results ({detections.length} found)
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>License Plate</TableCell>
                  <TableCell>Camera</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {detections.map((detection) => (
                  <TableRow key={detection.id}>
                    <TableCell>{detection.id}</TableCell>
                    <TableCell>
                      <Typography variant="body1" fontWeight="bold">
                        {detection.plate_number}
                      </Typography>
                    </TableCell>
                    <TableCell>Camera {detection.camera}</TableCell>
                    <TableCell>
                      <Chip
                        label={`${(detection.confidence * 100).toFixed(1)}%`}
                        color={detection.confidence > 0.8 ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(detection.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={detection.is_blacklisted ? 'Blacklisted' : 'Normal'}
                        color={detection.is_blacklisted ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          {detections.length === 0 && (
            <Box textAlign="center" py={4}>
              <Typography color="textSecondary">
                No detections found matching your criteria.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Detections;