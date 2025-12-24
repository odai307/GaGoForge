"""
User profile and tracking models for GaGoForge.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from problems.models import Problem


class UserProfile(models.Model):
    """
    Extended user profile with statistics and preferences.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    
    # Statistics - Overall
    total_problems_solved = models.PositiveIntegerField(
        default=0,
        help_text="Total number of problems solved"
    )
    total_problems_attempted = models.PositiveIntegerField(
        default=0,
        help_text="Total number of problems attempted"
    )
    total_submissions = models.PositiveIntegerField(
        default=0,
        help_text="Total number of code submissions"
    )
    total_score = models.PositiveIntegerField(
        default=0,
        help_text="Cumulative score across all solved problems"
    )
    
    # Statistics - By Difficulty
    beginner_solved = models.PositiveIntegerField(default=0)
    intermediate_solved = models.PositiveIntegerField(default=0)
    pro_solved = models.PositiveIntegerField(default=0)
    veteran_solved = models.PositiveIntegerField(default=0)
    
    # Statistics - By Framework
    framework_stats = models.JSONField(
        default=dict,
        help_text="Problems solved per framework {'django': 10, 'react': 5, ...}"
    )
    
    # Streaks
    current_streak_days = models.PositiveIntegerField(
        default=0,
        help_text="Current consecutive days with activity"
    )
    longest_streak_days = models.PositiveIntegerField(
        default=0,
        help_text="Longest streak ever achieved"
    )
    last_activity_date = models.DateField(
        null=True,
        blank=True,
        help_text="Last date user solved a problem"
    )
    
    # Preferences
    preferred_language = models.CharField(
        max_length=50,
        default='python',
        help_text="Preferred programming language"
    )
    theme = models.CharField(
        max_length=20,
        default='dark',
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
        ]
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive email notifications"
    )
    
    # Social
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text="User biography"
    )
    github_username = models.CharField(
        max_length=100,
        blank=True,
        help_text="GitHub username"
    )
    website_url = models.URLField(
        blank=True,
        help_text="Personal website URL"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def update_streak(self, activity_date):
        """Update streak counters based on activity date."""
        from datetime import timedelta
        
        if not self.last_activity_date:
            # First activity
            self.current_streak_days = 1
            self.longest_streak_days = 1
        else:
            days_diff = (activity_date - self.last_activity_date).days
            
            if days_diff == 1:
                # Consecutive day
                self.current_streak_days += 1
                if self.current_streak_days > self.longest_streak_days:
                    self.longest_streak_days = self.current_streak_days
            elif days_diff == 0:
                # Same day, no change
                pass
            else:
                # Streak broken
                self.current_streak_days = 1
        
        self.last_activity_date = activity_date
        self.save()

    def increment_framework_stat(self, framework_name):
        """Increment problem count for a specific framework."""
        if not self.framework_stats:
            self.framework_stats = {}
        
        current = self.framework_stats.get(framework_name, 0)
        self.framework_stats[framework_name] = current + 1
        self.save()


class HintUsage(models.Model):
    """
    Tracks which hints users have viewed for problems.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hint_usage'
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='hint_usage'
    )
    hint_index = models.PositiveIntegerField(
        help_text="Index of the hint viewed (0-based)"
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['viewed_at']
        verbose_name = 'Hint Usage'
        verbose_name_plural = 'Hint Usage'
        unique_together = ['user', 'problem', 'hint_index']
        indexes = [
            models.Index(fields=['user', 'problem']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - Hint {self.hint_index + 1}"


# Signal to auto-create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
