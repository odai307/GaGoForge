"""
Behavior Scorer - Calculate behavior validation score
"""

from typing import Dict, Any


class BehaviorScorer:
    """Calculate score for behavior validation"""
    
    @staticmethod
    def calculate_score(behavior_results: Dict[str, Any], weight: float) -> Dict[str, Any]:
        """
        Calculate weighted score for behavior
        
        Args:
            behavior_results: Results from BehaviorMatcher
            weight: Weight percentage (e.g., 45.0 for 45%)
        
        Returns:
            dict: {
                'component': 'behavior',
                'raw_score': float (0-100),
                'weight': float,
                'weighted_score': float,
                'passed': bool
            }
        """
        raw_score = behavior_results.get('score', 0.0)
        weighted_score = (raw_score * weight) / 100.0
        
        return {
            'component': 'behavior',
            'raw_score': raw_score,
            'weight': weight,
            'weighted_score': round(weighted_score, 2),
            'passed': behavior_results.get('passed', False),
            'details': behavior_results.get('details', [])
        }