"""
API views for core app.
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Framework, Category
from .serializers import FrameworkSerializer, CategorySerializer


class FrameworkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Framework model.
    Provides list and retrieve actions only.
    """
    queryset = Framework.objects.filter(is_active=True)
    serializer_class = FrameworkSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'name'
    
    @action(detail=True, methods=['get'])
    def categories(self, request, name=None):
        """Get all categories for a specific framework."""
        framework = self.get_object()
        categories = framework.categories.filter(is_active=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, name=None):
        """Get statistics for a specific framework."""
        framework = self.get_object()
        stats = {
            'total_problems': framework.problems.filter(is_active=True).count(),
            'beginner': framework.problems.filter(difficulty='beginner', is_active=True).count(),
            'intermediate': framework.problems.filter(difficulty='intermediate', is_active=True).count(),
            'pro': framework.problems.filter(difficulty='pro', is_active=True).count(),
            'veteran': framework.problems.filter(difficulty='veteran', is_active=True).count(),
            'total_categories': framework.categories.filter(is_active=True).count()
        }
        return Response(stats)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Category model.
    Provides list and retrieve actions only.
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['framework']
    
    @action(detail=True, methods=['get'])
    def problems(self, request, pk=None):
        """Get all problems for a specific category."""
        from problems.serializers import ProblemListSerializer
        
        category = self.get_object()
        problems = category.problems.filter(is_active=True)
        
        # Apply difficulty filter if provided
        difficulty = request.query_params.get('difficulty')
        if difficulty:
            problems = problems.filter(difficulty=difficulty)
        
        serializer = ProblemListSerializer(problems, many=True)
        return Response(serializer.data)
