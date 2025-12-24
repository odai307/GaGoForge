"""
Import Scorer - Calculate import validation score
"""

from typing import Dict, Any


class ImportScorer:
    """Calculate score for import validation"""
    
    @staticmethod
    def calculate_score(import_results: Dict[str, Any], weight: float) -> Dict[str, Any]:
        """
        Calculate weighted score for imports
        
        Args:
            import_results: Results from ImportMatcher
            weight: Weight percentage (e.g., 20.0 for 20%)
        
        Returns:
            dict: {
                'component': 'imports',
                'raw_score': float (0-100),
                'weight': float,
                'weighted_score': float,
                'passed': bool
            }
        """
        raw_score = import_results.get('score', 0.0)
        weighted_score = (raw_score * weight) / 100.0
        
        return {
            'component': 'imports',
            'raw_score': raw_score,
            'weight': weight,
            'weighted_score': round(weighted_score, 2),
            'passed': import_results.get('passed', False),
            'details': import_results.get('details', [])
        }