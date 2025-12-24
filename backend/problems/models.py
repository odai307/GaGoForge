"""
Problem and Pattern models for GaGoForge.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Framework, Category
import uuid


class Problem(models.Model):
    """
    Represents a coding challenge.
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('pro', 'Pro'),
        ('veteran', 'Veteran'),
    ]

    # Identification
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    problem_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique identifier (e.g., 'django-serializer-001')"
    )
    slug = models.SlugField(
        max_length=150,
        unique=True,
        help_text="URL-friendly version of title"
    )
    
    # Basic Info
    title = models.CharField(
        max_length=255,
        help_text="Problem title shown to users"
    )
    framework = models.ForeignKey(
        Framework,
        on_delete=models.CASCADE,
        related_name='problems'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='problems'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner'
    )
    
    # Content
    description = models.TextField(
        help_text="Full problem description (supports Markdown)"
    )
    description_preview = models.CharField(
        max_length=300,
        blank=True,
        help_text="Short preview for problem list"
    )
    context_code = models.TextField(
        blank=True,
        help_text="Pre-existing code context (read-only for user)"
    )
    starter_code = models.TextField(
        blank=True,
        help_text="Initial code in editor (editable by user)"
    )
    target_area = models.CharField(
        max_length=200,
        blank=True,
        help_text="What part of code to implement (e.g., 'UserSerializer class')"
    )
    
    # Validation Configuration
    validation_spec = models.JSONField(
        default=dict,
        help_text="Validation configuration (imports, structure, behavior)"
    )
    
    # Scoring Weights
    import_weight = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=20.00,
        help_text="Weight for imports validation (default 20%)"
    )
    structure_weight = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=35.00,
        help_text="Weight for structure validation (default 35%)"
    )
    behavior_weight = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=45.00,
        help_text="Weight for behavior validation (default 45%)"
    )
    passing_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=80.00,
        help_text="Minimum score to consider problem solved"
    )
    
    # Hints and Resources
    hints = models.JSONField(
        default=list,
        help_text="Progressive hints as JSON array"
    )
    learning_resources = models.JSONField(
        default=list,
        help_text="External learning resources as JSON array"
    )
    
    # Metadata
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorization"
    )
    estimated_time_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Estimated time to solve (in minutes)"
    )
    
    # Statistics
    total_submissions = models.PositiveIntegerField(
        default=0,
        help_text="Total number of submissions"
    )
    accepted_submissions = models.PositiveIntegerField(
        default=0,
        help_text="Number of accepted submissions"
    )
    acceptance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Acceptance rate percentage"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether problem is available to users"
    )
    is_premium = models.BooleanField(
        default=False,
        help_text="Whether problem requires premium access"
    )
    
    # Timestamps
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_problems'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #is_deleted = models.BooleanField(default=False)
    #deleted_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        ordering = ['framework', 'difficulty', 'order', 'title']
        verbose_name = 'Problem'
        verbose_name_plural = 'Problems'
        indexes = [
            models.Index(fields=['framework', 'difficulty']),
            models.Index(fields=['problem_id']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"[{self.difficulty.upper()}] {self.title}"

    def save(self, *args, **kwargs):
        # Auto-generate preview if not provided
        if not self.description_preview and self.description:
            self.description_preview = self.description[:297] + '...'
        
        # Update acceptance rate
        if self.total_submissions > 0:
            self.acceptance_rate = (self.accepted_submissions / self.total_submissions) * 100
        
        super().save(*args, **kwargs)

    #def delete(self, *args, **kwargs):
        #self.is_deleted = True
        #self.deleted_at = timezone.now()
        #self.save()


    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within category"
    )


class Pattern(models.Model):
    """
    Represents a valid solution pattern for a problem.
    Stores AST representation and validation rules.
    """
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='patterns'
    )
    pattern_id = models.CharField(
        max_length=100,
        help_text="Unique identifier for this pattern"
    )
    name = models.CharField(
        max_length=200,
        help_text="Descriptive name (e.g., 'Standard ModelSerializer')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this solution approach"
    )
    
    # Pattern Data
    ast_representation = models.JSONField(
        help_text="AST structure of the pattern"
    )
    behavior_signature = models.JSONField(
        default=dict,
        help_text="Expected behavior characteristics"
    )
    example_code = models.TextField(
        blank=True,
        help_text="Example code that matches this pattern"
    )
    
    # Validation Rules
    required_imports = models.JSONField(
        default=list,
        help_text="List of required imports"
    )
    required_structure = models.JSONField(
        default=dict,
        help_text="Required code structure elements"
    )
    forbidden_patterns = models.JSONField(
        default=list,
        help_text="Patterns that should not be present"
    )
    
    # Pattern Metadata
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the recommended solution pattern"
    )
    confidence_threshold = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=85.00,
        help_text="Minimum match confidence to accept (0-100)"
    )
    
    # Statistics
    match_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of submissions matching this pattern"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', 'pattern_id']
        verbose_name = 'Pattern'
        verbose_name_plural = 'Patterns'
        unique_together = ['problem', 'pattern_id']

    def __str__(self):
        primary = " (Primary)" if self.is_primary else ""
        return f"{self.problem.problem_id} - {self.name}{primary}"
