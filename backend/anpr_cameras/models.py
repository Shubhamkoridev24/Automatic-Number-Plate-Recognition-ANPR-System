from django.db import models
import logging

logger = logging.getLogger(__name__)

class Camera(models.Model):
    """Model for storing camera information"""
    name = models.CharField(max_length=100)
    rtsp_url = models.CharField(max_length=255)
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.location})"
    
    def save(self, *args, **kwargs):
        # Log when a camera is added or updated
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f"New camera added: {self.name} at {self.location}")
        else:
            logger.info(f"Camera updated: {self.name}")
    
    def start_stream(self):
        """Start the camera stream - placeholder for actual implementation"""
        # This would actually connect to the camera and start streaming
        # For now just logging the attempt
        logger.info(f"Starting stream for camera: {self.name}")
        return True
    
    def stop_stream(self):
        """Stop the camera stream - placeholder for actual implementation"""
        # This would actually disconnect from the camera
        # For now just logging the attempt
        logger.info(f"Stopping stream for camera: {self.name}")
        return True
