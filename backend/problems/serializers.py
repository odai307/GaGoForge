"""
Serializers for problems app models.
"""

from rest_framework import serializers
from .models import Problem, Pattern
from core.models import Framework, Category #(Considering this was missed, should an issue arise, check here)
from core.serializers import FrameworkSerializer, CategorySerializer, CategoryListSerializer



class PatternSerializer(serializers.ModelSerializer):
    """Serializer for Pattern model."""
    
    class Meta:
        model = Pattern
        fields = [
            'id',
            'pattern_id',
            'name',
            'description',
            'ast_representation',
            'behavior_signature',
            'example_code',
            'required_imports',
            'required_structure',
            'forbidden_patterns',
            'is_primary',
            'confidence_threshold',
            'match_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'match_count', 'created_at', 'updated_at']


class PatternListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for pattern lists."""
    
    class Meta:
        model = Pattern
        fields = ['id', 'pattern_id', 'name', 'is_primary']


class ProblemListSerializer(serializers.ModelSerializer):
    """Serializer for problem list view (lightweight)."""
    
    framework = serializers.CharField(source='framework.name')
    framework_display = serializers.CharField(source='framework.display_name')
    category = serializers.CharField(source='category.name')
    category_display = serializers.CharField(source='category.display_name')
    
    class Meta:
        model = Problem
        fields = [
            'id',
            'problem_id',
            'slug',
            'title',
            'framework',
            'framework_display',
            'category',
            'category_display',
            'difficulty',
            'description_preview',
            'acceptance_rate',
            'total_submissions',
            'is_premium',
            'tags',
            'estimated_time_minutes'
        ]


class ProblemDetailSerializer(serializers.ModelSerializer):
    """Serializer for problem detail view (full information)."""
    
    framework = FrameworkSerializer(read_only=True)
    category = CategoryListSerializer(read_only=True)
    patterns = PatternListSerializer(many=True, read_only=True)
    
    # User-specific fields (will be added dynamically in view)
    is_solved = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Problem
        fields = [
            'id',
            'problem_id',
            'slug',
            'title',
            'framework',
            'category',
            'difficulty',
            'description',
            'description_preview',
            'context_code',
            'starter_code',
            'target_area',
            'hints',
            'learning_resources',
            'tags',
            'estimated_time_minutes',
            'acceptance_rate',
            'total_submissions',
            'is_premium',
            'patterns',
            'is_solved',
            'user_progress',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'acceptance_rate',
            'total_submissions',
            'created_at',
            'updated_at'
        ]
    
    def get_is_solved(self, obj):
        """Check if current user has solved this problem."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            progress = obj.user_progress.filter(user=request.user).first()
            return progress.is_solved if progress else False
        return False
    
    def get_user_progress(self, obj):
        """Get user's progress on this problem."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from submissions.serializers import UserProgressSerializer
            progress = obj.user_progress.filter(user=request.user).first()
            if progress:
                return UserProgressSerializer(progress).data
        return None


class ProblemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating problems."""
    
    framework_id = serializers.PrimaryKeyRelatedField(
        queryset=Framework.objects.all(),
        source='framework',
        write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    
    class Meta:
        model = Problem
        fields = [
            'problem_id',
            'slug',
            'title',
            'framework_id',
            'category_id',
            'difficulty',
            'description',
            'description_preview',
            'context_code',
            'starter_code',
            'target_area',
            'validation_spec',
            'import_weight',
            'structure_weight',
            'behavior_weight',
            'passing_score',
            'hints',
            'learning_resources',
            'tags',
            'estimated_time_minutes',
            'is_active',
            'is_premium'
        ]