"""
Views for ANPR detection API
"""
import os
import cv2
import logging
import base64
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, action, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Detection
from .serializers import DetectionSerializer
from .services import ANPRDetector

# Configure logger
logger = logging.getLogger('anpr_detection')

class DetectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for license plate detections
    """
    queryset = Detection.objects.all().order_by('-timestamp')
    serializer_class = DetectionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['plate_number', 'camera', 'is_blacklisted', 'processed']
    ordering_fields = ['timestamp', 'confidence']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent detections"""
        recent_detections = Detection.objects.all().order_by('-timestamp')[:10]
        serializer = self.get_serializer(recent_detections, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def blacklisted(self, request):
        """Get blacklisted detections"""
        blacklisted = Detection.objects.filter(blacklist_flag=True).order_by('-timestamp')
        serializer = self.get_serializer(blacklisted, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def process_image(request):
    """
    Process an uploaded image for license plate detection
    """
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)
    
    try:
        # Get image file
        image_file = request.FILES['image']
        
        # Read image
        image_bytes = image_file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return JsonResponse({'error': 'Invalid image format'}, status=400)
        
        # Get camera ID (optional)
        camera_id = request.data.get('camera_id', None)
        
        # Process image with ANPR detector
        detector = ANPRDetector()
        result_image, detections = detector.process_frame(image, camera_id)
        
        # Save detections if camera_id is provided
        saved_detections = []
        if camera_id:
            for detection_data in detections:
                detection_obj = detector.save_detection(detection_data, image)
                if detection_obj:
                    saved_detections.append({
                        'id': detection_obj.id,
                        'plate_number': detection_obj.plate_number,
                        'confidence': detection_obj.confidence,
                        'is_blacklisted': detection_obj.is_blacklisted
                    })
        
        # Encode result image to base64
        _, buffer = cv2.imencode('.jpg', result_image)
        result_image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # Return results
        return JsonResponse({
            'detections': [
                {
                    'plate_number': d['plate_number'],
                    'confidence': d['confidence'],
                    'box': d['box']
                } for d in detections
            ],
            'saved_detections': saved_detections,
            'result_image': result_image_b64
        })
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
