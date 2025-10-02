from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import routers
from anpr_cameras.views import CameraViewSet
from anpr_alerts.views import BlacklistViewSet, AlertViewSet
from anpr_detection.views import DetectionViewSet
from anpr_reports.views import ReportViewSet

# Create a router and register our viewsets with it
router = routers.DefaultRouter()
router.register(r'cameras', CameraViewSet)
router.register(r'blacklist', BlacklistViewSet)
router.register(r'alerts', AlertViewSet)
router.register(r'detections', DetectionViewSet)
router.register(r'reports', ReportViewSet)

urlpatterns = [
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
