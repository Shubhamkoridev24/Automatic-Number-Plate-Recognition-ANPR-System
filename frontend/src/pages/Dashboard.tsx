import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Videocam as VideocamIcon,
  Search as SearchIcon,
  Warning as WarningIcon,
  Block as BlockIcon,
} from '@mui/icons-material';
import { detectionAPI, cameraAPI, alertAPI, Detection, Camera, Alert } from '../services/api';

interface StatCard {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    totalCameras: 0,
    totalDetections: 0,
    activeAlerts: 0,
    blacklistedDetections: 0,
  });
  const [recentDetections, setRecentDetections] = useState<Detection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch cameras
      const camerasResponse = await cameraAPI.getAll();
      const cameras = camerasResponse.data;
      
      // Fetch recent detections
      const detectionsResponse = await detectionAPI.getAll({ limit: 10 });
      const detections = detectionsResponse.data;
      
      // Fetch alerts
      const alertsResponse = await alertAPI.getAll({ is_resolved: false });
      const alerts = alertsResponse.data;
      
      // Calculate stats
      const blacklistedCount = detections.filter(d => d.is_blacklisted).length;
      
      setStats({
        totalCameras: cameras.length,
        totalDetections: detections.length,
        activeAlerts: alerts.length,
        blacklistedDetections: blacklistedCount,
      });
      
      setRecentDetections(detections.slice(0, 5));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards: StatCard[] = [
    {
      title: 'Total Cameras',
      value: stats.totalCameras,
      icon: <VideocamIcon sx={{ fontSize: 40 }} />,
      color: '#1976d2',
    },
    {
      title: 'Total Detections',
      value: stats.totalDetections,
      icon: <SearchIcon sx={{ fontSize: 40 }} />,
      color: '#2e7d32',
    },
    {
      title: 'Active Alerts',
      value: stats.activeAlerts,
      icon: <WarningIcon sx={{ fontSize: 40 }} />,
      color: '#ed6c02',
    },
    {
      title: 'Blacklisted Detections',
      value: stats.blacklistedDetections,
      icon: <BlockIcon sx={{ fontSize: 40 }} />,
      color: '#d32f2f',
    },
  ];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statCards.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" component="div">
                      {stat.value}
                    </Typography>
                  </Box>
                  <Box sx={{ color: stat.color }}>
                    {stat.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Recent Detections */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Detections
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>License Plate</TableCell>
                  <TableCell>Camera</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentDetections.map((detection) => (
                  <TableRow key={detection.id}>
                    <TableCell>{detection.license_plate}</TableCell>
                    <TableCell>Camera {detection.camera}</TableCell>
                    <TableCell>{(detection.confidence * 100).toFixed(1)}%</TableCell>
                    <TableCell>
                      {new Date(detection.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Typography
                        color={detection.is_blacklisted ? 'error' : 'success'}
                        variant="body2"
                      >
                        {detection.is_blacklisted ? 'Blacklisted' : 'Normal'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;