"""
Serializers for submissions app models.
"""

from rest_framework import serializers
from .models import Submission, UserProgress
from problems.serializers import ProblemListSerializer


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating submissions."""
    
    class Meta:
        model = Submission
        fields = ['problem', 'code', 'language']
    
    def validate_code(self, value):
        """Validate that code is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Code cannot be empty")
        return value


class SubmissionSerializer(serializers.ModelSerializer):
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    problem_framework = serializers.CharField(source='problem.framework.name', read_only=True)
    problem_difficulty = serializers.CharField(source='problem.difficulty', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'submission_id',
            'problem',
            'problem_title',
            'problem_framework',
            'problem_difficulty',
            'username',
            'code',
            'language',
            'verdict',
            'score',
            'feedback',
            'validation_results',
            'matched_patterns',
            'execution_time_ms',
            'attempt_number',
            'is_disputed',
            'dispute_reason',
            'submitted_at',
            'validated_at'
        ]
        read_only_fields = fields


class SubmissionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for submission lists."""
    
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    problem_id = serializers.CharField(source='problem.problem_id', read_only=True)
    framework = serializers.CharField(source='problem.framework.name', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'submission_id',
            'problem',
            'problem_id',
            'problem_title',
            'framework',
            'verdict',
            'score',
            'attempt_number',
            'submitted_at'
        ]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual submission view."""
    
    problem = ProblemListSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'submission_id',
            'user',
            'username',
            'problem',
            'code',
            'language',
            'verdict',
            'score',
            'validation_results',
            'feedback',
            'matched_patterns',
            'execution_time_ms',
            'hints_used',
            'hint_indices',
            'attempt_number',
            'is_disputed',
            'dispute_reason',
            'dispute_resolved',
            'submitted_at',
            'validated_at'
        ]


class DisputeSubmissionSerializer(serializers.Serializer):
    """Serializer for disputing a submission verdict."""
    
    dispute_reason = serializers.CharField(
        max_length=1000,
        required=True,
        help_text="Explain why you believe this verdict is incorrect"
    )


class UserProgressSerializer(serializers.ModelSerializer):
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    problem_framework = serializers.CharField(source='problem.framework.name', read_only=True)
    problem_difficulty = serializers.CharField(source='problem.difficulty', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'problem',
            'problem_title',
            'problem_framework',
            'problem_difficulty',
            'is_solved',
            'total_attempts',
            'best_score',
            'solved_at',
            'first_attempt_at',
            'last_attempt_at'
        ]
        read_only_fields = fields