import logging
from django.utils import timezone
from datetime import date
from submissions.models import Submission
from submissions.models import UserProgress

logger = logging.getLogger('validation')

class UserProfileService:
    @staticmethod
    def update_profile_on_submission(submission):
        """Update user profile stats after submission"""
        user = submission.user
        profile = user.profile
        problem = submission.problem
        
        profile.total_submissions += 1
        
        if submission.attempt_number == 1:
            profile.total_problems_attempted += 1
        
        if submission.verdict == 'accepted':
            # Check if this is first time solving
            solved_before = UserProgress.objects.filter(
                user=user,
                problem=problem,
                is_solved=True
            ).exclude(best_submission_id=submission.submission_id).exists()
            
            if not solved_before:
                profile.total_problems_solved += 1
                profile.total_score += int(submission.score)
                
                # Update difficulty stats
                difficulty = problem.difficulty.lower()
                difficulty_field = f'{difficulty}_solved'
                if hasattr(profile, difficulty_field):
                    current = getattr(profile, difficulty_field, 0) or 0
                    setattr(profile, difficulty_field, current + 1)
                
                # FIXED: Update framework stats in JSONField
                framework = problem.framework.name.lower()
                
                # Initialize framework_stats if needed
                if not profile.framework_stats:
                    profile.framework_stats = {}
                
                # Increment framework count
                current_count = profile.framework_stats.get(framework, 0)
                profile.framework_stats[framework] = current_count + 1
                
                logger.info(f"Stats updated: {user.username} - {profile.total_problems_solved} solved, {framework}: {profile.framework_stats[framework]}")
        
        profile.save()
        return profile    
    
    @staticmethod
    def update_streak(user):
        """Update user's solving streak"""
        profile = user.profile
        today = date.today()
        
        # Check if solved today
        today_solved = Submission.objects.filter(
            user=user,
            verdict='accepted',
            submitted_at__date=today
        ).exists()
        
        if not today_solved:
            return profile
        
        # Call the model's update_streak method with today's date
        profile.update_streak(today)
        
        logger.info(f"Streak updated: {user.username} - {profile.current_streak_days} days 🔥")
        
        return profile