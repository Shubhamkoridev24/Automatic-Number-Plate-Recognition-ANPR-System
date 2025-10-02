from rest_framework import serializers
from .models import Detection
from anpr_cameras.serializers import CameraSerializer

class DetectionSerializer(serializers.ModelSerializer):
    """Serializer for Detection model"""
    camera_details = CameraSerializer(source='camera', read_only=True)
    
    class Meta:
        model = Detection
        fields = ['id', 'plate_number', 'timestamp', 'camera', 'camera_details',
                  'image_path', 'video_path', 'confidence', 'blacklist_flag']
        read_only_fields = ['blacklist_flag']