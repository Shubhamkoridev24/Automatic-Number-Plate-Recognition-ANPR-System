from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model"""
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    format_type_display = serializers.CharField(source='get_format_type_display', read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'title', 'description', 'report_type', 'report_type_display',
                  'format_type', 'format_type_display', 'file_path', 'created_at',
                  'start_date', 'end_date', 'generated_by']
        read_only_fields = ['created_at', 'file_path']