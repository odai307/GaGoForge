"""
URL configuration for problems app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProblemViewSet, PatternViewSet

router = DefaultRouter()
router.register(r'problems', ProblemViewSet, basename='problem')
router.register(r'patterns', PatternViewSet, basename='pattern')

urlpatterns = [
    path('', include(router.urls)),
]