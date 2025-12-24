"""
URL configuration for core app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FrameworkViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'frameworks', FrameworkViewSet, basename='framework')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]