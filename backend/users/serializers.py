"""
Serializers for users app models.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, HintUsage


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    # Framework-specific stats (extracted from framework_stats JSONField)
    django_solved = serializers.SerializerMethodField()
    react_solved = serializers.SerializerMethodField()
    express_solved = serializers.SerializerMethodField()
    angular_solved = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'email',
            'total_problems_solved',
            'total_problems_attempted',
            'total_submissions',
            'total_score',
            'beginner_solved',
            'intermediate_solved',
            'pro_solved',
            'veteran_solved',
            'framework_stats',
            'django_solved',
            'react_solved',
            'express_solved',
            'angular_solved',
            'current_streak_days',
            'longest_streak_days',
            'last_activity_date',
            'preferred_language',
            'theme',
            'email_notifications',
            'bio',
            'github_username',
            'website_url',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'user',
            'total_problems_solved',
            'total_problems_attempted',
            'total_submissions',
            'total_score',
            'beginner_solved',
            'intermediate_solved',
            'pro_solved',
            'veteran_solved',
            'framework_stats',
            'current_streak_days',
            'longest_streak_days',
            'last_activity_date',
            'created_at',
            'updated_at'
        ]

    def get_django_solved(self, obj):
        """Extract Django problems solved from framework_stats."""
        return obj.framework_stats.get('django', 0)
    
    def get_react_solved(self, obj):
        """Extract React problems solved from framework_stats."""
        return obj.framework_stats.get('react', 0)
        
    def get_express_solved(self, obj):
        """Extract Express problems solved from framework_stats."""
        return obj.framework_stats.get('express', 0)
        
        
    def get_angular_solved(self, obj):
        """Extract Angular problems solved from framework_stats."""
        return obj.framework_stats.get('angular', 0)
    


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating editable user profile fields."""
    
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    
    class Meta:
        model = UserProfile
        fields = [
            # User fields (editable)
            'first_name',
            'last_name',
            
            # Profile preferences (editable)
            'preferred_language',
            'theme',
            'email_notifications',
            
            # Social fields (editable)
            'bio',
            'github_username',
            'website_url',
        ]
    
    def validate_github_username(self, value):
        """Validate GitHub username format."""
        if value and not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("GitHub username can only contain alphanumeric characters, hyphens, and underscores")
        return value
    
    def validate_bio(self, value):
        """Validate bio length."""
        if len(value) > 500:
            raise serializers.ValidationError("Bio cannot exceed 500 characters")
        return value
    
    def validate_preferred_language(self, value):
        """Validate preferred language."""
        valid_languages = ['python', 'javascript', 'typescript', 'java', 'c++', 'go', 'rust']
        if value.lower() not in valid_languages:
            raise serializers.ValidationError(f"Preferred language must be one of: {', '.join(valid_languages)}")
        return value.lower()
    
    def validate_theme(self, value):
        """Validate theme choice."""
        if value not in ['light', 'dark']:
            raise serializers.ValidationError("Theme must be 'light' or 'dark'")
        return value
    
    def update(self, instance, validated_data):
        """Update profile and related user fields."""
        # Handle user fields separately
        user_data = {}
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
        
        # Update User model fields
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance



class HintUsageSerializer(serializers.ModelSerializer):
    """Serializer for HintUsage model."""
    
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    
    class Meta:
        model = HintUsage
        fields = ['id', 'problem', 'problem_title', 'hint_index', 'viewed_at']
        read_only_fields = ['id', 'viewed_at']