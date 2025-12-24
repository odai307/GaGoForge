"""
Core models for GaGoForge.
Framework and Category models.
"""

from django.db import models


class Framework(models.Model):
    """
    Represents a programming framework/technology.
    Examples: Django, React, Angular, Express
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Internal framework name (e.g., 'django', 'react')"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Display name for UI (e.g., 'Django', 'React')"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of the framework"
    )
    icon_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to framework icon/logo"
    )
    version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary version supported (e.g., '4.2', '18')"
    )
    documentation_url = models.URLField(
        blank=True,
        null=True,
        help_text="Link to official documentation"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this framework is currently available for problems"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower numbers first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'display_name']
        verbose_name = 'Framework'
        verbose_name_plural = 'Frameworks'

    def __str__(self):
        return self.display_name


class Category(models.Model):
    """
    Problem categories within a framework.
    Examples: Models, Serializers, Components, Hooks
    """
    framework = models.ForeignKey(
        Framework,
        on_delete=models.CASCADE,
        related_name='categories',
        help_text="Framework this category belongs to"
    )
    name = models.CharField(
        max_length=100,
        help_text="Internal category name (e.g., 'models', 'serializers')"
    )
    display_name = models.CharField(
        max_length=150,
        help_text="Display name for UI (e.g., 'Models', 'Serializers')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this category covers"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within framework"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is available"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['framework', 'order', 'display_name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        unique_together = ['framework', 'name']

    def __str__(self):
        return f"{self.framework.display_name} - {self.display_name}"
