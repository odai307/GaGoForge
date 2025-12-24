"""
Score Aggregator - Combine all component scores
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger('validation')


class ScoreAggregator:
    """Aggregate scores from all validation components"""
    
    @staticmethod
    def aggregate_scores(component_scores: List[Dict[str, Any]], passing_score: float) -> Dict[str, Any]:
        """
        Aggregate component scores into final score
        
        Args:
            component_scores: List of scores from imports, structure, behavior
            passing_score: Minimum score to pass (e.g., 80.0)
        
        Returns:
            dict: {
                'total_score': float (0-100),
                'passing_score': float,
                'passed': bool,
                'verdict': str,
                'breakdown': dict
            }
        """
        logger.debug(f"Aggregating {len(component_scores)} components")
        
        # Calculate total score by summing weighted scores
        # Each weighted score is already (raw_score * weight) where weight is a decimal (0-1)
        # So total_score = sum(weighted_scores) which gives a value between 0-100
        total_score = sum(comp['weighted_score'] for comp in component_scores)
        
        # Ensure total score doesn't exceed 100
        total_score = min(total_score, 100.0)
        
        # Determine verdict
        if total_score >= passing_score:
            verdict = 'accepted'
        elif total_score >= passing_score * 0.6:
            verdict = 'partially_passed'
        else:
            verdict = 'failed'
        
        # Log detailed score breakdown
        score_details = []
        for comp in component_scores:
            score_details.append(
                f"{comp['component']}: raw={comp['raw_score']:.1f}, "
                f"weight={comp['weight']}, weighted={comp['weighted_score']:.1f}"
            )
        
        logger.debug(f"Score breakdown: {', '.join(score_details)}")
        logger.debug(f"Total: {total_score:.2f}/{passing_score} → {verdict}")
        
        # Create detailed breakdown for frontend display
        breakdown = {}
        for comp in component_scores:
            breakdown[comp['component']] = {
                'raw_score': round(comp['raw_score'], 2),
                'weight': comp['weight'],
                'weighted_score': round(comp['weighted_score'], 2),
                'passed': comp.get('passed', comp['raw_score'] >= 70.0),  # Default passing threshold
                'max_possible': round(comp['weight'] * 100, 2)  # Maximum possible score for this component
            }
        
        # Add summary to breakdown
        breakdown['summary'] = {
            'total_score': round(total_score, 2),
            'passing_score': passing_score,
            'components_count': len(component_scores),
            'components_passed': sum(1 for comp in component_scores if comp.get('passed', False))
        }
        
        return {
            'total_score': round(total_score, 2),
            'passing_score': passing_score,
            'passed': total_score >= passing_score,
            'verdict': verdict,
            'breakdown': breakdown
        }
    
    @staticmethod
    def calculate_weighted_score(raw_score: float, weight: float) -> float:
        """
        Calculate weighted score for a component
        
        Args:
            raw_score: Component score (0-100)
            weight: Component weight (0-1)
            
        Returns:
            float: Weighted score contribution to total
        """
        # Convert raw_score to decimal (0-1) then multiply by weight
        # This gives the component's contribution to the total score
        weighted = (raw_score / 100.0) * weight * 100
        return round(weighted, 2)