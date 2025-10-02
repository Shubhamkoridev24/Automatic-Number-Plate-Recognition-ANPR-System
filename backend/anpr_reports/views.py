from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
import csv
import os
from django.http import HttpResponse
from .models import Report
from .serializers import ReportSerializer
from anpr_detection.models import Detection
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Report instances"""
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    
    @action(detail=False, methods=['get'])
    def generate_csv(self, request):
        """Generate a CSV report of detections"""
        # Get query parameters
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        report_type = request.query_params.get('report_type', 'daily')
        
        # Set default dates if not provided
        if not end_date:
            end_date = timezone.now()
        else:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
            
        if not start_date:
            if report_type == 'daily':
                start_date = end_date - timedelta(days=1)
            elif report_type == 'weekly':
                start_date = end_date - timedelta(days=7)
            elif report_type == 'monthly':
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=1)
        else:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
        
        # Query detections
        detections = Detection.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).order_by('-timestamp')
        
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        writer.writerow(['Plate Number', 'Timestamp', 'Camera', 'Location', 'Blacklisted'])
        
        # Add detection data
        for detection in detections:
            writer.writerow([
                detection.plate_number,
                detection.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                detection.camera.name,
                detection.camera.location,
                'Yes' if detection.blacklist_flag else 'No'
            ])
        
        # Log report generation
        logger.info(f"Generated {report_type} CSV report from {start_date} to {end_date}")
        
        # Create report record in database
        title = f"{report_type.capitalize()} Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        Report.objects.create(
            title=title,
            description=f"Auto-generated {report_type} report",
            report_type=report_type,
            format_type='csv',
            start_date=start_date.date(),
            end_date=end_date.date(),
            generated_by=request.user.username if request.user.is_authenticated else 'API'
        )
        
        return response
