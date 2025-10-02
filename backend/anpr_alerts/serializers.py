from rest_framework import serializers
from .models import Blacklist, Alert

class BlacklistSerializer(serializers.ModelSerializer):
    """Serializer for Blacklist model"""
    
    class Meta:
        model = Blacklist
        fields = ['id', 'plate_number', 'reason', 'added_at', 'is_active']
        read_only_fields = ['added_at']


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model"""
    plate_number = serializers.CharField(source='blacklist_entry.plate_number', read_only=True)
    reason = serializers.CharField(source='blacklist_entry.reason', read_only=True)
    camera_name = serializers.CharField(source='detection.camera.name', read_only=True)
    camera_location = serializers.CharField(source='detection.camera.location', read_only=True)
    
    class Meta:
        model = Alert
        fields = ['id', 'plate_number', 'reason', 'timestamp', 'notified', 
                  'camera_name', 'camera_location', 'detection', 'blacklist_entry']
        read_only_fields = ['timestamp', 'notified', 'detection', 'blacklist_entry']