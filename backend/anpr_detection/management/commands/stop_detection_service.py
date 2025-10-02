"""
Management command to stop the ANPR detection service
"""
import logging
from django.core.management.base import BaseCommand
from anpr_cameras.models import Camera
from anpr_detection.stream_processor import StreamManager

logger = logging.getLogger('anpr_detection')

class Command(BaseCommand):
    help = 'Stop ANPR detection service for all or specific cameras'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--camera-id',
            type=int,
            help='ID of specific camera to stop (if not provided, stops all running cameras)'
        )
        
    def handle(self, *args, **options):
        stream_manager = StreamManager()
        camera_id = options.get('camera_id')
        
        if camera_id:
            try:
                camera = Camera.objects.get(id=camera_id)
                self.stdout.write(f"Stopping detection service for camera: {camera.name}")
                success = stream_manager.stop_stream(camera.id)
                
                if success:
                    self.stdout.write(self.style.SUCCESS(f"Successfully stopped detection for camera: {camera.name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to stop detection for camera: {camera.name} (not running)"))
            except Camera.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Camera with ID {camera_id} does not exist"))
        else:
            # Stop all running streams
            running_streams = list(stream_manager.streams.keys())
            
            if not running_streams:
                self.stdout.write(self.style.WARNING("No running detection services found"))
                return
                
            self.stdout.write(f"Stopping detection service for {len(running_streams)} cameras")
            
            for camera_id in running_streams:
                try:
                    camera = Camera.objects.get(id=camera_id)
                    camera_name = camera.name
                except Camera.DoesNotExist:
                    camera_name = f"Unknown (ID: {camera_id})"
                    
                self.stdout.write(f"Stopping detection for camera: {camera_name}")
                success = stream_manager.stop_stream(camera_id)
                
                if success:
                    self.stdout.write(self.style.SUCCESS(f"Successfully stopped detection for camera: {camera_name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to stop detection for camera: {camera_name}"))
                    
            self.stdout.write(self.style.SUCCESS("All ANPR detection services stopped"))