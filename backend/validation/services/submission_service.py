"""
Submission Service - Main orchestrator for code validation
Uses tiered validation engine for difficulty-aware validation
"""

from typing import Dict, Any
from django.utils import timezone
import time
import logging

logger = logging.getLogger('validation')

from validation.services.parser_service import ParserService
from validation.services.tiered_validator import EnhancedValidationEngine
from validation.scorers.aggregator import ScoreAggregator
from validation.feedback.feedback_generator import FeedbackGenerator


class SubmissionService:
    """Main service to validate code submissions using tiered validation"""
    
    @staticmethod
    def validate_submission(submission) -> Dict[str, Any]:
        """
        Validate a submission against problem requirements using tiered validation
        
        Args:
            submission: Submission model instance
        
        Returns:
            dict: Complete validation results
        """
        sub_id = str(submission.submission_id)[:8]
        logger.info(f"[{sub_id}] Starting validation")
        start = time.time()
        
        problem = submission.problem
        code = submission.code
        
        # DEBUG: Log the code being validated
        logger.debug(f"[{sub_id}] Code snippet: {code[:200]}...")
        
        # Determine language
        language = SubmissionService._determine_language(problem.framework.name)
        
        # Parse code
        parse_start = time.time()
        parsed_code = ParserService.parse_code(code, language)
        parse_ms = (time.time() - parse_start) * 1000
        logger.debug(f"[{sub_id}] Parse: {parse_ms:.0f}ms")
        
        # DEBUG: Log parsed imports for troubleshooting
        if parsed_code.get('success'):
            imports = parsed_code.get('imports', [])
            logger.debug(f"[{sub_id}] Parsed imports: {imports}")
            
            # Extract import details for debugging
            import_details = []
            for imp in imports:
                if imp['type'] == 'import':
                    import_details.append(f"import {imp['module']}")
                elif imp['type'] == 'from_import':
                    import_details.append(f"from {imp['module']} import {imp['name']}")
                elif imp['type'] == 'require':
                    import_details.append(f"require('{imp['module']}')")
            logger.debug(f"[{sub_id}] Import details: {import_details}")
        
        # If parsing failed, return syntax error
        if not parsed_code.get('success'):
            logger.warning(f"[{sub_id}] Parse failed: {parsed_code.get('error')}")
            return {
                'verdict': 'syntax_error',
                'score': 0.0,
                'parse_success': False,
                'parse_error': parsed_code.get('error'),
                'error_line': parsed_code.get('line'),
                'error_offset': parsed_code.get('offset'),
                'validation_results': {},
                'feedback': FeedbackGenerator.generate_feedback({
                    'parse_success': False,
                    'parse_error': parsed_code.get('error'),
                    'error_line': parsed_code.get('line'),
                    'error_offset': parsed_code.get('offset'),
                    'verdict': 'syntax_error',
                    'total_score': 0.0
                }),
                'matched_patterns': [],
                'execution_time_ms': parse_ms
            }
        
        # Prepare validation spec for tiered validator
        validation_spec = {
            'difficulty': problem.difficulty,
            'framework': problem.framework.name,
            'required_imports': problem.validation_spec.get('required_imports', []),
            'required_structure': problem.validation_spec.get('required_structure', {}),
            'behavior_patterns': problem.validation_spec.get('behavior_patterns', []),
            'scoring': {
                'import_weight': float(problem.import_weight),
                'structure_weight': float(problem.structure_weight),
                'behavior_weight': float(problem.behavior_weight)
            },
            'passing_score': float(problem.passing_score)
        }
        
        # DEBUG: Log validation spec for troubleshooting
        logger.debug(f"[{sub_id}] Validation spec - Difficulty: {validation_spec['difficulty']}, "
                    f"Required imports: {validation_spec['required_imports']}")
        
        # Run tiered validation engine
        validate_start = time.time()
        engine = EnhancedValidationEngine()
        tiered_results = engine.validate_submission(parsed_code, validation_spec, code)
        validate_ms = (time.time() - validate_start) * 1000
        logger.debug(f"[{sub_id}] Validation: {validate_ms:.0f}ms")
        
        # Check if there was an error in validation
        if 'error' in tiered_results:
            logger.error(f"[{sub_id}] Validation error: {tiered_results['error']}")
            return {
                'verdict': 'failed',
                'score': 0.0,
                'parse_success': True,
                'validation_error': tiered_results['error'],
                'validation_results': {},
                'feedback': [{
                    'type': 'error',
                    'message': tiered_results['error'],
                    'line': None,
                    'column': None
                }],
                'matched_patterns': [],
                'execution_time_ms': parse_ms + validate_ms
            }
        
        # Determine verdict based on score and passing threshold
        overall_score = tiered_results.get('overall_score', 0.0)
        passing_score = validation_spec['passing_score']
        
        if overall_score >= passing_score:
            verdict = 'accepted'
        elif overall_score >= passing_score * 0.6:
            verdict = 'partially_passed'
        else:
            verdict = 'failed'
        
        # Extract validation results for each component
        validation_results = {
            'imports': tiered_results.get('imports', {}),
            'structure': tiered_results.get('structure', {}),
            'behavior': tiered_results.get('behavior', {}),
            'validator_used': tiered_results.get('validator_used', 'unknown')
        }
        
        # DEBUG: Log validation results for troubleshooting
        logger.debug(f"[{sub_id}] Validation results - "
                    f"Imports: {validation_results['imports'].get('score', 0):.1f}, "
                    f"Structure: {validation_results['structure'].get('score', 0):.1f}, "
                    f"Behavior: {validation_results['behavior'].get('score', 0):.1f}, "
                    f"Overall: {overall_score:.1f}")
        
        # Add semantic results if present (for Pro level)
        if 'semantic' in tiered_results:
            validation_results['semantic'] = tiered_results['semantic']
        
        # Add framework-specific results if present
        for key in tiered_results:
            if key.endswith('_specific'):
                validation_results[key] = tiered_results[key]
        
        # Generate user-friendly feedback
        feedback_data = {
            'parse_success': True,
            'imports': validation_results.get('imports', {}),
            'structure': validation_results.get('structure', {}),
            'behavior': validation_results.get('behavior', {}),
            'semantic': validation_results.get('semantic', {}),
            'verdict': verdict,
            'total_score': overall_score,
            'difficulty': problem.difficulty,
            'framework': problem.framework.name
        }
        
        feedback = FeedbackGenerator.generate_feedback(feedback_data)
        
        total_ms = (time.time() - start) * 1000
        logger.info(f"[{sub_id}] Complete: {verdict} ({overall_score:.1f}) in {total_ms:.0f}ms")
        
        # Prepare final results
        results = {
            'verdict': verdict,
            'score': round(overall_score, 2),
            'parse_success': True,
            'validation_results': validation_results,
            'feedback': feedback,
            'matched_patterns': tiered_results.get('matched_patterns', []),
            'execution_time_ms': parse_ms + validate_ms,
            'validator_info': {
                'validator_used': tiered_results.get('validator_used', 'unknown'),
                'difficulty': problem.difficulty,
                'framework': problem.framework.name
            }
        }
        
        return results
    
    @staticmethod
    def _determine_language(framework_name: str) -> str:
        """Determine programming language from framework name"""
        language_map = {
            'django': 'python',
            'react': 'javascript',
            'angular': 'typescript',
            'express': 'javascript'
        }
        return language_map.get(framework_name, 'python')