"""
Admin configuration for core app.
"""

from django.contrib import admin
from .models import Framework, Category


@admin.register(Framework)
class FrameworkAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'version', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['order', 'display_name']
    list_editable = ['is_active', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Configuration', {
            'fields': ('version', 'icon_url', 'documentation_url')
        }),
        ('Status', {
            'fields': ('is_active', 'order')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'framework', 'name', 'is_active', 'order', 'created_at']
    list_filter = ['framework', 'is_active', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['framework', 'order', 'display_name']
    list_editable = ['is_active', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('framework', 'name', 'display_name', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'order')
        }),
    )
