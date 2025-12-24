"""
URL configuration for users app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, HintUsageViewSet, register, current_user, logout

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'hints', HintUsageViewSet, basename='hint')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register, name='register'),
    path('me/', current_user, name='current-user'),
    path('logout/', logout, name='logout'),
]