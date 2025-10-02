import React, { useState, useEffect } from 'react';
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
  Paper,
  Chip,
  Button,
  IconButton,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { alertAPI, Alert } from '../services/api';

const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const params: any = {};
      
      if (filterStatus === 'active') {
        params.is_resolved = false;
      } else if (filterStatus === 'resolved') {
        params.is_resolved = true;
      }

      const response = await alertAPI.getAll(params);
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResolveAlert = async (id: number) => {
    try {
      await alertAPI.resolve(id);
      fetchAlerts();
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  const handleFilterChange = (status: string) => {
    setFilterStatus(status);
    fetchAlerts();
  };

  const getAlertSeverity = (alert: Alert) => {
    // You can implement logic to determine severity based on various factors
    return 'high'; // For now, all blacklist alerts are high severity
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading alerts...</Typography>
      </Box>
    );
  }

  const activeAlerts = alerts.filter(alert => !alert.is_resolved);
  const resolvedAlerts = alerts.filter(alert => alert.is_resolved);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Security Alerts</Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchAlerts}
        >
          Refresh
        </Button>
      </Box>

      {/* Alert Statistics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Alerts
                  </Typography>
                  <Typography variant="h4" component="div" color="error">
                    {activeAlerts.length}
                  </Typography>
                </Box>
                <WarningIcon sx={{ fontSize: 40, color: 'error.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Resolved Alerts
                  </Typography>
                  <Typography variant="h4" component="div" color="success.main">
                    {resolvedAlerts.length}
                  </Typography>
                </Box>
                <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Alerts
                  </Typography>
                  <Typography variant="h4" component="div">
                    {alerts.length}
                  </Typography>
                </Box>
                <WarningIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filter Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Filter by Status</InputLabel>
                <Select
                  value={filterStatus}
                  label="Filter by Status"
                  onChange={(e) => handleFilterChange(e.target.value)}
                >
                  <MenuItem value="all">All Alerts</MenuItem>
                  <MenuItem value="active">Active Only</MenuItem>
                  <MenuItem value="resolved">Resolved Only</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Alerts Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Alert History ({alerts.length} total)
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Detection ID</TableCell>
                  <TableCell>Blacklist Entry</TableCell>
                  <TableCell>Severity</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {alerts.map((alert) => {
                  const severity = getAlertSeverity(alert);
                  return (
                    <TableRow key={alert.id}>
                      <TableCell>{alert.id}</TableCell>
                      <TableCell>#{alert.detection}</TableCell>
                      <TableCell>#{alert.blacklist_entry}</TableCell>
                      <TableCell>
                        <Chip
                          label={severity.toUpperCase()}
                          color={getSeverityColor(severity) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(alert.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={alert.is_resolved ? 'Resolved' : 'Active'}
                          color={alert.is_resolved ? 'success' : 'error'}
                          size="small"
                          icon={alert.is_resolved ? <CheckCircleIcon /> : <WarningIcon />}
                        />
                      </TableCell>
                      <TableCell>
                        {!alert.is_resolved && (
                          <Button
                            size="small"
                            variant="contained"
                            color="success"
                            onClick={() => handleResolveAlert(alert.id)}
                            startIcon={<CheckCircleIcon />}
                          >
                            Resolve
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
          {alerts.length === 0 && (
            <Box textAlign="center" py={4}>
              <Typography color="textSecondary">
                No alerts found.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Alerts;