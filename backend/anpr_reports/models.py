from django.db import models
import uuid
import os
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

def get_report_path(instance, filename):
    """Generate path for report files"""
    ext = filename.split('.')[-1]
    filename = f"report_{instance.report_type}_{uuid.uuid4().hex}.{ext}"
    return os.path.join('reports', filename)

class Report(models.Model):
    """Model for storing generated reports"""
    REPORT_TYPES = (
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('custom', 'Custom Report'),
    )
    
    FORMAT_TYPES = (
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    format_type = models.CharField(max_length=10, choices=FORMAT_TYPES)
    file_path = models.FileField(upload_to=get_report_path, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_by = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f"New report created: {self.title} ({self.get_report_type_display()})")
    
    class Meta:
        ordering = ['-created_at']
