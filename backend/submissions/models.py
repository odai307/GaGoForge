"""
Submission and UserProgress models for GaGoForge.
"""

from django.db import models
from django.contrib.auth.models import User
from problems.models import Problem, Pattern
import uuid


class Submission(models.Model):
    """
    Represents a user's code submission for a problem.
    """
    VERDICT_CHOICES = [
        ('accepted', 'Accepted'),
        ('partially_passed', 'Partially Passed'),
        ('failed', 'Failed'),
        ('syntax_error', 'Syntax Error'),
        ('pending', 'Pending'),
    ]

    # Identification
    submission_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    
    # Submission Data
    code = models.TextField(
        help_text="User's submitted code"
    )
    language = models.CharField(
        max_length=50,
        default='python',
        help_text="Programming language (python, javascript)"
    )
    
    # Results
    verdict = models.CharField(
        max_length=20,
        choices=VERDICT_CHOICES,
        default='pending'
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Overall score (0-100)"
    )
    
    # Detailed Validation Results
    validation_results = models.JSONField(
        default=dict,
        help_text="Detailed breakdown of validation (imports, structure, behavior)"
    )
    feedback = models.JSONField(
        default=list,
        help_text="Array of feedback messages with line numbers"
    )
    matched_patterns = models.JSONField(
        default=list,
        help_text="Patterns that were matched with confidence scores"
    )
    
    # Execution Metrics
    execution_time_ms = models.PositiveIntegerField(
        default=0,
        help_text="Validation execution time in milliseconds"
    )
    
    # Hints Usage
    hints_used = models.PositiveIntegerField(
        default=0,
        help_text="Number of hints viewed before this submission"
    )
    hint_indices = models.JSONField(
        default=list,
        help_text="Which hints were viewed (array of indices)"
    )
    
    # Attempt Tracking
    attempt_number = models.PositiveIntegerField(
        default=1,
        help_text="Which attempt this is for this user-problem combination"
    )
    
    # Dispute
    is_disputed = models.BooleanField(
        default=False,
        help_text="User claims this should be accepted"
    )
    dispute_reason = models.TextField(
        blank=True,
        help_text="User's reason for disputing the verdict"
    )
    dispute_resolved = models.BooleanField(
        default=False
    )
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When validation completed"
    )

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        indexes = [
            models.Index(fields=['user', 'problem']),
            models.Index(fields=['verdict']),
            models.Index(fields=['-submitted_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} ({self.verdict})"

    def is_accepted(self):
        """Check if submission is fully accepted."""
        return self.verdict == 'accepted'

    def is_passing(self):
        """Check if submission meets passing score threshold."""
        return self.score >= self.problem.passing_score


class UserProgress(models.Model):
    """
    Tracks user's progress on a specific problem.
    """
    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    # Status
    is_solved = models.BooleanField(
        default=False,
        help_text="Whether user has successfully solved this problem"
    )
    is_attempted = models.BooleanField(
        default=False,
        help_text="Whether user has made at least one attempt"
    )
    
    # Statistics
    total_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Total number of submissions"
    )
    best_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Highest score achieved"
    )
    best_submission = models.ForeignKey(
        Submission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    
    # Hints
    hints_viewed = models.PositiveIntegerField(
        default=0,
        help_text="Number of hints viewed for this problem"
    )
    
    # Timestamps
    first_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user first attempted this problem"
    )
    solved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user first solved this problem"
    )
    last_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Most recent submission time"
    )

    class Meta:
        ordering = ['-last_attempt_at']
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
        unique_together = ['user', 'problem']
        indexes = [
            models.Index(fields=['user', 'is_solved']),
        ]

    def __str__(self):
        status = "Solved" if self.is_solved else f"Attempted ({self.total_attempts})"
        return f"{self.user.username} - {self.problem.title} ({status})"
