from rest_framework import serializers
from .models import Camera

class CameraSerializer(serializers.ModelSerializer):
    """Serializer for Camera model"""
    
    class Meta:
        model = Camera
        fields = ['id', 'name', 'rtsp_url', 'location', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']