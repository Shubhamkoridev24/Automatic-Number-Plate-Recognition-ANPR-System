"""
Management command to check the status of the ANPR detection service
"""
import logging
from django.core.management.base import BaseCommand
from anpr_cameras.models import Camera
from anpr_detection.stream_processor import StreamManager

logger = logging.getLogger('anpr_detection')

class Command(BaseCommand):
    help = 'Check status of ANPR detection service for all cameras'
    
    def handle(self, *args, **options):
        stream_manager = StreamManager()
        all_cameras = Camera.objects.all()
        
        if not all_cameras:
            self.stdout.write(self.style.WARNING("No cameras found in the system"))
            return
            
        # Print header
        self.stdout.write("\nANPR Detection Service Status")
        self.stdout.write("=" * 50)
        self.stdout.write(f"{'ID':<5} {'Name':<20} {'Location':<20} {'Active':<10} {'Status':<10}")
        self.stdout.write("-" * 50)
        
        # Print status for each camera
        for camera in all_cameras:
            is_running = camera.id in stream_manager.streams and stream_manager.streams[camera.id].is_running
            status = "RUNNING" if is_running else "STOPPED"
            status_style = self.style.SUCCESS if is_running else self.style.ERROR
            
            self.stdout.write(
                f"{camera.id:<5} {camera.name:<20} {camera.location:<20} "
                f"{'Yes' if camera.is_active else 'No':<10} {status_style(status):<10}"
            )
            
        # Summary
        running_count = sum(1 for camera in all_cameras if camera.id in stream_manager.streams and stream_manager.streams[camera.id].is_running)
        self.stdout.write("-" * 50)
        self.stdout.write(f"Summary: {running_count}/{all_cameras.count()} cameras running")