"""
Structure Scorer - Calculate structure validation score
"""

from typing import Dict, Any


class StructureScorer:
    """Calculate score for structure validation"""
    
    @staticmethod
    def calculate_score(structure_results: Dict[str, Any], weight: float) -> Dict[str, Any]:
        """
        Calculate weighted score for structure
        
        Args:
            structure_results: Results from StructureMatcher
            weight: Weight percentage (e.g., 35.0 for 35%)
        
        Returns:
            dict: {
                'component': 'structure',
                'raw_score': float (0-100),
                'weight': float,
                'weighted_score': float,
                'passed': bool
            }
        """
        raw_score = structure_results.get('score', 0.0)
        weighted_score = (raw_score * weight) / 100.0
        
        return {
            'component': 'structure',
            'raw_score': raw_score,
            'weight': weight,
            'weighted_score': round(weighted_score, 2),
            'passed': structure_results.get('passed', False),
            'details': structure_results.get('details', [])
        }