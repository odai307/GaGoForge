"""
API views for submissions app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import models
from django.db.models import Q, Avg, Sum
from datetime import date
import time
import logging

logger = logging.getLogger('validation')

from .models import Submission, UserProgress
from .serializers import (
    SubmissionCreateSerializer,
    SubmissionSerializer,
    SubmissionListSerializer,
    SubmissionDetailSerializer,
    DisputeSubmissionSerializer,
    UserProgressSerializer
)
from problems.models import Problem
from validation.services.submission_service import SubmissionService
from submissions.services.progress_service import UserProgressService
from users.services.profile_service import UserProfileService
from problems.services.problem_stats_service import ProblemStatsService


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Submission model.
    Create, list, retrieve submissions.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['problem', 'verdict', 'is_disputed']
    ordering_fields = ['submitted_at', 'score']
    ordering = ['-submitted_at']
    
    def get_queryset(self):
        """Return submissions for current user."""
        return Submission.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return SubmissionCreateSerializer
        elif self.action == 'list':
            return SubmissionListSerializer
        elif self.action == 'retrieve':
            return SubmissionDetailSerializer
        return SubmissionSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new submission and validate it.
        This triggers the validation engine to check the code.
        """
        user = request.user.username
        logger.debug(f"Submission from {user}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            problem = serializer.validated_data['problem']
            code = serializer.validated_data['code']
            language = serializer.validated_data.get('language', 'python')
            
            # Get attempt number
            attempt_number = Submission.objects.filter(
                user=request.user,
                problem=problem
            ).count() + 1
            
            # Get hints used (if provided in request)
            hints_used = request.data.get('hints_used', 0)
            hint_indices = request.data.get('hint_indices', [])
            
            # Create submission with pending status
            submission = Submission.objects.create(
                user=request.user,
                problem=problem,
                code=code,
                language=language,
                attempt_number=attempt_number,
                hints_used=hints_used,
                hint_indices=hint_indices,
                verdict='pending',
                score=0
            )
            
            logger.debug(f"Created submission {str(submission.submission_id)[:8]}")
            
            # PHASE 2: VALIDATE SUBMISSION
            start_time = time.time()
            
            # Run validation engine
            validation_result = SubmissionService.validate_submission(submission)
            
            execution_time = int((time.time() - start_time) * 1000)  # Convert to ms
            
            # Update submission with validation results
            submission.verdict = validation_result['verdict']
            submission.score = validation_result['score']
            submission.validation_results = validation_result['validation_results']
            submission.feedback = validation_result['feedback']
            submission.matched_patterns = validation_result.get('matched_patterns', [])
            submission.execution_time_ms = execution_time
            submission.validated_at = timezone.now()
            submission.save()
            
            logger.info(f"Saved: {user} → {validation_result['verdict']} ({validation_result['score']:.1f})")
            
        except Exception as e:
            # If validation fails unexpectedly, mark as error
            submission.verdict = 'failed'
            submission.score = 0
            submission.feedback = [
                {
                    'type': 'error',
                    'message': f'Validation error: {str(e)}',
                    'line': None,
                    'column': None
                }
            ]
            submission.validated_at = timezone.now()
            submission.save()
            logger.error(f"Submission error: {str(e)}", exc_info=True)
            raise
        
        # Update user progress using service
        progress = UserProgressService.update_progress(submission)
        
        # Update user profile using service
        UserProfileService.update_profile_on_submission(submission)
        UserProfileService.update_streak(request.user)
        
        # Update problem stats using service
        ProblemStatsService.update_problem_stats(submission)
        
        # Return response with full submission details
        response_serializer = SubmissionSerializer(submission)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def dispute(self, request, pk=None):
        """Allow user to dispute a submission verdict."""
        submission = self.get_object()
        
        if submission.is_disputed:
            return Response(
                {'detail': 'This submission has already been disputed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = DisputeSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        submission.is_disputed = True
        submission.dispute_reason = serializer.validated_data['dispute_reason']
        submission.save()
        
        return Response({
            'detail': 'Submission disputed successfully',
            'submission_id': str(submission.submission_id)
        })
    
    @action(detail=False, methods=['get'])
    def recent_submissions(self, request):
        """Get user's 10 most recent submissions"""
        submissions = self.get_queryset().order_by('-submitted_at')[:10]
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user's submission statistics"""
        user_submissions = self.get_queryset()
        
        stats = {
            'total_submissions': user_submissions.count(),
            'accepted': user_submissions.filter(verdict='accepted').count(),
            'partially_passed': user_submissions.filter(verdict='partially_passed').count(),
            'failed': user_submissions.filter(verdict='failed').count(),
            'syntax_errors': user_submissions.filter(verdict='syntax_error').count(),
            'average_score': 0.0,
            'total_score': 0
        }
        
        if stats['total_submissions'] > 0:
            avg = user_submissions.aggregate(avg=models.Avg('score'))
            stats['average_score'] = round(float(avg['avg'] or 0), 2)
            total = user_submissions.aggregate(total=models.Sum('score'))
            stats['total_score'] = int(total['total'] or 0)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def solved_problems(self, request):
        """Get all problems user has solved"""
        solved = UserProgress.objects.filter(user=request.user, is_solved=True)
        serializer = UserProgressSerializer(solved, many=True)
        return Response(serializer.data)


class UserProgressViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_solved', 'problem__difficulty', 'problem__framework__name']
    ordering_fields = ['best_score', 'last_attempt_at', 'solved_at']
    ordering = ['-last_attempt_at']
    
    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get user's overall progress summary"""
        progress = self.get_queryset()
        
        summary = {
            'total_attempted': progress.filter(is_attempted=True).count(),
            'total_solved': progress.filter(is_solved=True).count(),
            'by_difficulty': {
                'beginner': {
                    'attempted': progress.filter(problem__difficulty='beginner', is_attempted=True).count(),
                    'solved': progress.filter(problem__difficulty='beginner', is_solved=True).count()
                },
                'intermediate': {
                    'attempted': progress.filter(problem__difficulty='intermediate', is_attempted=True).count(),
                    'solved': progress.filter(problem__difficulty='intermediate', is_solved=True).count()
                },
                'pro': {
                    'attempted': progress.filter(problem__difficulty='pro', is_attempted=True).count(),
                    'solved': progress.filter(problem__difficulty='pro', is_solved=True).count()
                },
                'veteran': {
                    'attempted': progress.filter(problem__difficulty='veteran', is_attempted=True).count(),
                    'solved': progress.filter(problem__difficulty='veteran', is_solved=True).count()
                }
            },
            'by_framework': {}
        }
        
        frameworks = ['django', 'react', 'express', 'angular']
        for framework in frameworks:
            summary['by_framework'][framework] = {
                'attempted': progress.filter(problem__framework__name=framework, is_attempted=True).count(),
                'solved': progress.filter(problem__framework__name=framework, is_solved=True).count()
            }
        
        return Response(summary)