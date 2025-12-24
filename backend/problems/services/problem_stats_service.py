import logging

logger = logging.getLogger('validation')

class ProblemStatsService:
    @staticmethod
    def update_problem_stats(submission):
        """Update problem statistics after submission"""
        problem = submission.problem
        
        problem.total_submissions += 1
        
        if submission.verdict == 'accepted':
            problem.accepted_submissions += 1
        
        # Recalculate acceptance rate
        if problem.total_submissions > 0:
            problem.acceptance_rate = (
                problem.accepted_submissions / problem.total_submissions
            ) * 100
        
        problem.save(update_fields=['total_submissions', 'accepted_submissions', 'acceptance_rate'])
        
        logger.debug(f"Problem stats: {problem.problem_id} - {problem.acceptance_rate:.1f}% acceptance")
        
        return problem
