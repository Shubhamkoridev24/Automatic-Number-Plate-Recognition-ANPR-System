from django.db import models
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

class Blacklist(models.Model):
    """Model for storing blacklisted license plates"""
    plate_number = models.CharField(max_length=20, unique=True)
    reason = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.plate_number} - {self.reason[:30]}"
    
    def save(self, *args, **kwargs):
        # Log when a plate is added to blacklist
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f"New plate added to blacklist: {self.plate_number}, Reason: {self.reason}")
        else:
            logger.info(f"Blacklist entry updated: {self.plate_number}")
            
    class Meta:
        verbose_name = "Blacklisted Plate"
        verbose_name_plural = "Blacklisted Plates"


class Alert(models.Model):
    """Model for storing alerts when blacklisted plates are detected"""
    detection = models.ForeignKey('anpr_detection.Detection', on_delete=models.CASCADE)
    blacklist_entry = models.ForeignKey(Blacklist, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Alert: {self.blacklist_entry.plate_number} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        # Log and send email when a new alert is created
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.warning(f"ALERT: Blacklisted plate detected - {self.blacklist_entry.plate_number}")
            self.send_notification()
    
    def send_notification(self):
        """Send email notification about the alert"""
        try:
            # In a real system, you'd send to security personnel or admins
            # For now, just log it
            subject = f"ANPR Alert: Blacklisted plate {self.blacklist_entry.plate_number} detected"
            message = f"""
            Alert Details:
            - Plate Number: {self.blacklist_entry.plate_number}
            - Reason for Blacklisting: {self.blacklist_entry.reason}
            - Detection Time: {self.timestamp}
            - Camera: {self.detection.camera.name}
            - Location: {self.detection.camera.location}
            """
            
            # Uncomment in production with real email addresses
            # from_email = settings.DEFAULT_FROM_EMAIL
            # recipient_list = ['security@example.com']
            # send_mail(subject, message, from_email, recipient_list)
            
            logger.info(f"Alert notification sent for plate {self.blacklist_entry.plate_number}")
            self.notified = True
            self.save(update_fields=['notified'])
        except Exception as e:
            logger.error(f"Failed to send alert notification: {str(e)}")
