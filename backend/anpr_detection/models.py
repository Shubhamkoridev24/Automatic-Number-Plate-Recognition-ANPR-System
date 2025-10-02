from django.db import models
import os
import logging
import uuid
from django.utils import timezone
from anpr_cameras.models import Camera
from anpr_alerts.models import Blacklist

logger = logging.getLogger(__name__)

def get_image_path(instance, filename):
    """Generate path for detection images"""
    ext = filename.split('.')[-1]
    filename = f"{instance.plate_number}_{uuid.uuid4().hex}.{ext}"
    return os.path.join('images', filename)

def get_video_path(instance, filename):
    """Generate path for detection videos"""
    ext = filename.split('.')[-1]
    filename = f"{instance.plate_number}_{uuid.uuid4().hex}.{ext}"
    return os.path.join('videos', filename)

class Detection(models.Model):
    """Model for storing license plate detections"""
    plate_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='detections')
    image_path = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    video_path = models.FileField(upload_to=get_video_path, blank=True, null=True)
    confidence = models.FloatField(default=0.0)  # Confidence score of the detection
    blacklist_flag = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.plate_number} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def save(self, *args, **kwargs):
        # Check if plate is in blacklist
        try:
            # This could be optimized with caching in a real system
            blacklisted = Blacklist.objects.filter(
                plate_number=self.plate_number, 
                is_active=True
            ).exists()
            
            if blacklisted and not self.blacklist_flag:
                self.blacklist_flag = True
                logger.warning(f"Blacklisted plate detected: {self.plate_number}")
        except Exception as e:
            # Don't let blacklist check failure prevent saving the detection
            logger.error(f"Error checking blacklist for {self.plate_number}: {str(e)}")
        
        # Save the detection
        super().save(*args, **kwargs)
        
        # If blacklisted, create an alert (but avoid circular import)
        if self.blacklist_flag and not self.processed:
            try:
                # We import here to avoid circular import issues
                from anpr_alerts.models import Alert, Blacklist
                
                blacklist_entry = Blacklist.objects.get(plate_number=self.plate_number)
                Alert.objects.create(
                    detection=self,
                    blacklist_entry=blacklist_entry
                )
                self.processed = True
                self.save(update_fields=['processed'])
                
            except Exception as e:
                logger.error(f"Failed to create alert for blacklisted plate {self.plate_number}: {str(e)}")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['plate_number']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['blacklist_flag']),
        ]
