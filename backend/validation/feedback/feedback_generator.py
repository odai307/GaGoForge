"""
Feedback Generator - Convert validation results to user-friendly messages
OPTIMIZED VERSION with old format detection and better error messages
"""

from typing import Dict, List, Any


class FeedbackGenerator:
    """Generate user-friendly feedback from validation results"""
    
    @staticmethod
    def generate_feedback(validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate feedback messages from validation results
        
        Args:
            validation_results: Complete validation results
        
        Returns:
            list: [
                {
                    'type': 'error' | 'warning' | 'info' | 'success',
                    'message': str,
                    'line': int or None,
                    'column': int or None
                }
            ]
        """
        feedback = []
        
        # ====================================
        # 1. SYNTAX ERRORS (Highest Priority)
        # ====================================
        if not validation_results.get('parse_success'):
            error = validation_results.get('parse_error', 'Unknown syntax error')
            line = validation_results.get('error_line')
            feedback.append({
                'type': 'error',
                'message': f'❌ Syntax Error: {error}',
                'line': line,
                'column': validation_results.get('error_offset')
            })
            return feedback
        
        # ====================================
        # 2. CHECK FOR OLD FORMAT PROBLEM
        # ====================================
        structure_result = validation_results.get('structure', {})
        if FeedbackGenerator._is_old_format_error(structure_result):
            FeedbackGenerator._add_old_format_warning(feedback, structure_result)
            return feedback
        
        # ====================================
        # 3. OVERALL VERDICT MESSAGE
        # ====================================
        verdict = validation_results.get('verdict')
        total_score = validation_results.get('total_score', 0)
        difficulty = validation_results.get('difficulty', 'unknown')
        
        if verdict == 'accepted':
            feedback.append({
                'type': 'success',
                'message': f'🎉 Solution Accepted! Score: {total_score:.1f}/100 ({difficulty.capitalize()} level)',
                'line': None,
                'column': None
            })
        elif verdict == 'partially_passed':
            feedback.append({
                'type': 'warning',
                'message': f'⚠️ Partially Correct. Score: {total_score:.1f}/100. Review the feedback below to improve.',
                'line': None,
                'column': None
            })
        else:
            feedback.append({
                'type': 'error',
                'message': f'❌ Solution Failed. Score: {total_score:.1f}/100. Please fix the errors below.',
                'line': None,
                'column': None
            })
        
        # ====================================
        # 4. COMPONENT-LEVEL FEEDBACK
        # ====================================
        
        # Import feedback
        imports_result = validation_results.get('imports', {})
        if imports_result:
            FeedbackGenerator._add_component_feedback(
                feedback, 
                imports_result, 
                'Imports',
                '📦'
            )
        
        # Structure feedback
        if structure_result:
            FeedbackGenerator._add_component_feedback(
                feedback, 
                structure_result, 
                'Structure',
                '🏗️'
            )
        
        # Behavior feedback
        behavior_result = validation_results.get('behavior', {})
        if behavior_result:
            FeedbackGenerator._add_component_feedback(
                feedback, 
                behavior_result, 
                'Behavior',
                '⚡'
            )
        
        # Semantic feedback (Pro level)
        semantic_result = validation_results.get('semantic', {})
        if semantic_result and semantic_result.get('patterns_checked'):
            FeedbackGenerator._add_semantic_feedback(feedback, semantic_result)
        
        # ====================================
        # 5. HELPFUL HINTS (if score is low)
        # ====================================
        if total_score < 50:
            FeedbackGenerator._add_helpful_hints(feedback, validation_results)
        
        return feedback
    
    @staticmethod
    def _is_old_format_error(structure_result: Dict) -> bool:
        """Check if structure validation failed due to old format"""
        details = structure_result.get('details', [])
        if not details:
            return False
        
        # Check if first detail mentions old format
        first_detail = str(details[0])
        return 'PROBLEM DEFINITION ERROR' in first_detail or 'outdated validation format' in first_detail
    
    @staticmethod
    def _add_old_format_warning(feedback: List, structure_result: Dict):
        """Add special warning for old format problems"""
        details = structure_result.get('details', [])
        
        feedback.append({
            'type': 'error',
            'message': '🚨 PROBLEM CONFIGURATION ERROR',
            'line': None,
            'column': None
        })
        
        feedback.append({
            'type': 'warning',
            'message': '⚠️ This problem uses an outdated validation format and cannot be graded.',
            'line': None,
            'column': None
        })
        
        # Add specific details from validator
        for detail in details:
            if 'Expected format' in detail:
                feedback.append({
                    'type': 'info',
                    'message': f'ℹ️ {detail}',
                    'line': None,
                    'column': None
                })
        
        feedback.append({
            'type': 'info',
            'message': '💡 What to do: Contact the course administrator to update this problem.',
            'line': None,
            'column': None
        })
        
        feedback.append({
            'type': 'info',
            'message': '📚 For admins: Update the validation_spec to use "classes": [{"name": "...", "methods": [...]}] format',
            'line': None,
            'column': None
        })
    
    @staticmethod
    def _add_component_feedback(feedback: List, component_result: Dict, 
                                component_name: str, icon: str):
        """Add feedback for a validation component"""
        if not component_result:
            return
        
        passed = component_result.get('passed', False)
        score = component_result.get('score', 0)
        details = component_result.get('details', [])
        
        # Component header
        status_icon = '✅' if passed else '⚠️'
        feedback.append({
            'type': 'info' if passed else 'warning',
            'message': f'{icon} {component_name}: {status_icon} Score: {score:.1f}/100',
            'line': None,
            'column': None
        })
        
        # Component details with smart formatting
        for detail in details:
            if not isinstance(detail, str):
                continue
            
            # Determine message type based on content
            if detail.startswith('✓') or 'found' in detail.lower() and '✓' in detail:
                msg_type = 'success'
            elif detail.startswith('✗') or 'missing' in detail.lower() or 'not found' in detail.lower():
                msg_type = 'error'
            elif detail.startswith('⚠️') or detail.startswith('ℹ️'):
                msg_type = 'info'
            else:
                msg_type = 'info'
            
            # Add indentation for sub-items
            indent = ''
            if detail.startswith('  '):
                indent = '  '
            elif detail.startswith('    '):
                indent = '    '
            
            feedback.append({
                'type': msg_type,
                'message': f'{indent}{detail.strip()}',
                'line': None,
                'column': None
            })
    
    @staticmethod
    def _add_semantic_feedback(feedback: List, semantic_result: Dict):
        """Add feedback for semantic validation (Pro level)"""
        feedback.append({
            'type': 'info',
            'message': '🎯 Advanced Pattern Analysis:',
            'line': None,
            'column': None
        })
        
        patterns_checked = semantic_result.get('patterns_checked', [])
        details = semantic_result.get('details', [])
        
        # Add patterns checked info
        if patterns_checked:
            feedback.append({
                'type': 'info',
                'message': f'  Patterns analyzed: {", ".join(patterns_checked)}',
                'line': None,
                'column': None
            })
        
        # Add detailed results
        for detail in details:
            if detail.startswith('✓'):
                feedback.append({
                    'type': 'success',
                    'message': f'  {detail}',
                    'line': None,
                    'column': None
                })
            elif detail.startswith('✗'):
                feedback.append({
                    'type': 'warning',
                    'message': f'  {detail}',
                    'line': None,
                    'column': None
                })
            else:
                feedback.append({
                    'type': 'info',
                    'message': f'  {detail}',
                    'line': None,
                    'column': None
                })
    
    @staticmethod
    def _add_helpful_hints(feedback: List, validation_results: Dict):
        """Add helpful hints when score is very low"""
        hints = []
        
        # Check imports
        imports_result = validation_results.get('imports', {})
        if imports_result.get('score', 0) < 50:
            hints.append('💡 Tip: Check that all required imports are included at the top of your file')
        
        # Check structure
        structure_result = validation_results.get('structure', {})
        if structure_result.get('score', 0) < 50:
            hints.append('💡 Tip: Make sure your class/function names match the requirements exactly')
            hints.append('💡 Tip: Check that you\'ve implemented all required methods/functions')
        
        # Check behavior
        behavior_result = validation_results.get('behavior', {})
        if behavior_result.get('score', 0) < 50:
            hints.append('💡 Tip: Review the problem requirements - your code may be missing key functionality')
        
        # Add hints to feedback
        if hints:
            feedback.append({
                'type': 'info',
                'message': '',
                'line': None,
                'column': None
            })
            
            for hint in hints:
                feedback.append({
                    'type': 'info',
                    'message': hint,
                    'line': None,
                    'column': None
                })
    
    @staticmethod
    def format_feedback_for_display(feedback: List[Dict[str, Any]]) -> str:
        """
        Format feedback list as plain text for display
        Useful for logging or text-based interfaces
        """
        lines = []
        
        for item in feedback:
            msg_type = item.get('type', 'info')
            message = item.get('message', '')
            line = item.get('line')
            
            # Add line number if present
            line_info = f" (Line {line})" if line else ""
            
            # Format based on type
            if msg_type == 'error':
                prefix = '❌'
            elif msg_type == 'warning':
                prefix = '⚠️'
            elif msg_type == 'success':
                prefix = '✅'
            else:
                prefix = 'ℹ️'
            
            lines.append(f"{prefix} {message}{line_info}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def get_score_breakdown(validation_results: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract score breakdown for analytics/display
        
        Returns:
            dict: {
                'imports': 85.5,
                'structure': 100.0,
                'behavior': 75.0,
                'total': 82.3
            }
        """
        breakdown = {
            'imports': validation_results.get('imports', {}).get('score', 0),
            'structure': validation_results.get('structure', {}).get('score', 0),
            'behavior': validation_results.get('behavior', {}).get('score', 0),
            'total': validation_results.get('total_score', 0)
        }
        
        # Add semantic if present (pro level)
        if 'semantic' in validation_results:
            breakdown['semantic'] = validation_results['semantic'].get('score', 0)
        
        return breakdown
    
    @staticmethod
    def get_failed_checks(validation_results: Dict[str, Any]) -> List[str]:
        """
        Extract list of failed checks for quick review
        
        Returns:
            list: ['Missing import: rest_framework', 'Method post missing', ...]
        """
        failed_checks = []
        
        for component in ['imports', 'structure', 'behavior', 'semantic']:
            component_result = validation_results.get(component, {})
            if not component_result:
                continue
            
            details = component_result.get('details', [])
            for detail in details:
                if isinstance(detail, str) and ('✗' in detail or 'missing' in detail.lower()):
                    # Clean up the message
                    clean_detail = detail.replace('✗', '').strip()
                    failed_checks.append(clean_detail)
        
        return failed_checks
    
    @staticmethod
    def should_show_hints(validation_results: Dict[str, Any]) -> bool:
        """Determine if hints should be shown to user"""
        total_score = validation_results.get('total_score', 0)
        attempt_number = validation_results.get('attempt_number', 1)
        
        # Show hints if:
        # - Score is below 50, OR
        # - Score is below 70 and it's their 3rd+ attempt
        return total_score < 50 or (total_score < 70 and attempt_number >= 3)
    
    @staticmethod
    def generate_summary(validation_results: Dict[str, Any]) -> str:
        """
        Generate a one-line summary of the validation
        Useful for notifications or quick status display
        """
        verdict = validation_results.get('verdict', 'unknown')
        score = validation_results.get('total_score', 0)
        
        if verdict == 'accepted':
            return f"✅ Accepted ({score:.0f}/100)"
        elif verdict == 'partially_passed':
            return f"⚠️ Partial ({score:.0f}/100)"
        elif verdict == 'syntax_error':
            return "❌ Syntax Error"
        else:
            return f"❌ Failed ({score:.0f}/100)"