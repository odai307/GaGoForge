import logging
from django.utils import timezone
from submissions.models import UserProgress, Submission

logger = logging.getLogger('validation')

class UserProgressService:
    @staticmethod
    def update_progress(submission):
        """Update user progress after submission"""
        user = submission.user
        problem = submission.problem
        
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            problem=problem,
            defaults={
                'is_attempted': True,
                'first_attempt_at': timezone.now(),
                'total_attempts': 1,
                'best_score': submission.score,
                'best_submission': submission,
            }
        )
        
        if not created:
            progress.total_attempts += 1
            progress.last_attempt_at = timezone.now()
            
            if submission.score > progress.best_score:
                progress.best_score = submission.score
                progress.best_submission = submission
        
        if submission.verdict == 'accepted' and not progress.is_solved:
            progress.is_solved = True
            progress.solved_at = timezone.now()
            logger.info(f"Problem solved: {user.username} - {problem.title}")
        
        progress.save()
        return progress
