"""
Admin configuration for problems app.
"""

from django.contrib import admin
from .models import Problem, Pattern


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = [
        'problem_id', 'title', 'framework', 'category', 
        'difficulty', 'is_active', 'acceptance_rate', 'total_submissions'
    ]
    list_filter = ['framework', 'category', 'difficulty', 'is_active', 'is_premium', 'created_at']
    search_fields = ['problem_id', 'title', 'description']
    ordering = ['framework', 'difficulty', 'order', 'title']
    list_editable = ['is_active']
    readonly_fields = ['id', 'total_submissions', 'accepted_submissions', 'acceptance_rate', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'problem_id', 'slug')
        }),
        ('Basic Information', {
            'fields': ('title', 'framework', 'category', 'difficulty')
        }),
        ('Content', {
            'fields': ('description', 'description_preview', 'context_code', 'starter_code', 'target_area')
        }),
        ('Validation Configuration', {
            'fields': ('validation_spec',),
            'classes': ('collapse',)
        }),
        ('Scoring', {
            'fields': ('import_weight', 'structure_weight', 'behavior_weight', 'passing_score')
        }),
        ('Hints & Resources', {
            'fields': ('hints', 'learning_resources'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('tags', 'estimated_time_minutes', 'order')
        }),
        ('Statistics', {
            'fields': ('total_submissions', 'accepted_submissions', 'acceptance_rate'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_premium')
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation."""
        if obj:  # Editing existing object
            return self.readonly_fields + ['problem_id']
        return self.readonly_fields


@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = ['pattern_id', 'problem', 'name', 'is_primary', 'confidence_threshold', 'match_count']
    list_filter = ['is_primary', 'problem__framework', 'created_at']
    search_fields = ['pattern_id', 'name', 'description', 'problem__title']
    ordering = ['problem', '-is_primary', 'pattern_id']
    list_editable = ['is_primary']
    readonly_fields = ['match_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('problem', 'pattern_id', 'name', 'description')
        }),
        ('Pattern Data', {
            'fields': ('ast_representation', 'behavior_signature', 'example_code'),
            'classes': ('collapse',)
        }),
        ('Validation Rules', {
            'fields': ('required_imports', 'required_structure', 'forbidden_patterns'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('is_primary', 'confidence_threshold')
        }),
        ('Statistics', {
            'fields': ('match_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
