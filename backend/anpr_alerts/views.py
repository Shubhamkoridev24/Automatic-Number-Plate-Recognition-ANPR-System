from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
from .models import Blacklist, Alert
from .serializers import BlacklistSerializer, AlertSerializer

logger = logging.getLogger(__name__)

class BlacklistViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Blacklist instances"""
    queryset = Blacklist.objects.all()
    serializer_class = BlacklistSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['plate_number']
    
    def perform_create(self, serializer):
        logger.info(f"Adding plate to blacklist: {serializer.validated_data.get('plate_number')}")
        serializer.save()
    
    def perform_update(self, serializer):
        logger.info(f"Updating blacklist entry: {serializer.instance.plate_number}")
        serializer.save()
    
    def perform_destroy(self, instance):
        logger.info(f"Removing plate from blacklist: {instance.plate_number}")
        instance.delete()


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing Alert instances (read-only)"""
    queryset = Alert.objects.all().order_by('-timestamp')
    serializer_class = AlertSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['blacklist_entry__plate_number']
    
    @action(detail=True, methods=['post'])
    def mark_as_notified(self, request, pk=None):
        """Mark an alert as notified"""
        alert = self.get_object()
        alert.notified = True
        alert.save()
        return Response({'status': 'alert marked as notified'})
