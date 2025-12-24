"""
Admin configuration for submissions app.
"""

from django.contrib import admin
from .models import Submission, UserProgress


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'submission_id', 'user', 'problem', 'verdict', 
        'score', 'attempt_number', 'submitted_at', 'is_disputed'
    ]
    list_filter = ['verdict', 'is_disputed', 'dispute_resolved', 'submitted_at', 'problem__framework']
    search_fields = ['user__username', 'problem__title', 'submission_id']
    ordering = ['-submitted_at']
    readonly_fields = ['submission_id', 'submitted_at', 'validated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('submission_id', 'user', 'problem')
        }),
        ('Code', {
            'fields': ('code', 'language'),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('verdict', 'score', 'execution_time_ms')
        }),
        ('Validation Details', {
            'fields': ('validation_results', 'feedback', 'matched_patterns'),
            'classes': ('collapse',)
        }),
        ('Hints', {
            'fields': ('hints_used', 'hint_indices'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('attempt_number', 'submitted_at', 'validated_at')
        }),
        ('Dispute', {
            'fields': ('is_disputed', 'dispute_reason', 'dispute_resolved'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Submissions should only be created through API."""
        return False


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'problem', 'is_solved', 'best_score', 
        'total_attempts', 'hints_viewed', 'last_attempt_at'
    ]
    list_filter = ['is_solved', 'is_attempted', 'problem__framework', 'problem__difficulty']
    search_fields = ['user__username', 'problem__title']
    ordering = ['-last_attempt_at']
    readonly_fields = ['first_attempt_at', 'solved_at', 'last_attempt_at']
    
    fieldsets = (
        ('Relationships', {
            'fields': ('user', 'problem')
        }),
        ('Status', {
            'fields': ('is_solved', 'is_attempted')
        }),
        ('Statistics', {
            'fields': ('total_attempts', 'best_score', 'best_submission', 'hints_viewed')
        }),
        ('Timestamps', {
            'fields': ('first_attempt_at', 'solved_at', 'last_attempt_at')
        }),
    )
    
    def has_add_permission(self, request):
        """Progress should be auto-created through submissions."""
        return False
