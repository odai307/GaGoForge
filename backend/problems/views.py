"""
API views for problems app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Problem, Pattern
from .serializers import (
    ProblemListSerializer,
    ProblemDetailSerializer,
    ProblemCreateSerializer,
    PatternSerializer
)


class ProblemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Problem model.
    List, retrieve, create, update, delete actions.
    """
    queryset = Problem.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['framework__name', 'category__name', 'difficulty', 'is_premium']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'difficulty', 'acceptance_rate', 'total_submissions']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ProblemListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProblemCreateSerializer
        return ProblemDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user authentication and filters."""
        queryset = super().get_queryset()
        
        # Filter by solved status for authenticated users
        if self.request.user.is_authenticated:
            is_solved = self.request.query_params.get('is_solved')
            if is_solved is not None:
                if is_solved.lower() == 'true':
                    queryset = queryset.filter(
                        user_progress__user=self.request.user,
                        user_progress__is_solved=True
                    )
                elif is_solved.lower() == 'false':
                    queryset = queryset.exclude(
                        user_progress__user=self.request.user,
                        user_progress__is_solved=True
                    )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def patterns(self, request, slug=None):
        """Get all patterns for a problem."""
        problem = self.get_object()
        patterns = problem.patterns.all()
        serializer = PatternSerializer(patterns, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def starter_code(self, request, slug=None):
        """Get starter code for a problem."""
        problem = self.get_object()
        return Response({
            'context_code': problem.context_code,
            'starter_code': problem.starter_code,
            'target_area': problem.target_area
        })
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """Get a random problem based on filters."""
        queryset = self.filter_queryset(self.get_queryset())
        problem = queryset.order_by('?').first()
        
        if problem:
            serializer = self.get_serializer(problem)
            return Response(serializer.data)
        return Response(
            {'detail': 'No problems found matching the criteria'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get overall problem statistics."""
        stats = {
            'total': Problem.objects.filter(is_active=True).count(),
            'by_difficulty': {
                'beginner': Problem.objects.filter(difficulty='beginner', is_active=True).count(),
                'intermediate': Problem.objects.filter(difficulty='intermediate', is_active=True).count(),
                'pro': Problem.objects.filter(difficulty='pro', is_active=True).count(),
                'veteran': Problem.objects.filter(difficulty='veteran', is_active=True).count(),
            },
            'by_framework': {}
        }
        
        from core.models import Framework
        for framework in Framework.objects.filter(is_active=True):
            stats['by_framework'][framework.name] = framework.problems.filter(is_active=True).count()
        
        return Response(stats)


class PatternViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Pattern model.
    Read-only access to patterns.
    """
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['problem', 'is_primary']