"""
API views for users app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import UserProfile, HintUsage
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    HintUsageSerializer
)
from problems.models import Problem


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user."""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout by blacklisting refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Blacklist the token
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserProfile model.
    Users can only access their own profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return profile for current user only."""
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get current user's profile."""
        return self.request.user.profile
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        profile = request.user.profile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get detailed statistics for current user."""
        profile = request.user.profile
        
        # Extract framework stats from JSONField
        framework_stats = profile.framework_stats or {}
        
        stats = {
            'total_problems_solved': profile.total_problems_solved,
            'total_problems_attempted': profile.total_problems_attempted,
            'total_submissions': profile.total_submissions,
            'total_score': profile.total_score,
            'by_difficulty': {
                'beginner': profile.beginner_solved,
                'intermediate': profile.intermediate_solved,
                'pro': profile.pro_solved,
                'veteran': profile.veteran_solved,
            },
            'by_framework': {
                'django': framework_stats.get('django', 0),
                'react': framework_stats.get('react', 0),
                'express': framework_stats.get('express', 0),
                'angular': framework_stats.get('angular', 0),
            },
            'streaks': {
                'current': profile.current_streak_days,
                'longest': profile.longest_streak_days,
                'last_activity': profile.last_activity_date,
            }
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['patch'])
    def update_preferences(self, request):
        """Update user preferences and profile information."""
        profile = request.user.profile
        
        # Use dedicated update serializer
        serializer = UserProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True  # Allow partial updates
        )
        
        if serializer.is_valid():
            serializer.save()
            # Return full profile data
            full_serializer = self.get_serializer(profile)
            return Response(full_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Update full profile (PUT request)."""
        profile = request.user.profile
        
        serializer = UserProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=False  # Require all editable fields
        )
        
        if serializer.is_valid():
            serializer.save()
            full_serializer = self.get_serializer(profile)
            return Response(full_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def editable_fields(self, request):
        """Get list of editable profile fields with current values."""
        profile = request.user.profile
        
        editable_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'preferred_language': profile.preferred_language,
            'theme': profile.theme,
            'email_notifications': profile.email_notifications,
            'bio': profile.bio,
            'github_username': profile.github_username,
            'website_url': profile.website_url,
            'available_options': {
                'themes': ['light', 'dark'],
                'languages': ['python', 'javascript', 'typescript', 'java', 'c++', 'go', 'rust']
            }
        }
        
        return Response(editable_data)
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get user's recent submissions and activity."""
        from submissions.models import Submission
        from submissions.serializers import SubmissionListSerializer
        
        # Get last 10 submissions
        recent_submissions = Submission.objects.filter(
            user=request.user
        ).select_related(
            'problem',
            'problem__framework'
        ).order_by('-submitted_at')[:10]
        
        # Serialize submissions
        serializer = SubmissionListSerializer(recent_submissions, many=True)
        
        return Response({
            'recent_submissions': serializer.data,
            'total_submissions': Submission.objects.filter(user=request.user).count(),
            'recent_activity_count': recent_submissions.count()
        })

    @action(detail=False, methods=['get'])
    def stats_summary(self, request):
        """Get comprehensive stats including total available problems."""
        from problems.models import Problem
        from django.db.models import Count
        
        profile = request.user.profile
        
        # Get user's solved counts
        framework_stats = profile.framework_stats or {}
        
        # Get total available problems per framework
        framework_totals = Problem.objects.filter(
            is_active=True
        ).values('framework__name').annotate(
            total=Count('id')
        )
        
        frameworks_data = {}
        for item in framework_totals:
            framework_name = item['framework__name'].lower()
            solved = framework_stats.get(framework_name, 0)
            total = item['total']
            
            frameworks_data[framework_name] = {
                'name': item['framework__name'],
                'solved': solved,
                'total': total,
                'proficiency': round((solved / total * 100)) if total > 0 else 0,
                'remaining': total - solved
            }
        
        # Get total available problems per difficulty
        difficulty_totals = Problem.objects.filter(
            is_active=True
        ).values('difficulty').annotate(
            total=Count('id')
        )
        
        difficulties_data = {}
        difficulty_colors = {
            'beginner': '#10B981',
            'intermediate': '#F59E0B',
            'pro': '#EF4444',
            'veteran': '#DC2626'
        }
        
        for item in difficulty_totals:
            difficulty = item['difficulty'].lower()
            difficulty_field = f'{difficulty}_solved'
            solved = getattr(profile, difficulty_field, 0)
            total = item['total']
            
            difficulties_data[difficulty] = {
                'level': item['difficulty'].capitalize(),
                'solved': solved,
                'total': total,
                'percentage': round((solved / total * 100)) if total > 0 else 0,
                'remaining': total - solved,
                'color': difficulty_colors.get(difficulty, '#6B7280')
            }
        
        return Response({
            'overview': {
                'total_problems_solved': profile.total_problems_solved,
                'total_problems_attempted': profile.total_problems_attempted,
                'total_submissions': profile.total_submissions,
                'total_score': profile.total_score,
            },
            'frameworks': frameworks_data,
            'difficulties': difficulties_data,
            'streaks': {
                'current': profile.current_streak_days,
                'longest': profile.longest_streak_days,
                'last_activity': profile.last_activity_date,
            }
        })

class HintUsageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HintUsage model.
    Track which hints users have viewed.
    """
    serializer_class = HintUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return hint usage for current user."""
        return HintUsage.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Record that user viewed a hint."""
        problem_id = request.data.get('problem')
        hint_index = request.data.get('hint_index')
        
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response(
                {'detail': 'Problem not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if hint exists for this problem
        if hint_index >= len(problem.hints):
            return Response(
                {'detail': 'Hint index out of range'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or get hint usage
        hint_usage, created = HintUsage.objects.get_or_create(
            user=request.user,
            problem=problem,
            hint_index=hint_index
        )
        
        # Update user progress
        from submissions.models import UserProgress
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            problem=problem
        )
        progress.hints_viewed = HintUsage.objects.filter(
            user=request.user,
            problem=problem
        ).count()
        progress.save()
        
        serializer = self.get_serializer(hint_usage)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
