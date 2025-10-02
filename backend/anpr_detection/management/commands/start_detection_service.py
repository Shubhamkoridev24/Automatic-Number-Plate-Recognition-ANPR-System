"""
Management command to start the ANPR detection service
"""
import time
import logging
from django.core.management.base import BaseCommand
from anpr_cameras.models import Camera
from anpr_detection.stream_processor import StreamManager

logger = logging.getLogger('anpr_detection')

class Command(BaseCommand):
    help = 'Start ANPR detection service for all active cameras'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--camera-id',
            type=int,
            help='ID of specific camera to start (if not provided, starts all active cameras)'
        )
        
    def handle(self, *args, **options):
        stream_manager = StreamManager()
        camera_id = options.get('camera_id')
        
        if camera_id:
            try:
                camera = Camera.objects.get(id=camera_id)
                if not camera.is_active:
                    self.stdout.write(self.style.WARNING(f"Camera {camera.name} is not active"))
                    return
                    
                self.stdout.write(f"Starting detection service for camera: {camera.name}")
                success = stream_manager.start_stream(camera)
                
                if success:
                    self.stdout.write(self.style.SUCCESS(f"Successfully started detection for camera: {camera.name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to start detection for camera: {camera.name}"))
            except Camera.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Camera with ID {camera_id} does not exist"))
        else:
            # Start for all active cameras
            active_cameras = Camera.objects.filter(is_active=True)
            
            if not active_cameras:
                self.stdout.write(self.style.WARNING("No active cameras found"))
                return
                
            self.stdout.write(f"Starting detection service for {active_cameras.count()} active cameras")
            
            for camera in active_cameras:
                self.stdout.write(f"Starting detection for camera: {camera.name}")
                success = stream_manager.start_stream(camera)
                
                if success:
                    self.stdout.write(self.style.SUCCESS(f"Successfully started detection for camera: {camera.name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to start detection for camera: {camera.name}"))
                    
            self.stdout.write(self.style.SUCCESS("ANPR detection service started"))