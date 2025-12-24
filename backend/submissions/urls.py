"""
URL configuration for submissions app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubmissionViewSet, UserProgressViewSet

router = DefaultRouter()
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'progress', UserProgressViewSet, basename='progress')

urlpatterns = [
    path('', include(router.urls)),
]