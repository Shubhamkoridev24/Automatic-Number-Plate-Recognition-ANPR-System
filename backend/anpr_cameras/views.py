"""Views for ANPR cameras API"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
import cv2
import base64
from .models import Camera
from .serializers import CameraSerializer
from anpr_detection.stream_processor import StreamManager

logger = logging.getLogger('anpr_cameras')

class CameraViewSet(viewsets.ModelViewSet):
    """API endpoint for cameras"""
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    
    def perform_create(self, serializer):
        logger.info(f"Creating new camera: {serializer.validated_data.get('name')}")
        serializer.save()
    
    def perform_update(self, serializer):
        logger.info(f"Updating camera {serializer.instance.id}: {serializer.instance.name}")
        serializer.save()
    
    def perform_destroy(self, instance):
        logger.info(f"Deleting camera {instance.id}: {instance.name}")
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def start_stream(self, request, pk=None):
        """Start streaming from a camera"""
        camera = self.get_object()
        logger.info(f"Starting stream for camera: {camera.name}")
        
        # Start stream using StreamManager
        stream_manager = StreamManager()
        success = stream_manager.start_stream(camera)
        
        if success:
            return Response({'status': 'stream started'})
        return Response({'status': 'failed to start stream'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def stop_stream(self, request, pk=None):
        """Stop streaming from a camera"""
        camera = self.get_object()
        logger.info(f"Stopping stream for camera: {camera.name}")
        
        # Stop stream using StreamManager
        stream_manager = StreamManager()
        success = stream_manager.stop_stream(camera.id)
        
        if success:
            return Response({'status': 'stream stopped'})
        return Response({'status': 'failed to stop stream'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def stream_frame(self, request, pk=None):
        """Get the latest frame from camera stream"""
        camera = self.get_object()
        
        # Get latest frame from StreamManager
        stream_manager = StreamManager()
        frame = stream_manager.get_stream_frame(camera.id)
        
        if frame is not None:
            # Convert frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Return as image response
            return HttpResponse(frame_bytes, content_type='image/jpeg')
        else:
            return JsonResponse({'error': 'No frame available'}, status=404)
    
    @action(detail=True, methods=['get'])
    def stream_status(self, request, pk=None):
        """Check if camera stream is active"""
        camera = self.get_object()
        
        # Check if stream is active
        stream_manager = StreamManager()
        is_active = camera.id in stream_manager.streams and stream_manager.streams[camera.id].is_running
        
        return Response({'active': is_active})
