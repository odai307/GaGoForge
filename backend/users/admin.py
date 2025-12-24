"""
Admin configuration for users app.
"""

from django.contrib import admin
from .models import UserProfile, HintUsage


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'total_problems_solved', 'total_submissions', 
        'current_streak_days', 'longest_streak_days', 'last_activity_date'
    ]
    list_filter = ['created_at', 'theme', 'preferred_language']
    search_fields = ['user__username', 'user__email', 'bio']
    ordering = ['-total_problems_solved', '-total_score']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Overall Statistics', {
            'fields': (
                'total_problems_solved', 'total_problems_attempted', 
                'total_submissions', 'total_score'
            )
        }),
        ('Difficulty Statistics', {
            'fields': ('beginner_solved', 'intermediate_solved', 'pro_solved', 'veteran_solved')
        }),
        ('Framework Statistics', {
            'fields': ('framework_stats',),
            'classes': ('collapse',)
        }),
        ('Streaks', {
            'fields': ('current_streak_days', 'longest_streak_days', 'last_activity_date')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'theme', 'email_notifications')
        }),
        ('Social', {
            'fields': ('bio', 'github_username', 'website_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Profiles are auto-created with users."""
        return False


@admin.register(HintUsage)
class HintUsageAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'hint_index', 'viewed_at']
    list_filter = ['viewed_at', 'problem__framework']
    search_fields = ['user__username', 'problem__title']
    ordering = ['-viewed_at']
    readonly_fields = ['viewed_at']
    
    fieldsets = (
        ('Tracking', {
            'fields': ('user', 'problem', 'hint_index', 'viewed_at')
        }),
    )
