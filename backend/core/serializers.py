"""
Serializers for core app models.
"""

from rest_framework import serializers
from .models import Framework, Category


class FrameworkSerializer(serializers.ModelSerializer):
    """Serializer for Framework model."""
    
    class Meta:
        model = Framework
        fields = [
            'id',
            'name',
            'display_name',
            'description',
            'icon_url',
            'version',
            'documentation_url',
            'is_active',
            'order',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    framework = FrameworkSerializer(read_only=True)
    framework_id = serializers.PrimaryKeyRelatedField(
        queryset=Framework.objects.all(),
        source='framework',
        write_only=True
    )
    
    class Meta:
        model = Category
        fields = [
            'id',
            'framework',
            'framework_id',
            'name',
            'display_name',
            'description',
            'order',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for category lists."""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'display_name', 'order']