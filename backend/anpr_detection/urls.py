"""
URL patterns for ANPR detection API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'detections', views.DetectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('process-image/', views.process_image, name='process-image'),
]