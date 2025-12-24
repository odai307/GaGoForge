"""
Enhanced Tiered Validation Engine with Framework-Specific Semantic Analysis
Supports: Django (Python) and React/Express/Angular (JavaScript)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Tuple
import re
import logging
from enum import Enum

logger = logging.getLogger('validation')


# ===== Base Validator Classes (ADDED BACK) =====

class BaseValidator(ABC):
    """Base validator interface - UNCHANGED"""
    
    @abstractmethod
    def validate(self, parsed_code: Dict[str, Any], validation_spec: Dict[str, Any], code: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def can_handle(self, difficulty: str, framework: str) -> bool:
        pass

    def _extract_all_imports(self, parsed_code: Dict) -> List[str]:
        """Extract all imports - works with existing parser format"""
        imports = []
        
        for imp in parsed_code.get('imports', []):
            imp_type = imp.get('type')
            
            if imp_type == 'import':
                # Python: import module
                imports.append(imp.get('module', ''))
            elif imp_type == 'from_import':
                # Python: from module import name
                module = imp.get('module', '')
                name = imp.get('name', '')
                imports.append(f"{module}.{name}")
                imports.append(module)
                imports.append(name)
            elif imp_type == 'require':
                # JS: const x = require('module')
                imports.append(imp.get('module', ''))
            else:
                # JS ES6: import { x } from 'module'
                imports.append(imp.get('module', ''))
                for spec in imp.get('specifiers', []):
                    imports.append(spec.get('local', ''))
                    if spec.get('imported'):
                        imports.append(spec['imported'])
        
        return imports

    def _is_import_match_enhanced(self, required: str, found_imports: List[str]) -> bool:
        """Enhanced import matching - UNCHANGED"""
        if required.startswith('.'):
            required_abs = required.lstrip('.')
            variations = [
                required_abs,
                required_abs.replace('.', '_'),
                required_abs.split('.')[-1]
            ]
            return any(
                any(var in found or found.endswith(var) for var in variations)
                for found in found_imports
            )
        
        required_parts = required.split('.')
        return any(
            required in found or 
            found in required or
            all(part in found for part in required_parts)
            for found in found_imports
        )

    def _validate_imports_common(self, parsed_code: Dict, required_imports: List[str]) -> Dict[str, Any]:
        """Common import validation - UNCHANGED"""
        if not required_imports:
            return {
                'passed': True,
                'score': 100.0,
                'details': ["No imports required for validation"]
            }
        
        found_imports = self._extract_all_imports(parsed_code)
        missing = []
        
        for required in required_imports:
            if not self._is_import_match_enhanced(required, found_imports):
                missing.append(required)
        
        score = 100.0 if not missing else max(0.0, (len(required_imports) - len(missing)) / len(required_imports) * 100)
        
        return {
            'passed': len(missing) == 0,
            'score': score,
            'details': [f"Missing imports: {missing}"] if missing else ["All imports present"]
        }


class BeginnerValidator(BaseValidator):
    """Enhanced beginner validator with basic semantic analysis"""
    
    def can_handle(self, difficulty: str, framework: str) -> bool:
        return difficulty in ['beginner', 'easy']
    
    def validate(self, parsed_code: Dict[str, Any], validation_spec: Dict[str, Any], code: str) -> Dict[str, Any]:
        # Get framework for basic semantic analysis
        framework = validation_spec.get('framework', 'unknown')
        
        # Add lightweight semantic analysis
        if framework != 'unknown':
            analyzer = FrameworkAnalyzerFactory.create_analyzer(framework)
            semantics = analyzer.analyze(code, parsed_code)
            parsed_code['semantics'] = semantics
            parsed_code['framework'] = framework
        
        return {
            'imports': self._validate_imports_common(parsed_code, validation_spec.get('required_imports', [])),
            'structure': self._validate_structure_enhanced(parsed_code, validation_spec.get('required_structure', {})),
            'behavior': self._validate_behavior_enhanced(parsed_code, validation_spec.get('behavior_patterns', []), code)
        }
    
    def _validate_structure_enhanced(self, parsed_code: Dict, required_structure: Dict) -> Dict[str, Any]:
        """
        Enhanced structure validation with basic semantic checks
        """
        details = []
        checks_passed = 0
        total_checks = 0
        
        framework = parsed_code.get('framework', 'unknown')
        semantics = parsed_code.get('semantics', {})
        
        # ====================================
        # CLASS VALIDATION
        # ====================================
        if 'classes' in required_structure and required_structure['classes']:
            for class_spec in required_structure['classes']:
                class_name = class_spec.get('name') if isinstance(class_spec, dict) else class_spec
                
                # Check if class exists
                total_checks += 1
                found_class = next((cls for cls in parsed_code.get('classes', []) 
                                if cls['name'] == class_name), None)
                
                if not found_class:
                    details.append(f"✗ Class '{class_name}' not found")
                    continue
                
                checks_passed += 1
                details.append(f"✓ Class '{class_name}' found")
                
                # If class_spec is detailed (dict), validate deeper structure
                if isinstance(class_spec, dict):
                    # Check parent class (inheritance)
                    if 'parent_class' in class_spec:
                        total_checks += 1
                        expected_parent = class_spec['parent_class']
                        actual_parents = found_class.get('bases', [])
                        
                        if expected_parent in actual_parents or any(expected_parent in p for p in actual_parents):
                            checks_passed += 1
                            details.append(f"  ✓ Inherits from '{expected_parent}'")
                        else:
                            details.append(f"  ✗ Does not inherit from '{expected_parent}' (found: {actual_parents})")
                    
                    # Check required methods
                    if 'methods' in class_spec:
                        class_methods = [m['name'] for m in found_class.get('methods', [])]
                        
                        for required_method in class_spec['methods']:
                            total_checks += 1
                            if required_method in class_methods:
                                checks_passed += 1
                                details.append(f"  ✓ Method '{required_method}' exists")
                            else:
                                details.append(f"  ✗ Method '{required_method}' missing")
                    
                    # BEGINNER-LEVEL SEMANTIC CHECKS for Django
                    if framework == 'django' and semantics:
                        if class_name.endswith('Model') or 'Model' in class_spec.get('parent_class', ''):
                            # Basic check: Does the model have any fields?
                            model_fields = semantics.get('model_fields', [])
                            if model_fields:
                                details.append(f"  ✓ Model has {len(model_fields)} field(s)")
                            else:
                                details.append(f"  ⚠ Model has no fields defined")
                    
                    # BEGINNER-LEVEL SEMANTIC CHECKS for React
                    if framework == 'react' and semantics:
                        if 'Component' in class_spec.get('parent_class', ''):
                            # Check if render method returns JSX
                            class_methods_full = found_class.get('methods', [])
                            render_method = next((m for m in class_methods_full if m['name'] == 'render'), None)
                            if render_method:
                                details.append(f"  ✓ Component has render() method")
        
        # ====================================
        # FUNCTION VALIDATION
        # ====================================
        if 'functions' in required_structure and required_structure['functions']:
            for func_spec in required_structure['functions']:
                func_name = func_spec.get('name') if isinstance(func_spec, dict) else func_spec
                
                # Check if function exists
                total_checks += 1
                found_func = next((f for f in parsed_code.get('functions', []) 
                                if f['name'] == func_name), None)
                
                if not found_func:
                    details.append(f"✗ Function '{func_name}' not found")
                    continue
                
                checks_passed += 1
                details.append(f"✓ Function '{func_name}' found")
                
                # If func_spec is detailed (dict), validate deeper structure
                if isinstance(func_spec, dict):
                    # Check parameters
                    if 'params' in func_spec:
                        total_checks += 1
                        expected_params = func_spec['params']
                        actual_params = found_func.get('params', [])
                        
                        if all(param in actual_params for param in expected_params):
                            checks_passed += 1
                            details.append(f"  ✓ Has correct parameters: {expected_params}")
                        else:
                            details.append(f"  ✗ Parameter mismatch (expected: {expected_params}, got: {actual_params})")
                    
                    # Check if it's a React component (starts with uppercase)
                    if func_spec.get('type') == 'functional_component':
                        total_checks += 1
                        if func_name[0].isupper():
                            checks_passed += 1
                            details.append(f"  ✓ Follows React component naming convention")
                            
                            # BEGINNER-LEVEL: Check if component uses hooks
                            if framework == 'react' and semantics:
                                hook_calls = semantics.get('hook_calls', [])
                                if hook_calls:
                                    hook_names = list(set(h['hook'] for h in hook_calls))
                                    details.append(f"  ✓ Uses hooks: {', '.join(hook_names[:3])}")
                        else:
                            details.append(f"  ✗ Component name should start with uppercase")
                    
                    # Check for PropTypes (React specific)
                    if func_spec.get('has_prop_types'):
                        total_checks += 1
                        # Simple check: look for PropTypes in code
                        if 'PropTypes' in str(parsed_code.get('imports', [])):
                            checks_passed += 1
                            details.append(f"  ✓ PropTypes imported")
                        else:
                            details.append(f"  ⚠ PropTypes not imported")
                    
                    # Check for export
                    if func_spec.get('has_export'):
                        total_checks += 1
                        exports = parsed_code.get('exports', [])
                        if any(exp.get('declaration') == func_name for exp in exports):
                            checks_passed += 1
                            details.append(f"  ✓ Function is exported")
                        else:
                            details.append(f"  ✗ Function is not exported")
        
        # ====================================
        # CALCULATE SCORE
        # ====================================
        
        if total_checks == 0:
            return {
                'passed': False,
                'score': 0.00,
                'details': ["⚠️ No structure validation performed - check validation spec format"]
            }
        
        score = (checks_passed / total_checks) * 100
        
        return {
            'passed': checks_passed == total_checks,
            'score': score,
            'details': details
        }
    
    def _validate_behavior_enhanced(self, parsed_code: Dict, behavior_patterns: List, code: str) -> Dict[str, Any]:
        """
        Enhanced behavior validation with basic semantic understanding
        """
        if not behavior_patterns:
            return {'passed': True, 'score': 100.00, 'details': ["No behavior patterns required"]}
        
        framework = parsed_code.get('framework', 'unknown')
        semantics = parsed_code.get('semantics', {})
        
        details = []
        matched = 0
        total = len(behavior_patterns)
        
        for pattern in behavior_patterns:
            if isinstance(pattern, str):
                # Legacy string pattern - use enhanced keyword matching
                result = self._validate_string_pattern_enhanced(pattern, code, semantics, framework)
                if result:
                    matched += 1
                    details.append(f"✓ {pattern}")
                else:
                    details.append(f"✗ {pattern}")
            
            elif isinstance(pattern, dict) and pattern.get('type'):
                # Structured pattern - use basic semantic validation
                result = self._validate_structured_pattern_basic(pattern, semantics, code, framework)
                if result['passed']:
                    matched += 1
                    details.append(f"✓ {result['message']}")
                else:
                    details.append(f"✗ {result['message']}")
            else:
                # Fallback to keyword matching
                pattern_str = pattern if isinstance(pattern, str) else str(pattern)
                keywords = [kw.lower() for kw in pattern_str.split() if len(kw) > 3]
                if any(keyword in code.lower() for keyword in keywords):
                    matched += 1
                    details.append(f"✓ {pattern_str}")
                else:
                    details.append(f"✗ {pattern_str}")
        
        score = (matched / total * 100) if total > 0 else 0
        
        return {
            'passed': matched == total,
            'score': score,
            'details': details
        }
    
    def _validate_string_pattern_enhanced(self, pattern: str, code: str, semantics: Dict, framework: str) -> bool:
        """
        Enhanced string pattern matching with semantic awareness
        """
        pattern_lower = pattern.lower()
        code_lower = code.lower()
        
        # Extract keywords (words > 3 chars)
        keywords = [kw for kw in pattern.split() if len(kw) > 3]
        
        # Basic keyword matching
        basic_match = any(keyword.lower() in code_lower for keyword in keywords)
        
        if not basic_match:
            return False
        
        # If we have semantics, do enhanced validation
        if not semantics:
            return True
        
        # DJANGO ENHANCED CHECKS
        if framework == 'django':
            # Check for model field patterns
            if 'field' in pattern_lower and any(field_type in pattern_lower for field_type in ['char', 'integer', 'foreign', 'boolean', 'date']):
                model_fields = semantics.get('model_fields', [])
                return len(model_fields) > 0
            
            # Check for filter/queryset patterns
            if 'filter' in pattern_lower or 'queryset' in pattern_lower:
                queryset_ops = semantics.get('queryset_operations', [])
                return 'filter' in queryset_ops or 'all' in queryset_ops
            
            # Check for serializer patterns
            if 'serializer' in pattern_lower:
                serializer_classes = semantics.get('serializer_classes', [])
                return len(serializer_classes) > 0
        
        # REACT ENHANCED CHECKS
        elif framework == 'react':
            # Check for hook patterns
            if 'usestate' in pattern_lower:
                hook_calls = semantics.get('hook_calls', [])
                return any(h['hook'] == 'useState' for h in hook_calls)
            
            if 'useeffect' in pattern_lower:
                hook_calls = semantics.get('hook_calls', [])
                return any(h['hook'] == 'useEffect' for h in hook_calls)
            
            # Check for event handler patterns
            if 'onclick' in pattern_lower or 'onchange' in pattern_lower or 'event' in pattern_lower:
                event_handlers = semantics.get('event_handlers', [])
                return len(event_handlers) > 0
            
            # Check for JSX patterns
            if 'jsx' in pattern_lower or 'return' in pattern_lower:
                jsx_elements = semantics.get('jsx_elements', [])
                return len(jsx_elements) > 0
        
        # Default to keyword match
        return True
    
    def _validate_structured_pattern_basic(self, pattern: Dict, semantics: Dict, code: str, framework: str) -> Dict:
        """
        Basic structured pattern validation for beginners
        """
        pattern_type = pattern.get('type')
        
        # REACT PATTERNS
        if framework == 'react':
            if pattern_type == 'hook_call':
                hook_name = pattern.get('hook')
                hook_calls = semantics.get('hook_calls', [])
                matching = [h for h in hook_calls if h['hook'] == hook_name]
                
                if matching:
                    return {'passed': True, 'message': f"{hook_name} used"}
                else:
                    return {'passed': False, 'message': f"{hook_name} not found"}
            
            elif pattern_type == 'state_management':
                state_declarations = semantics.get('state_declarations', [])
                if state_declarations:
                    return {'passed': True, 'message': "State management found"}
                else:
                    return {'passed': False, 'message': "No state management"}
            
            elif pattern_type == 'event_handler':
                event_handlers = semantics.get('event_handlers', [])
                if event_handlers:
                    return {'passed': True, 'message': "Event handlers found"}
                else:
                    return {'passed': False, 'message': "No event handlers"}
            
            elif pattern_type == 'conditional_rendering':
                # Simple check for ternary or && operators
                if '?' in code and ':' in code:
                    return {'passed': True, 'message': "Conditional rendering found"}
                elif '&&' in code:
                    return {'passed': True, 'message': "Conditional rendering found"}
                else:
                    return {'passed': False, 'message': "No conditional rendering"}
        
        # DJANGO PATTERNS
        elif framework == 'django':
            if pattern_type == 'model_field':
                model_fields = semantics.get('model_fields', [])
                if model_fields:
                    return {'passed': True, 'message': f"Model fields found ({len(model_fields)})"}
                else:
                    return {'passed': False, 'message': "No model fields"}
            
            elif pattern_type == 'queryset_operation':
                queryset_ops = semantics.get('queryset_operations', [])
                operation = pattern.get('operation', 'any')
                
                if operation == 'any':
                    if queryset_ops:
                        return {'passed': True, 'message': f"Queryset operations: {', '.join(queryset_ops[:3])}"}
                    else:
                        return {'passed': False, 'message': "No queryset operations"}
                else:
                    if operation in queryset_ops:
                        return {'passed': True, 'message': f"Queryset .{operation}() found"}
                    else:
                        return {'passed': False, 'message': f"Queryset .{operation}() not found"}
            
            elif pattern_type == 'serializer':
                serializer_classes = semantics.get('serializer_classes', [])
                if serializer_classes:
                    return {'passed': True, 'message': "Serializer found"}
                else:
                    return {'passed': False, 'message': "No serializer"}
        
        # Fallback to keyword matching
        description = pattern.get('description', str(pattern))
        keywords = [kw.lower() for kw in description.split() if len(kw) > 3]
        if any(keyword in code.lower() for keyword in keywords):
            return {'passed': True, 'message': description}
        else:
            return {'passed': False, 'message': description}

# ===== Original Code Continues =====

class FrameworkType(Enum):
    """Supported framework types"""
    DJANGO = "django"
    REACT = "react"
    EXPRESS = "express"
    ANGULAR = "angular"
    NODEJS = "nodejs"
    UNKNOWN = "unknown"


class LanguageType(Enum):
    """Programming language types"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    UNKNOWN = "unknown"


class FrameworkAnalyzerFactory:
    """Factory to create framework-specific semantic analyzers"""
    
    @staticmethod
    def create_analyzer(framework: str):
        """Create appropriate analyzer for framework"""
        framework_lower = framework.lower()
        
        if framework_lower == FrameworkType.DJANGO.value:
            return DjangoSemanticAnalyzer()
        elif framework_lower == FrameworkType.REACT.value:
            return ReactSemanticAnalyzer()
        elif framework_lower == FrameworkType.EXPRESS.value:
            return ExpressSemanticAnalyzer()
        elif framework_lower == FrameworkType.ANGULAR.value:
            return AngularSemanticAnalyzer()
        elif framework_lower == FrameworkType.NODEJS.value:
            return NodeJSSemanticAnalyzer()
        else:
            return BaseSemanticAnalyzer()


class BaseSemanticAnalyzer(ABC):
    """Base class for all semantic analyzers"""
    
    @abstractmethod
    def analyze(self, code: str, parsed_code: Dict) -> Dict[str, Any]:
        """Analyze code and return semantic insights"""
        pass
    
    def _detect_language(self, code: str) -> LanguageType:
        """Detect programming language from code"""
        # Python detection
        if re.search(r'\bimport\s+|from\s+\w+\s+import|\bdef\s+\w+\s*\(|class\s+\w+', code):
            return LanguageType.PYTHON
        # TypeScript detection
        elif re.search(r'\binterface\s+\w+|type\s+\w+|:\s*\w+[\[\]]?', code):
            return LanguageType.TYPESCRIPT
        # JavaScript detection
        elif re.search(r'\bconst\s+|let\s+|var\s+|function\s+\w+|\bexport\s+', code):
            return LanguageType.JAVASCRIPT
        return LanguageType.UNKNOWN


class DjangoSemanticAnalyzer(BaseSemanticAnalyzer):
    """Semantic analyzer for Django framework"""
    
    def analyze(self, code: str, parsed_code: Dict) -> Dict[str, Any]:
        """Analyze Django code for semantic patterns"""
        semantics = {
            # Model-related patterns
            'model_fields': self._extract_model_fields(code),
            'model_meta': self._extract_model_meta(code),
            'model_relationships': self._extract_model_relationships(code),
            'model_methods': self._extract_model_methods(parsed_code),
            
            # View-related patterns
            'view_classes': self._extract_view_classes(parsed_code),
            'view_methods': self._extract_view_methods(code, parsed_code),
            'view_decorators': self._extract_view_decorators(code),
            'permission_classes': self._extract_permission_classes(code),
            
            # Authentication patterns
            'authentication_usage': self._extract_auth_usage(code),
            'permission_checks': self._extract_permission_checks(code),
            'group_permissions': self._extract_group_permissions(code),
            
            # Middleware patterns
            'middleware_classes': self._extract_middleware_classes(parsed_code),
            'middleware_methods': self._extract_middleware_methods(code),
            
            # Serializer patterns
            'serializer_fields': self._extract_serializer_fields(code),
            'serializer_classes': self._extract_serializer_classes(parsed_code),
            
            # ORM patterns
            'queryset_operations': self._extract_queryset_ops(code),
            'queryset_methods': self._extract_queryset_methods(code),
            
            # URL patterns
            'url_patterns': self._extract_url_patterns(code),
            'url_includes': self._extract_url_includes(code),
            
            # Template patterns
            'template_usage': self._extract_template_usage(code),
            'context_data': self._extract_context_data(code),
            
            # Form patterns
            'form_fields': self._extract_form_fields(code),
            'form_classes': self._extract_form_classes(parsed_code),
            
            # Signal patterns
            'signal_handlers': self._extract_signal_handlers(code),
            'signal_connections': self._extract_signal_connections(code),
            
            # Admin patterns
            'admin_classes': self._extract_admin_classes(parsed_code),
            'admin_registrations': self._extract_admin_registrations(code),
            
            # Test patterns
            'test_classes': self._extract_test_classes(parsed_code),
            'test_methods': self._extract_test_methods(code),
        }
        return semantics
    
    # ===== Django Semantic Extractors =====
    
    def _extract_model_fields(self, code: str) -> List[Dict]:
        """Extract Django model field definitions"""
        fields = []
        django_field_types = [
            'CharField', 'TextField', 'IntegerField', 'FloatField', 'DecimalField',
            'BooleanField', 'DateField', 'DateTimeField', 'EmailField', 'URLField',
            'ForeignKey', 'ManyToManyField', 'OneToOneField', 'ImageField', 'FileField',
            'AutoField', 'BigAutoField', 'BigIntegerField', 'BinaryField', 'DurationField',
            'GenericIPAddressField', 'PositiveIntegerField', 'PositiveSmallIntegerField',
            'SlugField', 'SmallIntegerField', 'TimeField', 'UUIDField'
        ]
        
        for field_type in django_field_types:
            pattern = rf'(\w+)\s*=\s*(models\.)?{field_type}\s*\(([^)]*)\)'
            for match in re.finditer(pattern, code, re.DOTALL):
                field_name, _, params = match.groups()
                fields.append({
                    'field_type': field_type,
                    'name': field_name,
                    'params': params.strip(),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        return fields
    
    def _extract_model_meta(self, code: str) -> Dict[str, Any]:
        """Extract Model Meta class information"""
        meta_info = {}
        
        # Extract Meta class patterns
        meta_pattern = r'class\s+Meta\s*:\s*(.*?)(?=\n\S|\Z)'
        meta_match = re.search(meta_pattern, code, re.DOTALL | re.IGNORECASE)
        
        if meta_match:
            meta_content = meta_match.group(1)
            # Extract Meta options
            options = {
                'verbose_name': self._extract_meta_option(meta_content, 'verbose_name'),
                'verbose_name_plural': self._extract_meta_option(meta_content, 'verbose_name_plural'),
                'ordering': self._extract_meta_option(meta_content, 'ordering'),
                'permissions': self._extract_meta_option(meta_content, 'permissions'),
                'unique_together': self._extract_meta_option(meta_content, 'unique_together'),
                'indexes': self._extract_meta_option(meta_content, 'indexes'),
                'constraints': self._extract_meta_option(meta_content, 'constraints'),
            }
            meta_info['options'] = {k: v for k, v in options.items() if v}
        
        return meta_info
    
    def _extract_meta_option(self, meta_content: str, option_name: str) -> Any:
        """Extract specific Meta option"""
        pattern = rf'{option_name}\s*=\s*(.+)'
        match = re.search(pattern, meta_content)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_model_relationships(self, code: str) -> List[Dict]:
        """Extract model relationship fields"""
        relationships = []
        
        relationship_patterns = [
            (r'(\w+)\s*=\s*models\.ForeignKey\s*\(([^)]*)\)', 'ForeignKey'),
            (r'(\w+)\s*=\s*models\.ManyToManyField\s*\(([^)]*)\)', 'ManyToManyField'),
            (r'(\w+)\s*=\s*models\.OneToOneField\s*\(([^)]*)\)', 'OneToOneField'),
        ]
        
        for pattern, rel_type in relationship_patterns:
            for match in re.finditer(pattern, code, re.DOTALL):
                field_name, params = match.groups()
                
                # Extract related model from params
                related_model = None
                if 'to=' in params:
                    model_match = re.search(r"to=['\"]([^'\"]+)['\"]", params)
                    if model_match:
                        related_model = model_match.group(1)
                elif ',' in params:
                    # First positional argument is usually the model
                    first_arg = params.split(',')[0].strip()
                    if "'" in first_arg or '"' in first_arg:
                        related_model = first_arg.strip("'\"")
                
                relationships.append({
                    'field_name': field_name,
                    'type': rel_type,
                    'related_model': related_model,
                    'params': params.strip(),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        return relationships
    
    def _extract_model_methods(self, parsed_code: Dict) -> List[Dict]:
        """Extract model methods from parsed code"""
        model_methods = []
        
        for cls in parsed_code.get('classes', []):
            if cls.get('name', '').endswith('Model') or 'models.Model' in cls.get('parent_class', ''):
                for method in cls.get('methods', []):
                    method_name = method.get('name', '')
                    if method_name.startswith('__') or method_name in ['save', 'delete', 'clean']:
                        model_methods.append({
                            'method_name': method_name,
                            'class_name': cls.get('name'),
                            'decorators': method.get('decorators', [])
                        })
        
        return model_methods
    
    def _extract_view_classes(self, parsed_code: Dict) -> List[Dict]:
        """Extract Django view classes"""
        view_classes = []
        
        view_base_classes = [
            'View', 'TemplateView', 'ListView', 'DetailView', 
            'CreateView', 'UpdateView', 'DeleteView', 'FormView',
            'RedirectView', 'ArchiveIndexView', 'YearArchiveView',
            'MonthArchiveView', 'WeekArchiveView', 'DayArchiveView',
            'TodayArchiveView', 'DateDetailView'
        ]
        
        for cls in parsed_code.get('classes', []):
            parent_class = cls.get('parent_class', '')
            if any(base_class in parent_class for base_class in view_base_classes):
                view_classes.append({
                    'class_name': cls.get('name'),
                    'parent_class': parent_class,
                    'methods': [m.get('name') for m in cls.get('methods', [])],
                    'decorators': cls.get('decorators', [])
                })
        
        return view_classes
    
    def _extract_view_methods(self, code: str, parsed_code: Dict) -> List[str]:
        """Extract view HTTP methods"""
        http_methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
        methods_found = []
        
        for cls in parsed_code.get('classes', []):
            for method in cls.get('methods', []):
                if method['name'] in http_methods:
                    methods_found.append(method['name'])
        
        # Also look for function-based views
        func_pattern = r'def\s+(\w+)\s*\([^)]*request'
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1)
            if func_name in http_methods or any(meth in func_name for meth in ['view', 'handler']):
                methods_found.append(func_name)
        
        return list(set(methods_found))
    
    def _extract_view_decorators(self, code: str) -> List[str]:
        """Extract view decorators"""
        decorators = []
        
        common_decorators = [
            r'@login_required',
            r'@permission_required',
            r'@user_passes_test',
            r'@staff_member_required',
            r'@superuser_required',
            r'@csrf_exempt',
            r'@require_http_methods',
            r'@require_GET',
            r'@require_POST',
            r'@require_safe',
            r'@cache_control',
            r'@never_cache',
            r'@condition',
            r'@etag',
            r'@last_modified',
            r'@vary_on_cookie',
            r'@vary_on_headers',
        ]
        
        for decorator_pattern in common_decorators:
            if re.search(decorator_pattern, code):
                decorator_name = decorator_pattern.replace('@', '').replace('\\', '')
                decorators.append(decorator_name)
        
        return decorators
    
    def _extract_permission_classes(self, code: str) -> List[str]:
        """Extract DRF permission classes"""
        permission_classes = []
        
        patterns = [
            r'permission_classes\s*=\s*\[([^\]]+)\]',
            r'permission_classes\s*:\s*List\[[^\]]*\]\s*=\s*\[([^\]]+)\]',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, code):
                classes_text = match.group(1)
                # Extract class names
                class_matches = re.findall(r'([A-Z][A-Za-z]+Permission|IsAuthenticated|AllowAny|IsAdminUser)', classes_text)
                permission_classes.extend(class_matches)
        
        return list(set(permission_classes))
    
    def _extract_auth_usage(self, code: str) -> Dict[str, Any]:
        """Extract authentication-related patterns"""
        auth_patterns = {
            'login_required': bool(re.search(r'@login_required|login_required\(', code)),
            'permission_required': bool(re.search(r'@permission_required|permission_required\(', code)),
            'user_passes_test': bool(re.search(r'@user_passes_test|user_passes_test\(', code)),
            'has_perm_calls': len(list(re.finditer(r'\.has_perm\(', code))),
            'has_perms_calls': len(list(re.finditer(r'\.has_perms\(', code))),
            'check_permission_calls': len(list(re.finditer(r'check_permissions\(|test_func\(', code))),
            'authentication_classes': self._extract_authentication_classes(code),
        }
        return auth_patterns
    
    def _extract_authentication_classes(self, code: str) -> List[str]:
        """Extract DRF authentication classes"""
        auth_classes = []
        
        patterns = [
            r'authentication_classes\s*=\s*\[([^\]]+)\]',
            r'authentication_classes\s*:\s*List\[[^\]]*\]\s*=\s*\[([^\]]+)\]',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, code):
                classes_text = match.group(1)
                class_matches = re.findall(r'([A-Z][A-Za-z]+Authentication|TokenAuthentication|SessionAuthentication|BasicAuthentication)', classes_text)
                auth_classes.extend(class_matches)
        
        return list(set(auth_classes))
    
    def _extract_permission_checks(self, code: str) -> List[Dict]:
        """Extract permission check patterns"""
        checks = []
        
        check_patterns = [
            (r'\.has_perm\([\'\"]([^\'\"]+)[\'\"]', 'has_perm'),
            (r'\.has_perms\([\'\"]([^\'\"]+)[\'\"]', 'has_perms'),
            (r'check_permissions\([^)]*\)', 'check_permissions'),
            (r'test_func\([^)]*\)', 'test_func'),
        ]
        
        for pattern, check_type in check_patterns:
            for match in re.finditer(pattern, code):
                checks.append({
                    'type': check_type,
                    'match': match.group(0),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        return checks
    
    def _extract_group_permissions(self, code: str) -> Dict[str, Any]:
        """Extract group and permission management patterns"""
        patterns = {
            'group_creation': bool(re.search(r'Group\.objects\.(create|get_or_create)\(', code)),
            'permission_assignment': bool(re.search(r'\.permissions\.(set|add|remove)\(', code)),
            'user_group_assignment': bool(re.search(r'\.groups\.(set|add|remove)\(', code)),
            'content_type_usage': bool(re.search(r'ContentType\.objects\.get\(', code)),
            'permission_creation': bool(re.search(r'Permission\.objects\.(create|get_or_create)\(', code)),
            'role_based_checks': self._extract_role_checks(code),
        }
        return patterns
    
    def _extract_role_checks(self, code: str) -> List[str]:
        """Extract role-based permission checks"""
        role_checks = []
        
        patterns = [
            r'has_role\([\'\"]([^\'\"]+)[\'\"]',
            r'role_required\([^)]*roles\s*=\s*\[([^\]]+)\]',
            r'required_roles\s*=\s*\[([^\]]+)\]',
            r'role\s*(?:==|in)\s*[\'\"]([^\'\"]+)[\'\"]',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, code):
                role_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
                roles = re.findall(r'[\'\"]([^\'\"]+)[\'\"]', role_text)
                role_checks.extend(roles)
        
        return list(set(role_checks))
    
    def _extract_middleware_classes(self, parsed_code: Dict) -> List[Dict]:
        """Extract middleware classes"""
        middleware_classes = []
        
        for cls in parsed_code.get('classes', []):
            if 'Middleware' in cls.get('name', ''):
                middleware_classes.append({
                    'class_name': cls.get('name'),
                    'methods': [m.get('name') for m in cls.get('methods', [])],
                    'has_process_view': any(m.get('name') == 'process_view' for m in cls.get('methods', [])),
                    'has_process_request': any(m.get('name') == 'process_request' for m in cls.get('methods', [])),
                    'has_process_response': any(m.get('name') == 'process_response' for m in cls.get('methods', [])),
                })
        
        return middleware_classes
    
    def _extract_middleware_methods(self, code: str) -> List[str]:
        """Extract middleware method calls"""
        middleware_methods = []
        
        method_patterns = [
            'process_request',
            'process_view',
            'process_response',
            'process_exception',
            '__call__',
            '__init__',
        ]
        
        for method in method_patterns:
            if re.search(rf'\b{method}\b', code):
                middleware_methods.append(method)
        
        return middleware_methods
    
    def _extract_serializer_fields(self, code: str) -> List[Dict]:
        """Extract serializer fields"""
        fields = []
        
        serializer_field_types = [
            'CharField', 'IntegerField', 'BooleanField', 'DateTimeField',
            'SerializerMethodField', 'PrimaryKeyRelatedField', 'SlugRelatedField',
            'EmailField', 'URLField', 'FileField', 'ImageField', 'ListField',
            'DictField', 'JSONField', 'HiddenField', 'ReadOnlyField',
            'ModelField', 'StringRelatedField', 'HyperlinkedRelatedField',
            'HyperlinkedIdentityField', 'MultipleChoiceField', 'ChoiceField',
        ]
        
        for field_type in serializer_field_types:
            pattern = rf'(\w+)\s*=\s*(serializers\.)?{field_type}\s*\(([^)]*)\)'
            for match in re.finditer(pattern, code, re.DOTALL):
                field_name, _, params = match.groups()
                fields.append({
                    'field_type': field_type,
                    'name': field_name,
                    'params': params.strip(),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        return fields
    
    def _extract_serializer_classes(self, parsed_code: Dict) -> List[Dict]:
        """Extract serializer classes"""
        serializer_classes = []
        
        for cls in parsed_code.get('classes', []):
            if cls.get('name', '').endswith('Serializer'):
                serializer_classes.append({
                    'class_name': cls.get('name'),
                    'parent_class': cls.get('parent_class', ''),
                    'methods': [m.get('name') for m in cls.get('methods', [])],
                    'has_validate': any(m.get('name').startswith('validate_') for m in cls.get('methods', [])),
                })
        
        return serializer_classes
    
    def _extract_queryset_ops(self, code: str) -> List[str]:
        """Extract Django ORM queryset operations"""
        operations = []
        
        queryset_ops = [
            'filter', 'exclude', 'get', 'all', 'first', 'last', 'count',
            'aggregate', 'annotate', 'order_by', 'distinct', 'values', 'values_list',
            'select_related', 'prefetch_related', 'only', 'defer', 'using',
            'raw', 'exists', 'update', 'delete', 'bulk_create', 'bulk_update',
            'iterator', 'earliest', 'latest', 'create', 'get_or_create',
            'update_or_create', 'in_bulk', 'explain',
        ]
        
        for op in queryset_ops:
            if re.search(rf'\.{op}\s*\(', code):
                operations.append(op)
        
        return list(set(operations))
    
    def _extract_queryset_methods(self, code: str) -> List[Dict]:
        """Extract queryset method chains"""
        methods = []
        
        # Pattern for method chaining: .method1().method2().method3()
        chain_pattern = r'\.(\w+)\([^)]*\)(?:\.\w+\([^)]*\))*'
        
        for match in re.finditer(chain_pattern, code):
            chain = match.group(0)
            method_names = re.findall(r'\.(\w+)\(', chain)
            if len(method_names) >= 2:  # Only consider actual chains
                methods.append({
                    'chain': method_names,
                    'full_chain': chain,
                    'line': code[:match.start()].count('\n') + 1
                })
        
        return methods
    
    def _extract_url_patterns(self, code: str) -> List[Dict]:
        """Extract URL patterns"""
        url_patterns = []
        
        # Pattern for path() and re_path() calls
        path_patterns = [
            (r'path\([\'\"]([^\'\"]+)[\'\"],\s*([^,]+),\s*', 'path'),
            (r're_path\([\'\"]([^\'\"]+)[\'\"],\s*([^,]+),\s*', 're_path'),
            (r'url\([\'\"]([^\'\"]+)[\'\"],\s*([^,]+),\s*', 'url'),
        ]
        
        for pattern, pattern_type in path_patterns:
            for match in re.finditer(pattern, code):
                url_path, view = match.groups()
                url_patterns.append({
                    'type': pattern_type,
                    'path': url_path,
                    'view': view.strip(),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        return url_patterns
    
    def _extract_url_includes(self, code: str) -> List[str]:
        """Extract URL includes"""
        includes = []
        
        include_pattern = r'include\([\'\"]([^\'\"]+)[\'\"]\)'
        
        for match in re.finditer(include_pattern, code):
            include_path = match.group(1)
            includes.append(include_path)
        
        return includes
    
    def _extract_template_usage(self, code: str) -> Dict[str, Any]:
        """Extract template-related patterns"""
        template_patterns = {
            'render_calls': len(list(re.finditer(r'render\(', code))),
            'template_name_usage': bool(re.search(r'template_name\s*=', code)),
            'get_template_calls': len(list(re.finditer(r'get_template\(', code))),
            'loader_calls': len(list(re.finditer(r'loader\.', code))),
            'template_response': bool(re.search(r'TemplateResponse', code)),
            'context_usage': bool(re.search(r'context\s*=', code)),
        }
        return template_patterns
    
    def _extract_context_data(self, code: str) -> List[Dict]:
        """Extract context data patterns"""
        context_data = []
        
        # Pattern for get_context_data method
        context_pattern = r'def\s+get_context_data\s*\([^)]*\)\s*:\s*(.*?)(?=\ndef\s|\nclass\s|\Z)'
        context_match = re.search(context_pattern, code, re.DOTALL)
        
        if context_match:
            context_body = context_match.group(1)
            # Look for context variable assignments
            var_patterns = [
                r'context\[[\'\"]([^\'\"]+)[\'\"]\]\s*=\s*([^,\n]+)',
                r'context\.update\(([^)]+)\)',
            ]
            
            for pattern in var_patterns:
                for var_match in re.finditer(pattern, context_body):
                    if '[' in pattern:
                        key, value = var_match.groups()
                        context_data.append({'key': key, 'value': value.strip()})
                    else:
                        # Parse update dict
                        update_text = var_match.group(1)
                        key_value_pairs = re.findall(r'[\'\"]([^\'\"]+)[\'\"]\s*:\s*([^,}]+)', update_text)
                        for key, value in key_value_pairs:
                            context_data.append({'key': key, 'value': value.strip()})
        
        return context_data
    
    # Additional extractors for form, signal, admin, test patterns
    # (Implementation similar to above methods)
    
    def _extract_form_fields(self, code: str) -> List[Dict]:
        """Extract form field definitions"""
        fields = []
        form_field_types = [
            'CharField', 'IntegerField', 'BooleanField', 'DateField',
            'DateTimeField', 'EmailField', 'URLField', 'ChoiceField',
            'MultipleChoiceField', 'FileField', 'ImageField', 'ModelChoiceField',
            'ModelMultipleChoiceField',
        ]
        
        for field_type in form_field_types:
            pattern = rf'(\w+)\s*=\s*(forms\.)?{field_type}\s*\(([^)]*)\)'
            for match in re.finditer(pattern, code, re.DOTALL):
                field_name, _, params = match.groups()
                fields.append({
                    'field_type': field_type,
                    'name': field_name,
                    'params': params.strip(),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        return fields
    
    def _extract_signal_handlers(self, code: str) -> List[Dict]:
        """Extract signal handler decorators"""
        handlers = []
        
        signal_patterns = [
            (r'@receiver\(([^)]+)\)', 'receiver'),
            (r'\.connect\(([^)]+)\)', 'connect'),
        ]
        
        for pattern, handler_type in signal_patterns:
            for match in re.finditer(pattern, code):
                params = match.group(1)
                handlers.append({
                    'type': handler_type,
                    'params': params,
                    'line': code[:match.start()].count('\n') + 1
                })
        
        return handlers

    def _extract_form_classes(self, parsed_code: Dict) -> List[Dict]:
        """Extract form classes"""
        form_classes = []
        
        for cls in parsed_code.get('classes', []):
            if cls.get('name', '').endswith('Form'):
                form_classes.append({
                    'class_name': cls.get('name'),
                    'parent_class': cls.get('parent_class', ''),
                    'methods': [m.get('name') for m in cls.get('methods', [])],
                    'has_clean': any(m.get('name') == 'clean' for m in cls.get('methods', [])),
                    'has_save': any(m.get('name') == 'save' for m in cls.get('methods', [])),
                })
    
        return form_classes
    
    def _extract_test_classes(self, parsed_code: Dict) -> List[Dict]:
        """Extract test classes"""
        test_classes = []
        
        test_base_classes = ['TestCase', 'APITestCase', 'SimpleTestCase', 'TransactionTestCase']
        
        for cls in parsed_code.get('classes', []):
            parent_class = cls.get('parent_class', '')
            if any(base_class in parent_class for base_class in test_base_classes):
                test_classes.append({
                    'class_name': cls.get('name'),
                    'parent_class': parent_class,
                    'test_methods': [m.get('name') for m in cls.get('methods', []) if m.get('name', '').startswith('test_')],
                })
        
        return test_classes

    def _extract_signal_connections(self, code: str) -> List[Dict]:
        """Extract signal connection patterns"""
        connections = []
        
        connect_pattern = r'\.connect\(([^)]+)\)'
        for match in re.finditer(connect_pattern, code):
            params = match.group(1)
            connections.append({
                'params': params,
                'line': code[:match.start()].count('\n') + 1
            })
        
        return connections

    def _extract_admin_classes(self, parsed_code: Dict) -> List[Dict]:
        """Extract admin classes"""
        admin_classes = []
        
        for cls in parsed_code.get('classes', []):
            if cls.get('name', '').endswith('Admin'):
                admin_classes.append({
                    'class_name': cls.get('name'),
                    'parent_class': cls.get('parent_class', ''),
                    'methods': [m.get('name') for m in cls.get('methods', [])],
                    'has_list_display': 'list_display' in str(cls.get('body', '')),
                })
        
        return admin_classes

    def _extract_admin_registrations(self, code: str) -> List[str]:
        """Extract admin registration calls"""
        registrations = []
        
        admin_pattern = r'admin\.site\.register\(([^)]+)\)'
        for match in re.finditer(admin_pattern, code):
            params = match.group(1)
            registrations.append(params.strip())
        
        return registrations
    
    def _extract_test_methods(self, code: str) -> List[str]:
        """Extract test method patterns"""
        test_methods = []
        
        test_pattern = r'def\s+(test_\w+)\s*\('
        for match in re.finditer(test_pattern, code):
            test_methods.append(match.group(1))
        
        return test_methods


class ReactSemanticAnalyzer(BaseSemanticAnalyzer):
    """Semantic analyzer for React framework"""
    
    def analyze(self, code: str, parsed_code: Dict) -> Dict[str, Any]:
        """Analyze React code for semantic patterns"""
        semantics = {
            # Hook-related patterns
            'hook_calls': self._extract_hook_calls(code, parsed_code),
            'hook_dependencies': self._extract_hook_dependencies(code),
            'custom_hooks': self._extract_custom_hooks(code, parsed_code),
            
            # Component patterns
            'component_types': self._extract_component_types(parsed_code),
            'component_props': self._extract_component_props(code, parsed_code),
            'component_state': self._extract_component_state(code),
            
            # State management patterns
            'state_declarations': self._extract_state_declarations(code),
            'state_updates': self._extract_state_updates(code),
            'state_management_libs': self._extract_state_management_libs(code),
            
            # Effect patterns
            'effect_usage': self._extract_effect_usage(code),
            'effect_cleanup': self._extract_effect_cleanup(code),
            'effect_dependencies': self._extract_effect_dependencies(code),
            
            # Performance patterns
            'memoization_usage': self._extract_memoization_usage(code),
            'optimization_patterns': self._extract_optimization_patterns(code),
            
            # Event handling patterns
            'event_handlers': self._extract_event_handlers(code),
            'event_types': self._extract_event_types(code),
            
            # Form patterns
            'form_handling': self._extract_form_handling(code),
            'form_validation': self._extract_form_validation(code),
            
            # Routing patterns
            'routing_usage': self._extract_routing_usage(code),
            'route_components': self._extract_route_components(parsed_code),
            
            # API patterns
            'api_calls': self._extract_api_calls(code),
            'fetch_patterns': self._extract_fetch_patterns(code),
            'async_patterns': self._extract_async_patterns(code, parsed_code),
            
            # JSX patterns
            'jsx_elements': self._extract_jsx_elements(code),
            'jsx_attributes': self._extract_jsx_attributes(code),
            
            # TypeScript patterns (if applicable)
            'typescript_features': self._extract_typescript_features(code),
        }
        return semantics
    
    # ===== React Semantic Extractors =====
    
    def _extract_hook_calls(self, code: str, parsed_code: Dict) -> List[Dict]:
        """Extract React hook calls with detailed information"""
        hook_calls = []
        
        react_hooks = [
            'useState', 'useEffect', 'useContext', 'useReducer',
            'useCallback', 'useMemo', 'useRef', 'useImperativeHandle',
            'useLayoutEffect', 'useDebugValue', 'useTransition',
            'useDeferredValue', 'useId', 'useSyncExternalStore',
        ]
        
        for hook in react_hooks:
            pattern = rf'\b{hook}\s*\(([^)]*)\)'
            matches = list(re.finditer(pattern, code))
            
            if matches:
                for match in matches:
                    params = match.group(1)
                    line = code[:match.start()].count('\n') + 1
                    
                    # Analyze hook parameters
                    param_analysis = self._analyze_hook_params(hook, params)
                    
                    hook_calls.append({
                        'hook': hook,
                        'params': params.strip(),
                        'param_analysis': param_analysis,
                        'line': line,
                        'context': self._get_hook_context(code, match.start())
                    })
        
        return hook_calls
    
    def _analyze_hook_params(self, hook: str, params: str) -> Dict[str, Any]:
        """Analyze hook parameters based on hook type"""
        analysis = {}
        
        if hook == 'useState':
            # Extract initial value
            analysis['initial_value'] = params.strip()
            analysis['has_function_initializer'] = '() =>' in params or 'function' in params
        
        elif hook == 'useEffect':
            # Extract dependencies
            if '[' in params and ']' in params:
                deps_start = params.find('[')
                deps_end = params.find(']')
                deps = params[deps_start+1:deps_end].strip()
                analysis['dependencies'] = [d.strip() for d in deps.split(',') if d.strip()]
                analysis['dependency_count'] = len(analysis['dependencies'])
                analysis['empty_deps'] = analysis['dependency_count'] == 0
            else:
                analysis['dependencies'] = []
                analysis['dependency_count'] = 0
                analysis['empty_deps'] = False
        
        elif hook == 'useCallback':
            # Extract callback and dependencies
            parts = params.split(',', 1)
            if len(parts) == 2:
                analysis['callback'] = parts[0].strip()
                deps = parts[1].strip()
                if deps.startswith('[') and deps.endswith(']'):
                    analysis['dependencies'] = [d.strip() for d in deps[1:-1].split(',') if d.strip()]
        
        elif hook == 'useMemo':
            # Extract factory and dependencies
            parts = params.split(',', 1)
            if len(parts) == 2:
                analysis['factory'] = parts[0].strip()
                deps = parts[1].strip()
                if deps.startswith('[') and deps.endswith(']'):
                    analysis['dependencies'] = [d.strip() for d in deps[1:-1].split(',') if d.strip()]
        
        return analysis
    
    def _get_hook_context(self, code: str, position: int) -> str:
        """Determine where hook is called (component, custom hook, etc.)"""
        code_before = code[:position]
        
        # Check if inside function component
        if re.search(r'(?:function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>)\s*\{[^}]*$', code_before, re.DOTALL):
            return 'function_component'
        
        # Check if inside custom hook (starts with 'use')
        if re.search(r'(?:function\s+use[A-Z]|const\s+use[A-Z]\w+\s*=\s*\([^)]*\)\s*=>)', code_before):
            return 'custom_hook'
        
        # Check if inside class component method
        if re.search(r'class\s+\w+\s+extends\s+(?:React\.)?Component\s*\{[^}]*$', code_before, re.DOTALL):
            # Check if inside lifecycle method or custom method
            method_patterns = ['componentDidMount', 'componentDidUpdate', 'componentWillUnmount', 'render']
            for pattern in method_patterns:
                if re.search(rf'{pattern}\s*\([^)]*\)\s*{{[^}}]*$', code_before, re.DOTALL):
                    return f'class_component_{pattern}'
            return 'class_component_other'
        
        return 'unknown'
    
    def _extract_hook_dependencies(self, code: str) -> List[Dict]:
        """Extract hook dependency arrays"""
        dependencies = []
        
        # Pattern for useEffect, useCallback, useMemo dependencies
        dep_pattern = r'(useEffect|useCallback|useMemo)\s*\([^,]+,\s*\[([^\]]+)\]\)'
        
        for match in re.finditer(dep_pattern, code):
            hook_name, deps_text = match.groups()
            dep_list = [d.strip() for d in deps_text.split(',') if d.strip()]
            
            dependencies.append({
                'hook': hook_name,
                'dependencies': dep_list,
                'count': len(dep_list),
                'line': code[:match.start()].count('\n') + 1
            })
        
        return dependencies
    
    def _extract_custom_hooks(self, code: str, parsed_code: Dict) -> List[Dict]:
        """Extract custom hook definitions"""
        custom_hooks = []
        
        # Pattern for custom hook functions (start with 'use')
        patterns = [
            r'function\s+(use[A-Z]\w+)\s*\(([^)]*)\)',
            r'const\s+(use[A-Z]\w+)\s*=\s*\(([^)]*)\)\s*=>',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, code):
                hook_name, params = match.groups()
                
                # Find hook body
                func_start = match.end()
                brace_count = 0
                in_function = False
                func_end = func_start
                
                for i, char in enumerate(code[func_start:], func_start):
                    if char == '{':
                        brace_count += 1
                        in_function = True
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and in_function:
                            func_end = i
                            break
                
                hook_body = code[func_start:func_end] if func_end > func_start else ''
                
                # Analyze hook body
                uses_react_hooks = bool(re.search(r'\b(useState|useEffect|useContext|useReducer|useCallback|useMemo|useRef)\s*\(', hook_body))
                returns_value = 'return' in hook_body
                
                custom_hooks.append({
                    'name': hook_name,
                    'params': [p.strip() for p in params.split(',') if p.strip()],
                    'uses_react_hooks': uses_react_hooks,
                    'returns_value': returns_value,
                    'line': code[:match.start()].count('\n') + 1
                })
        
        return custom_hooks
    
    def _extract_component_types(self, parsed_code: Dict) -> Dict[str, int]:
        """Extract component type counts"""
        component_types = {
            'function_components': 0,
            'class_components': 0,
            'arrow_function_components': 0,
            'memo_components': 0,
            'forward_ref_components': 0,
            'lazy_components': 0,
        }
        
        # Function components
        for func in parsed_code.get('functions', []):
            func_name = func['name']
            if func_name[0].isupper() or 'Component' in func_name:
                component_types['function_components'] += 1
        
        # Class components
        for cls in parsed_code.get('classes', []):
            parent_class = cls.get('parent_class', '')
            if 'Component' in parent_class or 'PureComponent' in parent_class:
                component_types['class_components'] += 1
        
        # Check for memo, forwardRef, etc. in code
        code_text = parsed_code.get('raw_code', '')
        if 'React.memo(' in code_text:
            component_types['memo_components'] = code_text.count('React.memo(')
        if 'React.forwardRef(' in code_text:
            component_types['forward_ref_components'] = code_text.count('React.forwardRef(')
        if 'React.lazy(' in code_text:
            component_types['lazy_components'] = code_text.count('React.lazy(')
        
        return component_types


    def _extract_component_state(self, code: str) -> Dict[str, Any]:
        """Extract React component state patterns including class and function component state"""
        state_patterns = {
            'class_component_state': self._extract_class_component_state(code),
            'function_component_state': self._extract_function_component_state(code),
            'context_state': self._extract_context_state(code),
            'global_state': self._extract_global_state(code),
            'state_variables': self._extract_state_variables(code),
            'state_initializations': self._extract_state_initializations(code)
    }
        return state_patterns
    
    def _extract_class_component_state(self, code: str) -> List[Dict]:
        """Extract state from React class components"""
        class_states = []
        
        # Pattern for class component state initialization
        state_init_pattern = r'class\s+\w+\s+extends\s+(?:React\.)?Component\s*{[\s\S]*?constructor\s*\([^)]*\)\s*{[\s\S]*?this\.state\s*=\s*({[^}]+})'
        
        for match in re.finditer(state_init_pattern, code, re.DOTALL):
            state_obj = match.group(1)
            # Parse state object
            state_items = []
            for prop_match in re.finditer(r'(\w+)\s*:\s*([^,\n}]+)', state_obj):
                key, value = prop_match.groups()
                state_items.append({
                    'key': key.strip(),
                    'value': value.strip(),
                    'line': code[:match.start()].count('\n') + 1
                })
            
            class_states.append({
                'type': 'class_component',
                'initial_state': state_items,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Pattern for setState calls
        setstate_pattern = r'this\.setState\s*\(([^)]+)\)'
        for match in re.finditer(setstate_pattern, code):
            params = match.group(1).strip()
            is_function = params.startswith('(') or '=>' in params
            is_object = params.startswith('{')
            
            class_states.append({
                'type': 'set_state_call',
                'params': params,
                'is_function': is_function,
                'is_object': is_object,
                'line': code[:match.start()].count('\n') + 1
            })
        
        return class_states
    

    def _extract_function_component_state(self, code: str) -> List[Dict]:
        """Extract state from React function components"""
        function_states = []
        
        # Pattern for useState hooks
        usestate_pattern = r'const\s*\[([^\]]+)\]\s*=\s*useState\s*\(([^)]*)\)'
        for match in re.finditer(usestate_pattern, code):
            variables, initial_value = match.groups()
            var_list = [v.strip() for v in variables.split(',')]
            
            function_states.append({
                'type': 'use_state',
                'variables': var_list,
                'initial_value': initial_value.strip(),
                'is_function_initializer': '=>' in initial_value or initial_value.strip().startswith('()'),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Pattern for useReducer hooks
        usereducer_pattern = r'const\s*\[([^\]]+)\]\s*=\s*useReducer\s*\(([^)]*)\)'
        for match in re.finditer(usereducer_pattern, code):
            variables, reducer_params = match.groups()
            var_list = [v.strip() for v in variables.split(',')]
            
            function_states.append({
                'type': 'use_reducer',
                'variables': var_list,
                'reducer_params': reducer_params.strip(),
                'line': code[:match.start()].count('\n') + 1
            })
        
        return function_states
    

    def _extract_context_state(self, code: str) -> List[Dict]:
        """Extract state from React Context API"""
        contexts = []
        
        # Pattern for createContext
        createcontext_pattern = r'createContext\s*\(([^)]*)\)'
        for match in re.finditer(createcontext_pattern, code):
            default_value = match.group(1).strip()
            contexts.append({
                'type': 'create_context',
                'default_value': default_value,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Pattern for useContext
        usecontext_pattern = r'useContext\s*\(([^)]+)\)'
        for match in re.finditer(usecontext_pattern, code):
            context_ref = match.group(1).strip()
            contexts.append({
                'type': 'use_context',
                'context_ref': context_ref,
                'line': code[:match.start()].count('\n') + 1
            })
        
        return contexts


    def _extract_global_state(self, code: str) -> List[Dict]:
        """Extract global state management patterns (Redux, Zustand, etc.)"""
        global_states = []
        
        # Redux patterns
        redux_patterns = [
            (r'createStore\s*\(', 'redux_create_store'),
            (r'useSelector\s*\(', 'redux_use_selector'),
            (r'useDispatch\s*\(', 'redux_use_dispatch'),
            (r'configureStore\s*\(', 'redux_toolkit_configure_store'),
            (r'createSlice\s*\(', 'redux_toolkit_create_slice'),
        ]
        
        for pattern, lib_type in redux_patterns:
            if re.search(pattern, code):
                global_states.append({
                    'library': 'redux',
                    'type': lib_type,
                    'detected': True
                })
        
        # Zustand patterns
        zustand_patterns = [
            (r'create\s*\(', 'zustand_create'),
            (r'useStore\s*\(', 'zustand_use_store'),
        ]
        
        for pattern, lib_type in zustand_patterns:
            if re.search(pattern, code):
                global_states.append({
                    'library': 'zustand',
                    'type': lib_type,
                    'detected': True
                })
        
        # MobX patterns
        mobx_patterns = [
            (r'makeObservable\s*\(', 'mobx_make_observable'),
            (r'makeAutoObservable\s*\(', 'mobx_make_auto_observable'),
            (r'observable\s*\(', 'mobx_observable'),
            (r'action\s*\(', 'mobx_action'),
            (r'computed\s*\(', 'mobx_computed'),
        ]
        
        for pattern, lib_type in mobx_patterns:
            if re.search(pattern, code):
                global_states.append({
                    'library': 'mobx',
                    'type': lib_type,
                    'detected': True
                })
        
        return global_states
    

    def _extract_state_variables(self, code: str) -> List[str]:
        """Extract all state variable names"""
        state_vars = []
        
        # Extract from useState
        usestate_var_pattern = r'const\s*\[([^\]]+)\]\s*=\s*useState'
        for match in re.finditer(usestate_var_pattern, code):
            variables = match.group(1)
            vars_list = [v.strip() for v in variables.split(',') if v.strip()]
            state_vars.extend(vars_list)
        
        # Extract from class state
        class_state_pattern = r'this\.state\.(\w+)'
        for match in re.finditer(class_state_pattern, code):
            state_vars.append(match.group(1))
        
        return list(set(state_vars))
    

    def _extract_state_initializations(self, code: str) -> List[Dict]:
        """Extract state initialization patterns"""
        initializations = []
        
        # Function component state initialization
        func_init_pattern = r'useState\s*\(([^)]*)\)'
        for match in re.finditer(func_init_pattern, code):
            value = match.group(1).strip()
            init_type = 'function' if '=>' in value or value.startswith('(') else 'value'
            initializations.append({
                'type': 'useState_init',
                'value': value,
                'init_type': init_type,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Class component state initialization
        class_init_pattern = r'this\.state\s*=\s*({[^}]+})'
        for match in re.finditer(class_init_pattern, code):
            state_obj = match.group(1)
            initializations.append({
                'type': 'class_state_init',
                'value': state_obj,
                'init_type': 'object',
                'line': code[:match.start()].count('\n') + 1
            })
        
        return initializations
    

    def _extract_state_updates(self, code: str) -> List[Dict]:
        """Extract React state update patterns"""
        updates = []
        
        # useState setter calls
        setter_pattern = r'(\w+Setter|\w+Dispatch)\s*\(([^)]*)\)'
        for match in re.finditer(setter_pattern, code):
            func_name, params = match.groups()
            updates.append({
                'type': 'setter_call',
                'setter': func_name,
                'params': params.strip(),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Functional updates pattern
        func_update_pattern = r'set\w+\s*\(.*?=>.*?\)'
        for match in re.finditer(func_update_pattern, code, re.DOTALL):
            update_text = match.group(0)
            updates.append({
                'type': 'functional_update',
                'update': update_text.strip(),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Batch updates (React 18+)
        batch_pattern = r'flushSync\s*\(|startTransition\s*\('
        for match in re.finditer(batch_pattern, code):
            updates.append({
                'type': 'batch_update',
                'method': match.group(0).replace('(', '').strip(),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Redux dispatch
        dispatch_pattern = r'dispatch\s*\(({[^}]+})\)'
        for match in re.finditer(dispatch_pattern, code):
            action = match.group(1)
            updates.append({
                'type': 'redux_dispatch',
                'action': action.strip(),
                'line': code[:match.start()].count('\n') + 1
            })
        
        return updates


    def _extract_state_management_libs(self, code: str) -> List[str]:
        """Detect React state management libraries"""
        libraries = []
        
        lib_patterns = {
            'redux': [
                r'from\s+[\'"]redux[\'"]',
                r'from\s+[\'"]@reduxjs/toolkit[\'"]',
                r'import.*redux',
                r'createStore\s*\(',
                r'useSelector\s*\(',
                r'useDispatch\s*\(',
            ],
            'zustand': [
                r'from\s+[\'"]zustand[\'"]',
                r'import.*zustand',
                r'create\s*\(',
                r'useStore\s*\(',
            ],
            'mobx': [
                r'from\s+[\'"]mobx[\'"]',
                r'from\s+[\'"]mobx-react[\'"]',
                r'import.*mobx',
                r'makeObservable\s*\(',
                r'observable\s*\(',
            ],
            'recoil': [
                r'from\s+[\'"]recoil[\'"]',
                r'import.*recoil',
                r'atom\s*\(',
                r'useRecoilState\s*\(',
                r'useRecoilValue\s*\(',
            ],
            'jotai': [
                r'from\s+[\'"]jotai[\'"]',
                r'import.*jotai',
                r'atom\s*\(',
                r'useAtom\s*\(',
            ],
            'xstate': [
                r'from\s+[\'"]xstate[\'"]',
                r'from\s+[\'"]@xstate/react[\'"]',
                r'import.*xstate',
                r'createMachine\s*\(',
                r'useMachine\s*\(',
            ],
            'context': [
                r'createContext\s*\(',
                r'useContext\s*\(',
                r'Context\.Provider',
            ],
        }
        
        for lib_name, patterns in lib_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    if lib_name not in libraries:
                        libraries.append(lib_name)
                    break
        
        return libraries


    def _extract_effect_cleanup(self, code: str) -> List[Dict]:
        """Extract React effect cleanup patterns"""
        cleanups = []
        
        # Pattern for useEffect with cleanup
        effect_cleanup_pattern = r'useEffect\s*\(\(\)\s*=>\s*{([\s\S]*?)return\s*\(\)\s*=>\s*{([\s\S]*?)}([\s\S]*?)}\s*,\s*\[([^\]]*)\]\)'
        
        for match in re.finditer(effect_cleanup_pattern, code, re.DOTALL):
            effect_body, cleanup_body, after_cleanup, deps = match.groups()
            
            cleanup_operations = []
            
            # Check for common cleanup operations
            cleanup_patterns = [
                (r'clearInterval\s*\(([^)]+)\)', 'clear_interval'),
                (r'clearTimeout\s*\(([^)]+)\)', 'clear_timeout'),
                (r'removeEventListener\s*\(([^)]+)\)', 'remove_event_listener'),
                (r'abort\s*\(\)', 'abort_controller'),
                (r'\.unsubscribe\s*\(\)', 'unsubscribe'),
                (r'\.cancel\s*\(\)', 'cancel'),
                (r'\.close\s*\(\)', 'close'),
                (r'\.disconnect\s*\(\)', 'disconnect'),
                (r'\.stop\s*\(\)', 'stop'),
            ]
            
            for pattern, op_type in cleanup_patterns:
                if re.search(pattern, cleanup_body):
                    cleanup_operations.append(op_type)
            
            cleanups.append({
                'effect_body': effect_body.strip(),
                'cleanup_body': cleanup_body.strip(),
                'cleanup_operations': cleanup_operations,
                'dependencies': [d.strip() for d in deps.split(',') if d.strip()],
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Also look for simpler patterns
        simple_cleanup_pattern = r'useEffect\s*\(.*?return.*?=>.*?{'
        simple_matches = list(re.finditer(simple_cleanup_pattern, code, re.DOTALL))
        if simple_matches and not cleanups:
            for match in simple_matches:
                cleanups.append({
                    'has_cleanup': True,
                    'line': code[:match.start()].count('\n') + 1,
                    'simple_pattern': True
                })
        
        return cleanups
    

    def _extract_effect_dependencies(self, code: str) -> List[Dict]:
        """Extract React effect dependency patterns"""
        dependencies = []
        
        # Pattern for useEffect, useCallback, useMemo dependencies
        dep_patterns = [
            (r'useEffect\s*\([^,]+,\s*\[([^\]]+)\]\)', 'useEffect'),
            (r'useCallback\s*\([^,]+,\s*\[([^\]]+)\]\)', 'useCallback'),
            (r'useMemo\s*\([^,]+,\s*\[([^\]]+)\]\)', 'useMemo'),
        ]
        
        for pattern, hook_type in dep_patterns:
            for match in re.finditer(pattern, code):
                deps_text = match.group(1)
                dep_list = [d.strip() for d in deps_text.split(',') if d.strip()]
                
                # Analyze dependencies
                dependency_analysis = {
                    'count': len(dep_list),
                    'empty': len(dep_list) == 0,
                    'includes_state': any(re.search(r'set\w+|dispatch', d, re.IGNORECASE) for d in dep_list),
                    'includes_props': any('props' in d.lower() for d in dep_list),
                    'includes_refs': any('ref' in d.lower() for d in dep_list),
                    'complex_deps': any('.' in d or '[' in d for d in dep_list),
                }
                
                dependencies.append({
                    'hook': hook_type,
                    'dependencies': dep_list,
                    'analysis': dependency_analysis,
                    'line': code[:match.start()].count('\n') + 1
                })
        
        # Find missing dependency warnings (ESLint pattern)
        missing_dep_pattern = r'React Hook .*? has a missing dependency: \'(\w+)\''
        for match in re.finditer(missing_dep_pattern, code):
            dependencies.append({
                'hook': 'eslint_warning',
                'missing_dependency': match.group(1),
                'warning': match.group(0),
                'line': code[:match.start()].count('\n') + 1
            })
        
        return dependencies
    

    def _extract_memoization_usage(self, code: str) -> Dict[str, Any]:
        """Detect React memoization patterns"""
        memoization = {
            'react_memo': [],
            'use_memo': [],
            'use_callback': [],
            'memo_components': [],
            'pure_components': []
        }
        
        # React.memo() usage
        react_memo_pattern = r'(?:React\.)?memo\s*\(([^)]+)\)'
        for match in re.finditer(react_memo_pattern, code):
            memoized_component = match.group(1).strip()
            memoization['react_memo'].append({
                'component': memoized_component,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # useMemo usage
        use_memo_pattern = r'useMemo\s*\(([^,]+),\s*\[([^\]]+)\]\)'
        for match in re.finditer(use_memo_pattern, code):
            factory, deps = match.groups()
            dep_list = [d.strip() for d in deps.split(',') if d.strip()]
            
            memoization['use_memo'].append({
                'factory': factory.strip(),
                'dependencies': dep_list,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # useCallback usage
        use_callback_pattern = r'useCallback\s*\(([^,]+),\s*\[([^\]]+)\]\)'
        for match in re.finditer(use_callback_pattern, code):
            callback, deps = match.groups()
            dep_list = [d.strip() for d in deps.split(',') if d.strip()]
            
            memoization['use_callback'].append({
                'callback': callback.strip(),
                'dependencies': dep_list,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # PureComponent usage
        pure_component_pattern = r'extends\s+(?:React\.)?PureComponent'
        if re.search(pure_component_pattern, code):
            memoization['pure_components'].append({
                'detected': True,
                'count': len(list(re.finditer(pure_component_pattern, code)))
            })
        
        # Count memoized components
        memoization['memo_components_count'] = len(memoization['react_memo'])
        memoization['use_memo_count'] = len(memoization['use_memo'])
        memoization['use_callback_count'] = len(memoization['use_callback'])
        
        return memoization
    

    def _extract_optimization_patterns(self, code: str) -> List[str]:
        """Extract React optimization patterns"""
        optimizations = []
        
        optimization_patterns = [
            (r'React\.memo\s*\(', 'react_memo'),
            (r'useMemo\s*\(', 'use_memo'),
            (r'useCallback\s*\(', 'use_callback'),
            (r'extends\s+PureComponent', 'pure_component'),
            (r'React\.lazy\s*\(', 'react_lazy'),
            (r'Suspense', 'suspense'),
            (r'startTransition\s*\(', 'start_transition'),
            (r'useDeferredValue\s*\(', 'use_deferred_value'),
            (r'useTransition\s*\(', 'use_transition'),
            (r'profiler', 'profiler'),
            (r'key\s*=\s*{', 'list_keys'),
            (r'window\.addEventListener\s*\(', 'event_listener_optimization'),
            (r'IntersectionObserver', 'intersection_observer'),
            (r'ResizeObserver', 'resize_observer'),
            (r'requestAnimationFrame', 'raf_optimization'),
            (r'requestIdleCallback', 'idle_callback'),
            (r'debounce\s*\(', 'debounce'),
            (r'throttle\s*\(', 'throttle'),
            (r'memo\s*=\s*{?\[?', 'custom_memoization'),
        ]
        
        for pattern, optimization in optimization_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                optimizations.append(optimization)
        
        # Check for virtualized lists
        virtualized_patterns = ['react-window', 'react-virtualized', 'virtuoso', 'react-virtuoso']
        for lib in virtualized_patterns:
            if lib in code.lower():
                optimizations.append(f'virtualized_list_{lib}')
        
        # Check for code splitting
        if 'import(' in code and '.then' in code or 'lazy' in code:
            optimizations.append('code_splitting')
        
        return list(set(optimizations))


    def _extract_event_handlers(self, code: str) -> List[Dict]:
        """Extract React event handler patterns"""
        handlers = []
        
        # Inline event handlers
        inline_pattern = r'on(\w+)\s*=\s*{([^}]+)}'
        for match in re.finditer(inline_pattern, code):
            event_type, handler = match.groups()
            handlers.append({
                'type': 'inline',
                'event': event_type,
                'handler': handler.strip(),
                'is_arrow_function': '=>' in handler,
                'is_function_call': handler.strip().endswith(')'),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Function event handlers
        func_pattern = r'on(\w+)\s*=\s*{?(\w+)}?'
        for match in re.finditer(func_pattern, code):
            event_type, func_name = match.groups()
            # Make sure it's not already captured as inline
            if not any(h['event'] == event_type and h['handler'] == func_name for h in handlers):
                handlers.append({
                    'type': 'function_reference',
                    'event': event_type,
                    'handler': func_name,
                    'line': code[:match.start()].count('\n') + 1
                })
        
        # Event handler function definitions
        handler_func_pattern = r'(?:const\s+)?(handle\w+|on\w+)\s*=\s*(?:\(([^)]*)\)\s*=>|function(?:\s+\w+)?\s*\(([^)]*)\))'
        for match in re.finditer(handler_func_pattern, code):
            func_name = match.group(1)
            params1 = match.group(2)
            params2 = match.group(3)
            params = params1 if params1 else params2 if params2 else ''
            
            handlers.append({
                'type': 'handler_definition',
                'name': func_name,
                'params': [p.strip() for p in params.split(',') if p.strip()],
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Synthetic event usage
        synth_pattern = r'\.(preventDefault|stopPropagation|nativeEvent|target|currentTarget)\b'
        for match in re.finditer(synth_pattern, code):
            handlers.append({
                'type': 'synthetic_event_usage',
                'method': match.group(1),
                'line': code[:match.start()].count('\n') + 1
            })
        
        return handlers

    def _extract_event_types(self, code: str) -> List[str]:
        """Extract React event types"""
        event_types = []
        
        # Common React event types
        react_events = [
            'onClick', 'onChange', 'onSubmit', 'onMouseEnter', 'onMouseLeave',
            'onMouseMove', 'onMouseDown', 'onMouseUp', 'onKeyDown', 'onKeyUp',
            'onKeyPress', 'onFocus', 'onBlur', 'onInput', 'onScroll',
            'onLoad', 'onError', 'onDragStart', 'onDragEnd', 'onDragOver',
            'onDrop', 'onCopy', 'onCut', 'onPaste', 'onDoubleClick',
            'onContextMenu', 'onWheel', 'onTouchStart', 'onTouchEnd',
            'onTouchMove', 'onAnimationStart', 'onAnimationEnd',
            'onTransitionEnd'
        ]
        
        for event in react_events:
            if re.search(rf'\b{event}\b', code):
                event_types.append(event)
        
        # Custom events (starting with on)
        custom_event_pattern = r'\bon([A-Z][a-zA-Z]+)\b'
        for match in re.finditer(custom_event_pattern, code):
            event_name = match.group(0)
            if event_name not in event_types and event_name not in react_events:
                event_types.append(event_name)
        
        return event_types


    def _extract_form_handling(self, code: str) -> Dict[str, Any]:
        """Extract React form handling patterns"""
        form_patterns = {
            'controlled_components': [],
            'uncontrolled_components': [],
            'form_libraries': [],
            'validation_patterns': [],
            'form_state': []
        }
        
        # Controlled components (value + onChange)
        controlled_pattern = r'value\s*=\s*{([^}]+)}[\s\S]*?onChange\s*=\s*{([^}]+)}'
        for match in re.finditer(controlled_pattern, code, re.DOTALL):
            value, handler = match.groups()
            form_patterns['controlled_components'].append({
                'value_source': value.strip(),
                'change_handler': handler.strip(),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Uncontrolled components (refs)
        ref_pattern = r'ref\s*=\s*{?(\w+)}?'
        for match in re.finditer(ref_pattern, code):
            ref_name = match.group(1)
            # Check if it's likely a form element
            if any(tag in code for tag in ['<input', '<select', '<textarea']):
                form_patterns['uncontrolled_components'].append({
                    'ref': ref_name,
                    'line': code[:match.start()].count('\n') + 1
                })
        
        # Form library detection
        form_libs = {
            'formik': [r'from\s+[\'"]formik[\'"]', r'useFormik\s*\(', r'<Formik'],
            'react-hook-form': [r'from\s+[\'"]react-hook-form[\'"]', r'useForm\s*\(', r'register\s*\('],
            'final-form': [r'from\s+[\'"]react-final-form[\'"]', r'useField\s*\(', r'<Form'],
            'redux-form': [r'from\s+[\'"]redux-form[\'"]', r'reduxForm\s*\('],
        }
        
        for lib_name, patterns in form_libs.items():
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    if lib_name not in form_patterns['form_libraries']:
                        form_patterns['form_libraries'].append(lib_name)
                    break
        
        # Form submission patterns
        submit_pattern = r'onSubmit\s*=\s*{([^}]+)}'
        for match in re.finditer(submit_pattern, code):
            handler = match.group(1).strip()
            form_patterns['form_state'].append({
                'type': 'submit_handler',
                'handler': handler,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Form reset patterns
        reset_pattern = r'onReset\s*=\s*{([^}]+)}'
        for match in re.finditer(reset_pattern, code):
            handler = match.group(1).strip()
            form_patterns['form_state'].append({
                'type': 'reset_handler',
                'handler': handler,
                'line': code[:match.start()].count('\n') + 1
            })
        
        return form_patterns


    def _extract_form_validation(self, code: str) -> List[Dict]:
        """Extract React form validation patterns"""
        validations = []
        
        # Inline validation
        inline_patterns = [
            (r'required\s*=', 'required_field'),
            (r'pattern\s*=\s*{?/(.+)/}?', 'regex_pattern'),
            (r'minLength\s*=', 'min_length'),
            (r'maxLength\s*=', 'max_length'),
            (r'min\s*=', 'min_value'),
            (r'max\s*=', 'max_value'),
        ]
        
        for pattern, val_type in inline_patterns:
            for match in re.finditer(pattern, code):
                validations.append({
                    'type': val_type,
                    'pattern': match.group(0),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        # Validation function calls
        validation_func_pattern = r'validate\w*\s*\(([^)]*)\)'
        for match in re.finditer(validation_func_pattern, code):
            params = match.group(1)
            validations.append({
                'type': 'validation_function',
                'function': match.group(0).split('(')[0],
                'params': params,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Error state patterns
        error_patterns = [
            (r'error\s*=\s*{', 'error_state'),
            (r'errors\.', 'errors_object'),
            (r'\.error', 'dot_error'),
            (r'isValid\s*=', 'is_valid_check'),
            (r'validateOnBlur', 'validate_on_blur'),
            (r'validateOnChange', 'validate_on_change'),
        ]
        
        for pattern, val_type in error_patterns:
            if re.search(pattern, code):
                validations.append({
                    'type': val_type,
                    'detected': True
                })
        
        # Yup validation patterns
        yup_pattern = r'\byup\b|\.object\(|\.string\(|\.number\(|\.required\(|\.matches\('
        if re.search(yup_pattern, code, re.IGNORECASE):
            validations.append({
                'type': 'yup_validation',
                'detected': True
            })
        
        # Zod validation patterns
        zod_pattern = r'\bzod\b|z\.object\(|z\.string\(|z\.number\('
        if re.search(zod_pattern, code, re.IGNORECASE):
            validations.append({
                'type': 'zod_validation',
                'detected': True
            })
        
        return validations
    

    def _extract_routing_usage(self, code: str) -> Dict[str, Any]:
        """Detect React routing patterns"""
        routing = {
            'router_detected': False,
            'router_library': None,
            'routes': [],
            'route_components': [],
            'navigation_methods': [],
            'route_params': [],
            'nested_routes': False
        }
        
        # Detect router library
        router_patterns = {
            'react-router': [
                r'from\s+[\'"]react-router-dom[\'"]',
                r'from\s+[\'"]react-router[\'"]',
                r'<BrowserRouter',
                r'<Router',
                r'<Routes',
                r'<Route',
            ],
            'nextjs': [
                r'from\s+[\'"]next/router[\'"]',
                r'useRouter\s*\(\)',
                r'Link\s+from\s+[\'"]next/link[\'"]',
                r'getServerSideProps',
                r'getStaticProps',
            ],
            'wouter': [
                r'from\s+[\'"]wouter[\'"]',
                r'useRoute\s*\(\)',
                r'useLocation\s*\(\)',
            ],
            'reach-router': [
                r'from\s+[\'"]@reach/router[\'"]',
                r'<Router\s+',
            ],
        }
        
        for lib_name, patterns in router_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    routing['router_detected'] = True
                    routing['router_library'] = lib_name
                    break
        
        # Extract routes
        route_pattern = r'<Route\s+(.*?)/?>'
        for match in re.finditer(route_pattern, code, re.DOTALL):
            route_attrs = match.group(1)
            
            # Parse route attributes
            path_match = re.search(r'path\s*=\s*[\'"]([^\'"]+)[\'"]', route_attrs)
            element_match = re.search(r'element\s*=\s*{([^}]+)}', route_attrs)
            component_match = re.search(r'component\s*=\s*{([^}]+)}', route_attrs)
            
            route_info = {
                'path': path_match.group(1) if path_match else None,
                'element': element_match.group(1).strip() if element_match else None,
                'component': component_match.group(1).strip() if component_match else None,
                'line': code[:match.start()].count('\n') + 1
            }
            
            routing['routes'].append(route_info)
        
        # Navigation methods
        nav_patterns = [
            (r'useNavigate\s*\(\)', 'use_navigate'),
            (r'useHistory\s*\(\)', 'use_history'),
            (r'history\.push\s*\(', 'history_push'),
            (r'history\.replace\s*\(', 'history_replace'),
            (r'navigate\s*\(', 'navigate'),
            (r'<Link\s+', 'link_component'),
            (r'<NavLink\s+', 'navlink_component'),
        ]
        
        for pattern, nav_type in nav_patterns:
            if re.search(pattern, code):
                routing['navigation_methods'].append(nav_type)
        
        # Route parameters
        param_pattern = r':(\w+)'
        for match in re.finditer(param_pattern, code):
            if any(route['path'] and match.group(0) in route['path'] for route in routing['routes']):
                routing['route_params'].append({
                    'param': match.group(1),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        # Nested routes detection
        nested_pattern = r'<Route.*?>.*?<Route'
        if re.search(nested_pattern, code, re.DOTALL):
            routing['nested_routes'] = True
        
        return routing
    

    def _extract_route_components(self, parsed_code: Dict) -> List[Dict]:
        """Extract React route components"""
        route_components = []
        
        # Get component names from parsed code
        components = []
        
        # Function components (capitalized)
        for func in parsed_code.get('functions', []):
            if func['name'][0].isupper():
                components.append(func['name'])
        
        # Class components
        for cls in parsed_code.get('classes', []):
            if 'Component' in cls.get('parent_class', ''):
                components.append(cls['name'])
        
        # Check if components are used in routes
        code_text = parsed_code.get('raw_code', '')
        
        for component in components:
            # Check if component is used in Route element or component prop
            route_patterns = [
                rf'element\s*=\s*{{.*?{component}.*?}}',
                rf'component\s*=\s*{{.*?{component}.*?}}',
                rf'<Route.*?>\s*<{component}',
            ]
            
            for pattern in route_patterns:
                if re.search(pattern, code_text, re.DOTALL):
                    route_components.append({
                        'name': component,
                        'type': 'route_component',
                        'detected': True
                    })
                    break
        
        return route_components


    def _extract_fetch_patterns(self, code: str) -> List[Dict]:
        """Extract React fetch patterns"""
        fetch_patterns = []
        
        # Basic fetch calls
        fetch_call_pattern = r'fetch\s*\(([^)]*)\)'
        for match in re.finditer(fetch_call_pattern, code):
            params = match.group(1).strip()
            
            # Analyze fetch parameters
            method_match = re.search(r'method\s*:\s*[\'"]([^\'"]+)[\'"]', params)
            headers_match = re.search(r'headers\s*:\s*({[^}]+})', params)
            body_match = re.search(r'body\s*:\s*([^,]+)', params)
            
            fetch_patterns.append({
                'type': 'fetch',
                'params': params,
                'method': method_match.group(1) if method_match else 'GET',
                'has_headers': bool(headers_match),
                'has_body': bool(body_match),
                'is_async': self._is_await_call(code, match.start()),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Axios calls
        axios_pattern = r'axios\.(get|post|put|delete|patch|request)\s*\(([^)]*)\)'
        for match in re.finditer(axios_pattern, code):
            method, params = match.groups()
            fetch_patterns.append({
                'type': 'axios',
                'method': method.upper(),
                'params': params.strip(),
                'is_async': self._is_await_call(code, match.start()),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # React Query patterns
        react_query_patterns = [
            (r'useQuery\s*\(([^)]*)\)', 'use_query'),
            (r'useMutation\s*\(([^)]*)\)', 'use_mutation'),
            (r'useInfiniteQuery\s*\(([^)]*)\)', 'use_infinite_query'),
        ]
        
        for pattern, query_type in react_query_patterns:
            for match in re.finditer(pattern, code):
                params = match.group(1)
                fetch_patterns.append({
                    'type': 'react_query',
                    'query_type': query_type,
                    'params': params.strip(),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        # SWR patterns
        swr_pattern = r'useSWR\s*\(([^)]*)\)'
        for match in re.finditer(swr_pattern, code):
            params = match.group(1)
            fetch_patterns.append({
                'type': 'swr',
                'params': params.strip(),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # AbortController patterns (for fetch cancellation)
        abort_pattern = r'new\s+AbortController\s*\(\)'
        for match in re.finditer(abort_pattern, code):
            fetch_patterns.append({
                'type': 'abort_controller',
                'detected': True,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Response handling patterns
        response_patterns = [
            (r'\.json\s*\(\)', 'json_response'),
            (r'\.text\s*\(\)', 'text_response'),
            (r'\.blob\s*\(\)', 'blob_response'),
            (r'\.arrayBuffer\s*\(\)', 'array_buffer_response'),
        ]
        
        for pattern, resp_type in response_patterns:
            if re.search(pattern, code):
                fetch_patterns.append({
                    'type': 'response_handling',
                    'response_type': resp_type,
                    'detected': True
                })
        
        return fetch_patterns


    def _extract_async_patterns(self, code: str, parsed_code: Dict) -> List[Dict]:
        """Extract React async patterns"""
        async_patterns = []
        
        # Async function declarations
        async_func_pattern = r'async\s+(?:function\s+(\w+)|const\s+(\w+)\s*=\s*async|(\w+)\s*=\s*async\s*\()'
        for match in re.finditer(async_func_pattern, code):
            func_name = match.group(1) or match.group(2) or match.group(3)
            
            async_patterns.append({
                'type': 'async_function',
                'name': func_name,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Async arrow functions
        async_arrow_pattern = r'const\s+(\w+)\s*=\s*async\s*\([^)]*\)\s*=>'
        for match in re.finditer(async_arrow_pattern, code):
            func_name = match.group(1)
            async_patterns.append({
                'type': 'async_arrow_function',
                'name': func_name,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Await usage
        await_pattern = r'await\s+(\w+)\s*\('
        for match in re.finditer(await_pattern, code):
            call_name = match.group(1)
            async_patterns.append({
                'type': 'await_call',
                'call': call_name,
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Promise chains
        promise_patterns = [
            (r'\.then\s*\(([^)]+)\)', 'promise_then'),
            (r'\.catch\s*\(([^)]+)\)', 'promise_catch'),
            (r'\.finally\s*\(([^)]+)\)', 'promise_finally'),
            (r'Promise\.all\s*\(', 'promise_all'),
            (r'Promise\.race\s*\(', 'promise_race'),
            (r'Promise\.resolve\s*\(', 'promise_resolve'),
            (r'Promise\.reject\s*\(', 'promise_reject'),
        ]
        
        for pattern, promise_type in promise_patterns:
            for match in re.finditer(pattern, code):
                async_patterns.append({
                    'type': promise_type,
                    'expression': match.group(1) if len(match.groups()) > 0 else '',
                    'line': code[:match.start()].count('\n') + 1
                })
        
        # Async in useEffect
        async_use_effect_pattern = r'useEffect\s*\(\(\)\s*=>\s*{[\s\S]*?await'
        if re.search(async_use_effect_pattern, code, re.DOTALL):
            async_patterns.append({
                'type': 'async_use_effect',
                'detected': True
            })
        
        # Error handling patterns
        error_patterns = [
            (r'try\s*{', 'try_block'),
            (r'catch\s*\(', 'catch_block'),
        ]
        
        for pattern, error_type in error_patterns:
            matches = list(re.finditer(pattern, code))
            if matches:
                async_patterns.append({
                    'type': error_type,
                    'count': len(matches)
                })
        
        return async_patterns


    def _extract_typescript_features(self, code: str) -> Dict[str, Any]:
        """Detect TypeScript features"""
        ts_features = {
            'typescript_detected': False,
            'type_annotations': [],
            'interfaces': [],
            'types': [],
            'generics': [],
            'enums': [],
            'decorators': [],
            'type_imports': []
        }
        
        # Check for TypeScript syntax
        ts_patterns = [
            # Type annotations
            (r':\s*\w+(?:\s*<[^>]+>)?(?:\s*\[\])?(?:\s*\|\s*\w+)*', 'type_annotation'),
            # Interfaces
            (r'interface\s+(\w+)', 'interface'),
            # Type aliases
            (r'type\s+(\w+)', 'type_alias'),
            # Generics
            (r'<[A-Z][a-zA-Z]*>', 'generic'),
            # Enums
            (r'enum\s+(\w+)', 'enum'),
            # Decorators
            (r'@(\w+)', 'decorator'),
        ]
        
        for pattern, feature_type in ts_patterns:
            for match in re.finditer(pattern, code):
                if feature_type == 'type_annotation':
                    ts_features['type_annotations'].append({
                        'annotation': match.group(0),
                        'line': code[:match.start()].count('\n') + 1
                    })
                elif feature_type == 'interface':
                    ts_features['interfaces'].append(match.group(1))
                elif feature_type == 'type_alias':
                    ts_features['types'].append(match.group(1))
                elif feature_type == 'generic':
                    ts_features['generics'].append(match.group(0))
                elif feature_type == 'enum':
                    ts_features['enums'].append(match.group(1))
                elif feature_type == 'decorator':
                    ts_features['decorators'].append(match.group(1))
        
        # Type imports
        type_import_pattern = r'import\s+type\s+'
        if re.search(type_import_pattern, code):
            ts_features['type_imports'] = True
        
        # Check for .tsx or .ts extension comments (not reliable but can help)
        if any(pattern in code for pattern in ['// @ts-', '// ts-', 'tslint:', 'eslint-']):
            ts_features['typescript_detected'] = True
        
        # If we found any TypeScript-specific features, mark as detected
        if (ts_features['type_annotations'] or ts_features['interfaces'] or 
            ts_features['types'] or ts_features['generics']):
            ts_features['typescript_detected'] = True
        
        return ts_features
    
    # Additional React extractors for props, state, effects, etc.
    # (Implementation follows similar patterns as above)
    
    def _extract_component_props(self, code: str, parsed_code: Dict) -> List[Dict]:
        """Extract component props patterns"""
        props_patterns = []
        
        # Pattern for function component props
        func_prop_pattern = r'function\s+\w+\s*\(({[^}]*}|\w+)\)'
        for match in re.finditer(func_prop_pattern, code):
            props = match.group(1)
            props_patterns.append({
                'type': 'function_component',
                'props': props,
                'destructured': props.startswith('{'),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Pattern for arrow function props
        arrow_prop_pattern = r'const\s+\w+\s*=\s*\(({[^}]*}|\w+)\)\s*=>'
        for match in re.finditer(arrow_prop_pattern, code):
            props = match.group(1)
            props_patterns.append({
                'type': 'arrow_function',
                'props': props,
                'destructured': props.startswith('{'),
                'line': code[:match.start()].count('\n') + 1
            })
            
                # Check for PropTypes definitions
        proptypes_pattern = r'(\w+)\.propTypes\s*=\s*\{'
        for match in re.finditer(proptypes_pattern, code):
            component_name = match.group(1)
            props_patterns.append({
                'type': 'propTypes',
                'component': component_name,
                'line': code[:match.start()].count('\n') + 1
            })

        return props_patterns  


    def _validate_react_default_props(self, pattern: Dict, semantics: Dict, code: str) -> Dict:
        """Validate React defaultProps pattern"""
        # Check for defaultProps in code
        default_props_pattern = r'(\w+)\.defaultProps\s*=\s*\{([^}]+)\}'
        
        matches = list(re.finditer(default_props_pattern, code, re.DOTALL))
        
        if matches:
            component_name = matches[0].group(1)
            props_content = matches[0].group(2)
            
            # Count default props
            prop_count = len([p for p in props_content.split(',') if ':' in p])
            
            return {'passed': True, 'message': f"defaultProps defined for {component_name} ({prop_count} props)"}
        else:
            required_for = pattern.get('required_for')
            if required_for:
                return {'passed': False, 'message': f"defaultProps not defined for {required_for}"}
            return {'passed': False, 'message': "defaultProps not found"} 
    
        
    
    def _extract_state_declarations(self, code: str) -> List[Dict]:
        """Extract state declarations"""
        state_declarations = []
        
        # useState patterns
        state_pattern = r'const\s*\[([^\]]+)\]\s*=\s*useState\s*\(([^)]*)\)'
        for match in re.finditer(state_pattern, code):
            state_vars, initial_value = match.groups()
            vars_list = [v.strip() for v in state_vars.split(',')]
            
            state_declarations.append({
                'type': 'useState',
                'variables': vars_list,
                'initial_value': initial_value.strip(),
                'line': code[:match.start()].count('\n') + 1
            })
        
        # useReducer patterns
        reducer_pattern = r'const\s*\[([^\]]+)\]\s*=\s*useReducer\s*\(([^)]*)\)'
        for match in re.finditer(reducer_pattern, code):
            state_vars, reducer_params = match.groups()
            vars_list = [v.strip() for v in state_vars.split(',')]
            
            state_declarations.append({
                'type': 'useReducer',
                'variables': vars_list,
                'reducer_params': reducer_params.strip(),
                'line': code[:match.start()].count('\n') + 1
            })
        
        return state_declarations
    
    def _extract_effect_usage(self, code: str) -> List[Dict]:
        """Extract useEffect patterns"""
        effects = []
        
        effect_pattern = r'useEffect\s*\(([^,]+),\s*\[([^\]]+)\]\)'
        for match in re.finditer(effect_pattern, code):
            effect_fn, deps = match.groups()
            dep_list = [d.strip() for d in deps.split(',') if d.strip()]
            
            effects.append({
                'effect_function': effect_fn.strip(),
                'dependencies': dep_list,
                'dependency_count': len(dep_list),
                'empty_deps': len(dep_list) == 0,
                'line': code[:match.start()].count('\n') + 1
            })
        
        return effects
    
    def _extract_api_calls(self, code: str) -> List[Dict]:
        """Extract API call patterns"""
        api_calls = []
        
        # fetch patterns
        fetch_patterns = [
            (r'fetch\s*\(([^)]*)\)', 'fetch'),
            (r'axios\.(get|post|put|delete|patch)\s*\(([^)]*)\)', 'axios'),
            (r'\.then\s*\(([^)]*)\)', 'promise_then'),
            (r'\.catch\s*\(([^)]*)\)', 'promise_catch'),
        ]
        
        for pattern, call_type in fetch_patterns:
            for match in re.finditer(pattern, code):
                params = match.group(1) if len(match.groups()) > 0 else ''
                api_calls.append({
                    'type': call_type,
                    'params': params.strip(),
                    'line': code[:match.start()].count('\n') + 1,
                    'has_await': self._is_await_call(code, match.start())
                })
        
        return api_calls


    def _extract_jsx_elements(self, code: str) -> List[str]:
        """Extract React JSX elements from code"""
        jsx_elements = []
        
        # Self-closing elements with props (both PascalCase and lowercase)
        self_closing_pattern = r'<([A-Z][a-zA-Z0-9]*|[a-z][a-z0-9-]*)\s+[^/>]*/>'
        for match in re.finditer(self_closing_pattern, code):
            element = match.group(1)
            if element not in jsx_elements:
                jsx_elements.append(element)
        
        # Opening tags with props
        opening_pattern = r'<([A-Z][a-zA-Z0-9]*|[a-z][a-z0-9-]*)\s+[^>]*>'
        for match in re.finditer(opening_pattern, code):
            element = match.group(1)
            if element not in jsx_elements:
                jsx_elements.append(element)
        
        # Closing tags (for elements without props)
        closing_pattern = r'</([A-Z][a-zA-Z0-9]*|[a-z][a-z0-9-]*)>'
        for match in re.finditer(closing_pattern, code):
            element = match.group(1)
            if element not in jsx_elements:
                jsx_elements.append(element)
        
        # Fragment detection
        fragment_patterns = [
            r'<>',
            r'</>',
            r'<React\.Fragment>',
            r'</React\.Fragment>',
            r'<Fragment>',
            r'</Fragment>'
        ]
        
        has_fragment = False
        for pattern in fragment_patterns:
            if re.search(pattern, code):
                has_fragment = True
                break
        
        if has_fragment and 'Fragment' not in jsx_elements:
            jsx_elements.append('Fragment')
        
        # Custom component detection (PascalCase without < >)
        custom_comp_pattern = r'\b([A-Z][a-zA-Z0-9]+)\b(?=[^>]*</)'
        for match in re.finditer(custom_comp_pattern, code):
            component = match.group(1)
            # Check if it's actually used as a component (not a prop or something else)
            if component not in jsx_elements and len(component) > 1:
                # Verify it's used in JSX context
                context_start = max(0, match.start() - 20)
                context = code[context_start:match.start()]
                if '<' in context:
                    jsx_elements.append(component)
        
        # Built-in React components
        react_components = [
            'Suspense', 'Profiler', 'StrictMode', 'lazy', 'memo', 'forwardRef'
        ]
        
        for comp in react_components:
            if comp in code and comp not in jsx_elements:
                # Check if used as JSX element
                if re.search(rf'<{comp}\b', code) or re.search(rf'</{comp}>', code):
                    jsx_elements.append(comp)
        
        # Remove duplicates and sort
        return sorted(list(set(jsx_elements)))


    def _extract_jsx_attributes(self, code: str) -> List[Dict]:
        """Extract React JSX attributes with detailed information"""
        attributes = []
        
        # Find all JSX tags (self-closing and opening)
        tag_pattern = r'<([A-Za-z][A-Za-z0-9-]*)(\s+[^>]*?)(/?)>'
        
        for match in re.finditer(tag_pattern, code):
            tag_name, attrs_text, is_self_closing = match.groups()
            line_number = code[:match.start()].count('\n') + 1
            
            # Extract individual attributes
            attr_pattern = r'(\w+)(?:\s*=\s*(?:{([^}]+)}|[\'"]([^\'"]+)[\'"]))?'
            
            for attr_match in re.finditer(attr_pattern, attrs_text):
                attr_name = attr_match.group(1)
                js_value = attr_match.group(2)
                string_value = attr_match.group(3)
                
                # Skip if it's not a valid attribute (could be part of regex)
                if not attr_name or attr_name in ['if', 'else', 'for', 'while', 'switch', 'case']:
                    continue
                
                value = None
                value_type = 'none'
                
                if js_value is not None:
                    value = js_value.strip()
                    value_type = 'js_expression'
                elif string_value is not None:
                    value = string_value.strip()
                    value_type = 'string'
                
                # Determine attribute category
                attribute_category = self._categorize_jsx_attribute(attr_name, value)
                
                attribute_info = {
                    'tag': tag_name,
                    'name': attr_name,
                    'value': value,
                    'value_type': value_type,
                    'category': attribute_category,
                    'line': line_number,
                    'is_event_handler': attr_name.startswith('on') and len(attr_name) > 2,
                    'is_style': attr_name == 'style',
                    'is_class_name': attr_name in ['className', 'class'],
                    'is_ref': attr_name == 'ref',
                    'is_key': attr_name == 'key',
                    'is_spread': attr_name == '...'
                }
                
                # Add special handling for specific attributes
                if attr_name == 'style' and value and value_type == 'js_expression':
                    attribute_info['style_properties'] = self._extract_style_properties(value)
                
                if attr_name == 'className' and value:
                    attribute_info['css_classes'] = value.replace('"', '').replace("'", '').split()
                
                attributes.append(attribute_info)
            
            # Check for spread attributes
            spread_pattern = r'\.\.\.(\w+)'
            for spread_match in re.finditer(spread_pattern, attrs_text):
                spread_var = spread_match.group(1)
                attributes.append({
                    'tag': tag_name,
                    'name': '...',
                    'value': spread_var,
                    'value_type': 'spread',
                    'category': 'spread',
                    'line': line_number,
                    'is_spread': True
                })
        
        # Extract boolean attributes (attributes without values)
        boolean_attr_pattern = r'<[^>]*\s(\w+)(?=\s|/?>)'
        for match in re.finditer(boolean_attr_pattern, code):
            line_number = code[:match.start()].count('\n') + 1
            attr_name = match.group(1)
            
            # Check if this is already captured
            already_captured = any(
                attr['name'] == attr_name and attr['line'] == line_number 
                for attr in attributes
            )
            
            if not already_captured and attr_name not in ['if', 'else', 'for', 'while']:
                # Check if it's a valid boolean attribute
                common_boolean_attrs = [
                    'checked', 'disabled', 'readOnly', 'required', 'hidden',
                    'autoFocus', 'multiple', 'selected', 'defaultChecked',
                    'defaultValue', 'open', 'playsInline', 'loop', 'muted',
                    'controls', 'autoPlay', 'noValidate', 'formNoValidate'
                ]
                
                if attr_name in common_boolean_attrs or attr_name.startswith('data-') or attr_name.startswith('aria-'):
                    attributes.append({
                        'tag': 'unknown',  # Will be determined from context
                        'name': attr_name,
                        'value': True,
                        'value_type': 'boolean',
                        'category': 'boolean',
                        'line': line_number,
                        'is_boolean': True
                    })
        
        # Extract data-* and aria-* attributes
        data_aria_pattern = r'\s((?:data|aria)-[\w-]+)\s*=\s*(?:{([^}]+)}|[\'"]([^\'"]+)[\'"])'
        for match in re.finditer(data_aria_pattern, code):
            attr_name, js_value, string_value = match.groups()
            line_number = code[:match.start()].count('\n') + 1
            
            value = js_value.strip() if js_value is not None else string_value.strip() if string_value is not None else None
            
            attributes.append({
                'tag': 'unknown',
                'name': attr_name,
                'value': value,
                'value_type': 'js_expression' if js_value else 'string',
                'category': 'data_aria',
                'line': line_number,
                'is_data_attribute': attr_name.startswith('data-'),
                'is_aria_attribute': attr_name.startswith('aria-')
            })
        
        return attributes
    

    def _categorize_jsx_attribute(self, attr_name: str, value: Any) -> str:
        """Categorize JSX attribute based on name and value"""
        # Event handlers
        if attr_name.startswith('on') and len(attr_name) > 2:
            return 'event_handler'
        
        # React-specific attributes
        react_attrs = [
            'key', 'ref', 'children', 'dangerouslySetInnerHTML',
            'suppressContentEditableWarning', 'suppressHydrationWarning'
        ]
        if attr_name in react_attrs:
            return 'react_specific'
        
        # Style and class
        if attr_name in ['style', 'className', 'class']:
            return 'styling'
        
        # Form attributes
        form_attrs = [
            'value', 'defaultValue', 'checked', 'defaultChecked',
            'onChange', 'onSubmit', 'onReset', 'name', 'placeholder',
            'required', 'disabled', 'readOnly', 'autoFocus', 'form'
        ]
        if attr_name in form_attrs:
            return 'form'
        
        # Media attributes
        media_attrs = [
            'src', 'alt', 'width', 'height', 'poster', 'controls',
            'autoPlay', 'loop', 'muted', 'playsInline'
        ]
        if attr_name in media_attrs:
            return 'media'
        
        # Link attributes
        link_attrs = ['href', 'target', 'rel', 'download']
        if attr_name in link_attrs:
            return 'link'
        
        # Accessibility
        if attr_name.startswith('aria-'):
            return 'accessibility'
        
        # Data attributes
        if attr_name.startswith('data-'):
            return 'data'
        
        # Boolean attributes
        boolean_attrs = [
            'hidden', 'multiple', 'selected', 'open', 'noValidate'
        ]
        if attr_name in boolean_attrs:
            return 'boolean'
        
        # Spread operator
        if attr_name == '...':
            return 'spread'
        
        return 'generic'


    def _extract_style_properties(self, style_expression: str) -> Dict[str, str]:
        """Extract CSS properties from style object"""
        properties = {}
        
        # Remove outer curly braces and whitespace
        clean_style = style_expression.strip()
        if clean_style.startswith('{') and clean_style.endswith('}'):
            clean_style = clean_style[1:-1].strip()
        
        # Split by commas, but be careful with nested objects
        in_nested = 0
        current_prop = ''
        prop_start = 0
        
        for i, char in enumerate(clean_style):
            if char == '{':
                in_nested += 1
            elif char == '}':
                in_nested -= 1
            elif char == ',' and in_nested == 0:
                prop_text = clean_style[prop_start:i].strip()
                if ':' in prop_text:
                    key_value = prop_text.split(':', 1)
                    key = key_value[0].strip().strip('"').strip("'")
                    value = key_value[1].strip()
                    properties[key] = value
                prop_start = i + 1
        
        # Process last property
        if prop_start < len(clean_style):
            prop_text = clean_style[prop_start:].strip()
            if ':' in prop_text:
                key_value = prop_text.split(':', 1)
                key = key_value[0].strip().strip('"').strip("'")
                value = key_value[1].strip()
                properties[key] = value
        
        return properties
    
    def _is_await_call(self, code: str, position: int) -> bool:
        """Check if API call is preceded by await"""
        code_before = code[:position]
        # Look for 'await' keyword before the call
        return bool(re.search(r'\bawait\s+$', code_before.strip()[-20:]))


# Placeholder classes for other frameworks
class ExpressSemanticAnalyzer(BaseSemanticAnalyzer):
    def analyze(self, code: str, parsed_code: Dict) -> Dict[str, Any]:
        return {'framework': 'express', 'status': 'analyzer_not_implemented'}


class AngularSemanticAnalyzer(BaseSemanticAnalyzer):
    def analyze(self, code: str, parsed_code: Dict) -> Dict[str, Any]:
        return {'framework': 'angular', 'status': 'analyzer_not_implemented'}


class NodeJSSemanticAnalyzer(BaseSemanticAnalyzer):
    def analyze(self, code: str, parsed_code: Dict) -> Dict[str, Any]:
        return {'framework': 'nodejs', 'status': 'analyzer_not_implemented'}


# ===== Enhanced Intermediate Validator (UPDATED to inherit from BaseValidator) =====

class EnhancedIntermediateValidator(BaseValidator):
    """
    Enhanced Intermediate Validator with comprehensive framework support
    """
    
    def can_handle(self, difficulty: str, framework: str) -> bool:
        return difficulty in ['intermediate', 'medium']
    
    def validate(self, parsed_code: Dict[str, Any], validation_spec: Dict[str, Any], code: str) -> Dict[str, Any]:
        framework = validation_spec.get('framework', 'unknown')
        
        # Get appropriate analyzer
        analyzer = FrameworkAnalyzerFactory.create_analyzer(framework)
        semantics = analyzer.analyze(code, parsed_code)
        
        # Store semantics for validation methods
        parsed_code['semantics'] = semantics
        parsed_code['framework'] = framework
        
        return {
            'imports': self._validate_imports_common(parsed_code, validation_spec.get('required_imports', [])),
            'structure': self._validate_structure_enhanced(parsed_code, validation_spec.get('required_structure', {})),
            'behavior': self._validate_behavior_enhanced(parsed_code, validation_spec.get('behavior_patterns', []), code, framework)
        }
    
    def _validate_structure_enhanced(self, parsed_code: Dict, required_structure: Dict) -> Dict[str, Any]:
        """Enhanced structure validation with framework awareness"""
        details = []
        checks_passed = 0
        total_checks = 0
        
        framework = parsed_code.get('framework', 'unknown')
        semantics = parsed_code.get('semantics', {})
        
        # Class validation with framework-specific checks
        if 'classes' in required_structure:
            for class_spec in required_structure['classes']:
                if not isinstance(class_spec, dict):
                    continue
                
                class_name = class_spec.get('name')
                if not class_name:
                    continue
                
                total_checks += 1
                found = next((c for c in parsed_code.get('classes', []) if c['name'] == class_name), None)
                
                if found:
                    checks_passed += 1
                    details.append(f"✓ Class '{class_name}' found")
                    
                    # Framework-specific class validation
                    if framework == 'django':
                        self._validate_django_class(class_spec, found, semantics, details)
                    elif framework == 'react':
                        self._validate_react_class(class_spec, found, semantics, details)
                    
                else:
                    details.append(f"✗ Class '{class_name}' not found")
        
        # Function validation
        if 'functions' in required_structure:
            for func_spec in required_structure['functions']:
                if not isinstance(func_spec, dict):
                    continue
                
                func_name = func_spec.get('name')
                if not func_name:
                    continue
                
                total_checks += 1
                found = next((f for f in parsed_code.get('functions', []) if f['name'] == func_name), None)
                
                if not found:
                    details.append(f"✗ Function '{func_name}' not found")
                    continue
                
                checks_passed += 1
                details.append(f"✓ Function '{func_name}' found")
                
                # Check parameters
                if 'params' in func_spec:
                    total_checks += 1
                    expected_params = func_spec['params']
                    actual_params = found.get('params', [])
                    
                    if set(expected_params).issubset(set(actual_params)):
                        checks_passed += 1
                        details.append(f"  ✓ Parameters correct")
                    else:
                        details.append(f"  ✗ Parameters mismatch")
                
                # Framework-specific function validation
                if framework == 'django':
                    self._validate_django_function(func_spec, found, semantics, details)
                elif framework == 'react':
                    self._validate_react_function(func_spec, found, semantics, details)
        
        if total_checks == 0:
            return {'passed': False, 'score': 0.0, 'details': ["⚠️ No structure validation"]}
        
        score = (checks_passed / total_checks) * 100
        
        return {
            'passed': checks_passed == total_checks,
            'score': score,
            'details': details
        }
    
    def _validate_django_class(self, class_spec: Dict, found_class: Dict, semantics: Dict, details: List[str]):
        """Validate Django-specific class patterns"""
        class_name = class_spec.get('name', '')
        
        # Check for Django model fields
        if class_name.endswith('Model') or 'Model' in class_spec.get('parent_class', ''):
            model_fields = semantics.get('model_fields', [])
            if model_fields:
                details.append(f"  ✓ Model has {len(model_fields)} fields")
            else:
                details.append(f"  ⚠️ Model has no fields defined")
        
        # Check for Django view methods
        elif any(view_base in class_spec.get('parent_class', '') for view_base in ['View', 'ListView', 'DetailView']):
            view_methods = semantics.get('view_methods', [])
            if view_methods:
                details.append(f"  ✓ View has methods: {', '.join(view_methods)}")
    
    def _validate_react_class(self, class_spec: Dict, found_class: Dict, semantics: Dict, details: List[str]):
        """Validate React-specific class patterns"""
        parent_class = class_spec.get('parent_class', '')
        
        # Check for React.Component or React.PureComponent
        if 'Component' in parent_class:
            component_type = semantics.get('component_types', {})
            if component_type.get('class_components', 0) > 0:
                details.append(f"  ✓ React class component")
            
            # Check for lifecycle methods
            class_methods = found_class.get('methods', [])
            lifecycle_methods = ['componentDidMount', 'componentDidUpdate', 'componentWillUnmount', 'render']
            has_lifecycle = any(method['name'] in lifecycle_methods for method in class_methods)
            if has_lifecycle:
                details.append(f"  ✓ Has lifecycle methods")
    
    def _validate_django_function(self, func_spec: Dict, found_func: Dict, semantics: Dict, details: List[str]):
        """Validate Django-specific function patterns"""
        func_name = func_spec.get('name', '')
        
        # Check for view functions
        if any(term in func_name.lower() for term in ['view', 'handler']):
            view_decorators = semantics.get('view_decorators', [])
            if view_decorators:
                details.append(f"  ✓ View function with decorators: {', '.join(view_decorators)}")
        
        # Check for permission-related functions
        if 'permission' in func_name.lower() or 'role' in func_name.lower():
            permission_checks = semantics.get('permission_checks', [])
            if permission_checks:
                details.append(f"  ✓ Function performs permission checks")
    
    def _validate_react_function(self, func_spec: Dict, found_func: Dict, semantics: Dict, details: List[str]):
        """Validate React-specific function patterns"""
        func_name = func_spec.get('name', '')
        
        # Check for custom hooks
        if func_name.startswith('use'):
            custom_hooks = semantics.get('custom_hooks', [])
            if any(hook['name'] == func_name for hook in custom_hooks):
                details.append(f"  ✓ Custom hook implementation")
        
        # Check for component functions
        elif func_name[0].isupper() or 'Component' in func_name:
            hook_calls = semantics.get('hook_calls', [])
            if hook_calls:
                details.append(f"  ✓ Function uses React hooks")
    
    def _validate_behavior_enhanced(self, parsed_code: Dict, behavior_patterns: List, code: str, framework: str) -> Dict[str, Any]:
        """
        Enhanced behavior validation with comprehensive framework support
        """
        if not behavior_patterns:
            return {'passed': True, 'score': 100.0, 'details': ["No behavior patterns required"]}
        
        semantics = parsed_code.get('semantics', {})
        details = []
        matched = 0
        total = len(behavior_patterns)
        
        for pattern in behavior_patterns:
            if isinstance(pattern, str):
                # Legacy string pattern
                result = self._validate_legacy_pattern(pattern, code)
            else:
                # Structured pattern with framework support
                result = self._validate_structured_pattern(pattern, semantics, code, framework)
            
            if result['passed']:
                matched += 1
                details.append(f"✓ {result['message']}")
            else:
                details.append(f"✗ {result['message']}")
        
        score = (matched / total * 100) if total > 0 else 0
        
        return {
            'passed': matched == total,
            'score': score,
            'details': details
        }
    
    def _validate_structured_pattern(self, pattern: Dict, semantics: Dict, code: str, framework: str) -> Dict:
        """Validate structured patterns with framework awareness"""
        pattern_type = pattern.get('type')
        
        # Framework-specific pattern validation
        if framework == 'django':
            return self._validate_django_pattern(pattern_type, pattern, semantics, code)
        elif framework == 'react':
            return self._validate_react_pattern(pattern_type, pattern, semantics, code)
        elif framework == 'express':
            return self._validate_express_pattern(pattern_type, pattern, semantics, code)
        elif framework == 'angular':
            return self._validate_angular_pattern(pattern_type, pattern, semantics, code)
        else:
            return self._validate_generic_pattern(pattern_type, pattern, semantics, code)
    
    def _validate_django_pattern(self, pattern_type: str, pattern: Dict, semantics: Dict, code: str) -> Dict:
        """Validate Django-specific patterns"""
        
        if pattern_type == 'model_field':
            return self._validate_django_model_field(pattern, semantics)
        elif pattern_type == 'view_method':
            return self._validate_django_view_method(pattern, semantics)
        elif pattern_type == 'permission_check':
            return self._validate_django_permission_check(pattern, semantics)
        elif pattern_type == 'middleware':
            return self._validate_django_middleware(pattern, semantics)
        elif pattern_type == 'serializer':
            return self._validate_django_serializer(pattern, semantics)
        elif pattern_type == 'queryset_operation':
            return self._validate_django_queryset_operation(pattern, semantics)
        elif pattern_type == 'decorator':
            return self._validate_django_decorator(pattern, semantics, code)
        elif pattern_type == 'authentication':
            return self._validate_django_authentication(pattern, semantics)
        elif pattern_type == 'url_pattern':
            return self._validate_django_url_pattern(pattern, semantics, code)
        elif pattern_type == 'template_usage':
            return self._validate_django_template_usage(pattern, semantics)
        elif pattern_type == 'form_validation':
            return self._validate_django_form_validation(pattern, semantics)
        elif pattern_type == 'signal_handler':
            return self._validate_django_signal_handler(pattern, semantics, code)
        elif pattern_type == 'test_case':
            return self._validate_django_test_case(pattern, semantics)
        else:
            return self._validate_generic_pattern(pattern_type, pattern, semantics, code)
    
    def _validate_react_pattern(self, pattern_type: str, pattern: Dict, semantics: Dict, code: str) -> Dict:
        """Validate React-specific patterns"""
        
        if pattern_type == 'hook_call':
            return self._validate_react_hook_call(pattern, semantics)
        elif pattern_type == 'component_props':
            return self._validate_react_component_props(pattern, semantics)
        elif pattern_type == 'state_management':
            return self._validate_react_state_management(pattern, semantics)
        elif pattern_type == 'effect_usage':
            return self._validate_react_effect_usage(pattern, semantics)
        elif pattern_type == 'event_handler':
            return self._validate_react_event_handler(pattern, semantics, code)
        elif pattern_type == 'form_handling':
            return self._validate_react_form_handling(pattern, semantics)
        elif pattern_type == 'routing':
            return self._validate_react_routing(pattern, semantics, code)
        elif pattern_type == 'api_call':
            return self._validate_react_api_call(pattern, semantics)
        elif pattern_type == 'memoization':
            return self._validate_react_memoization(pattern, semantics)
        elif pattern_type == 'custom_hook':
            return self._validate_react_custom_hook(pattern, semantics)
        elif pattern_type == 'context_usage':
            return self._validate_react_context_usage(pattern, semantics)
        elif pattern_type == 'ref_usage':
            return self._validate_react_ref_usage(pattern, semantics)
        elif pattern_type == 'conditional_rendering':
            return self._validate_react_conditional_rendering(pattern, semantics, code)
        elif pattern_type == 'ternary_operator':
            # Alias for conditional_rendering with ternary type
            pattern['conditional_type'] = 'ternary'
            return self._validate_react_conditional_rendering(pattern, semantics, code)
        elif pattern_type == 'default_props':
            return self._validate_react_default_props(pattern, semantics, code)
        elif pattern_type == 'prop_types':
            # Check if PropTypes are defined
            component_props = semantics.get('component_props', [])
            proptype_defs = [p for p in component_props if p.get('type') == 'propTypes']
            if proptype_defs:
                return {'passed': True, 'message': f"PropTypes defined for {len(proptype_defs)} components"}
            return {'passed': False, 'message': "PropTypes not found"}
        else:
            return self._validate_generic_pattern(pattern_type, pattern, semantics, code)


    # Django-specific validation methods
    def _validate_django_model_field(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate Django model field pattern"""
        field_type = pattern.get('field_type')
        field_name = pattern.get('field_name')
        min_count = pattern.get('min_count', 1)
        
        model_fields = semantics.get('model_fields', [])
        
        if field_name:
            matching = [f for f in model_fields if f['name'] == field_name and f['field_type'] == field_type]
            if matching:
                return {'passed': True, 'message': f"Field '{field_name}' ({field_type}) found"}
            else:
                return {'passed': False, 'message': f"Field '{field_name}' ({field_type}) not found"}
        else:
            matching = [f for f in model_fields if f['field_type'] == field_type]
            if len(matching) >= min_count:
                return {'passed': True, 'message': f"{field_type} found ({len(matching)} instances)"}
            else:
                return {'passed': False, 'message': f"{field_type} not found (required: {min_count}, found: {len(matching)})"}
    
    def _validate_django_view_method(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate Django view method pattern"""
        method_name = pattern.get('method')
        view_methods = semantics.get('view_methods', [])
        
        if method_name in view_methods:
            return {'passed': True, 'message': f"View method '{method_name}' found"}
        else:
            return {'passed': False, 'message': f"View method '{method_name}' not found"}
    
    def _validate_django_permission_check(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate Django permission check pattern"""
        check_type = pattern.get('check_type', 'any')
        permission_checks = semantics.get('permission_checks', [])
        auth_usage = semantics.get('authentication_usage', {})
        
        if check_type == 'any':
            if permission_checks or auth_usage.get('has_perm_calls', 0) > 0:
                return {'passed': True, 'message': "Permission checks present"}
            else:
                return {'passed': False, 'message': "No permission checks found"}
        
        elif check_type == 'specific':
            permission_name = pattern.get('permission')
            for check in permission_checks:
                if permission_name in check.get('match', ''):
                    return {'passed': True, 'message': f"Permission check '{permission_name}' found"}
            return {'passed': False, 'message': f"Permission check '{permission_name}' not found"}
        
        return {'passed': False, 'message': "Invalid permission check type"}
    
    def _validate_django_middleware(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate Django middleware pattern"""
        middleware_classes = semantics.get('middleware_classes', [])
        middleware_methods = semantics.get('middleware_methods', [])
        
        if middleware_classes:
            class_names = [c['class_name'] for c in middleware_classes]
            return {'passed': True, 'message': f"Middleware classes: {', '.join(class_names)}"}
        elif middleware_methods:
            return {'passed': True, 'message': f"Middleware methods: {', '.join(middleware_methods)}"}
        else:
            return {'passed': False, 'message': "No middleware implementation found"}
    
    def _validate_django_serializer(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate Django serializer pattern"""
        serializer_fields = semantics.get('serializer_fields', [])
        serializer_classes = semantics.get('serializer_classes', [])
        
        if serializer_classes:
            class_names = [c['class_name'] for c in serializer_classes]
            return {'passed': True, 'message': f"Serializer classes: {', '.join(class_names)}"}
        elif serializer_fields:
            field_types = set(f['field_type'] for f in serializer_fields)
            return {'passed': True, 'message': f"Serializer fields: {', '.join(field_types)}"}
        else:
            return {'passed': False, 'message': "No serializer implementation found"}
    
    def _validate_django_queryset_operation(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate Django queryset operation pattern"""
        operation = pattern.get('operation')
        queryset_ops = semantics.get('queryset_operations', [])
        
        if operation in queryset_ops:
            return {'passed': True, 'message': f"Queryset operation '{operation}' found"}
        else:
            return {'passed': False, 'message': f"Queryset operation '{operation}' not found"}
    
    def _validate_django_decorator(self, pattern: Dict, semantics: Dict, code: str) -> Dict:
        """Validate Django decorator pattern"""
        decorator_name = pattern.get('decorator')
        view_decorators = semantics.get('view_decorators', [])
        
        # Check in view decorators
        if decorator_name in view_decorators:
            return {'passed': True, 'message': f"Decorator '@{decorator_name}' found"}
        
        # Also check directly in code
        if re.search(rf'@{decorator_name}\b', code):
            return {'passed': True, 'message': f"Decorator '@{decorator_name}' found"}
        
        return {'passed': False, 'message': f"Decorator '@{decorator_name}' not found"}
    
    def _validate_django_authentication(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate Django authentication pattern"""
        auth_type = pattern.get('auth_type', 'any')
        auth_usage = semantics.get('authentication_usage', {})
        
        if auth_type == 'any':
            if any(auth_usage.values()):
                return {'passed': True, 'message': "Authentication patterns found"}
            else:
                return {'passed': False, 'message': "No authentication patterns found"}
        
        elif auth_type == 'login_required':
            if auth_usage.get('login_required'):
                return {'passed': True, 'message': "@login_required decorator found"}
            else:
                return {'passed': False, 'message': "@login_required decorator not found"}
        
        elif auth_type == 'permission_required':
            if auth_usage.get('permission_required'):
                return {'passed': True, 'message': "@permission_required decorator found"}
            else:
                return {'passed': False, 'message': "@permission_required decorator not found"}
        
        return {'passed': False, 'message': "Invalid authentication type"}


    def _validate_django_url_pattern(self, pattern: Dict, semantics: Dict, code: str) -> Dict:
        """Validate Django URL pattern configuration"""
        url_patterns = semantics.get('url_patterns', [])
        url_includes = semantics.get('url_includes', [])
        
        pattern_type = pattern.get('pattern_type', 'any')
        required_path = pattern.get('path')
        required_view = pattern.get('view')
        
        if pattern_type == 'any':
            if url_patterns or url_includes:
                details = []
                if url_patterns:
                    details.append(f"{len(url_patterns)} URL patterns")
                if url_includes:
                    details.append(f"{len(url_includes)} includes")
                return {'passed': True, 'message': f"URL configuration: {', '.join(details)}"}
            else:
                return {'passed': False, 'message': "No URL patterns found"}
        
        elif pattern_type == 'path':
            if required_path:
                matching = [p for p in url_patterns if required_path in p.get('path', '')]
                if matching:
                    return {'passed': True, 'message': f"URL path '{required_path}' found"}
                else:
                    return {'passed': False, 'message': f"URL path '{required_path}' not found"}
            else:
                if url_patterns:
                    paths = [p.get('path', 'unknown') for p in url_patterns]
                    return {'passed': True, 'message': f"URL paths found: {', '.join(paths[:3])}"}
                return {'passed': False, 'message': "No URL paths defined"}
        
        elif pattern_type == 'view':
            if required_view:
                matching = [p for p in url_patterns if required_view in p.get('view', '')]
                if matching:
                    return {'passed': True, 'message': f"View '{required_view}' mapped in URLs"}
                else:
                    return {'passed': False, 'message': f"View '{required_view}' not found in URL patterns"}
            return {'passed': False, 'message': "No view specified for validation"}
        
        elif pattern_type == 'include':
            required_include = pattern.get('include')
            if required_include:
                if required_include in url_includes:
                    return {'passed': True, 'message': f"Include '{required_include}' found"}
                else:
                    return {'passed': False, 'message': f"Include '{required_include}' not found"}
            else:
                if url_includes:
                    return {'passed': True, 'message': f"URL includes found: {', '.join(url_includes)}"}
                return {'passed': False, 'message': "No URL includes found"}
        
        elif pattern_type == 're_path':
            re_paths = [p for p in url_patterns if p.get('type') == 're_path']
            if re_paths:
                return {'passed': True, 'message': f"re_path patterns found ({len(re_paths)})"}
            else:
                return {'passed': False, 'message': "No re_path patterns found"}
        
        return {'passed': False, 'message': f"Unknown URL pattern type: {pattern_type}"}


    def _validate_django_template_usage(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate Django template usage patterns"""
        template_usage = semantics.get('template_usage', {})
        context_data = semantics.get('context_data', [])
        
        usage_type = pattern.get('usage_type', 'any')
        
        if usage_type == 'any':
            if any(template_usage.values()) or context_data:
                details = []
                if template_usage.get('render_calls', 0) > 0:
                    details.append(f"{template_usage['render_calls']} render() calls")
                if template_usage.get('template_name_usage'):
                    details.append("template_name defined")
                if template_usage.get('get_template_calls', 0) > 0:
                    details.append(f"{template_usage['get_template_calls']} get_template() calls")
                if context_data:
                    details.append(f"{len(context_data)} context variables")
                return {'passed': True, 'message': f"Template usage: {', '.join(details)}"}
            else:
                return {'passed': False, 'message': "No template usage found"}
        
        elif usage_type == 'render':
            if template_usage.get('render_calls', 0) > 0:
                return {'passed': True, 'message': f"render() used {template_usage['render_calls']} times"}
            else:
                return {'passed': False, 'message': "render() not used"}
        
        elif usage_type == 'template_name':
            if template_usage.get('template_name_usage'):
                return {'passed': True, 'message': "template_name attribute defined"}
            else:
                return {'passed': False, 'message': "template_name attribute not found"}
        
        elif usage_type == 'context_data':
            required_keys = pattern.get('required_keys', [])
            if required_keys:
                context_keys = [item.get('key') for item in context_data]
                missing = [key for key in required_keys if key not in context_keys]
                if not missing:
                    return {'passed': True, 'message': f"All required context keys present: {', '.join(required_keys)}"}
                else:
                    return {'passed': False, 'message': f"Missing context keys: {', '.join(missing)}"}
            else:
                if context_data:
                    keys = [item.get('key') for item in context_data]
                    return {'passed': True, 'message': f"Context data found: {', '.join(keys)}"}
                return {'passed': False, 'message': "No context data found"}
        
        elif usage_type == 'get_template':
            if template_usage.get('get_template_calls', 0) > 0:
                return {'passed': True, 'message': f"get_template() used {template_usage['get_template_calls']} times"}
            else:
                return {'passed': False, 'message': "get_template() not used"}
        
        elif usage_type == 'template_response':
            if template_usage.get('template_response'):
                return {'passed': True, 'message': "TemplateResponse used"}
            else:
                return {'passed': False, 'message': "TemplateResponse not found"}
        
        return {'passed': False, 'message': f"Unknown template usage type: {usage_type}"}

    def _validate_django_form_validation(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate Django form validation patterns"""
        form_fields = semantics.get('form_fields', [])
        form_classes = semantics.get('form_classes', [])
        
        validation_type = pattern.get('validation_type', 'any')
        
        if validation_type == 'any':
            if form_fields or form_classes:
                details = []
                if form_fields:
                    details.append(f"{len(form_fields)} form fields")
                if form_classes:
                    has_clean = any(fc.get('has_clean') for fc in form_classes)
                    has_save = any(fc.get('has_save') for fc in form_classes)
                    if has_clean:
                        details.append("clean() method")
                    if has_save:
                        details.append("save() method")
                return {'passed': True, 'message': f"Form validation: {', '.join(details)}"}
            else:
                return {'passed': False, 'message': "No form validation found"}
        
        elif validation_type == 'clean_method':
            forms_with_clean = [fc for fc in form_classes if fc.get('has_clean')]
            if forms_with_clean:
                form_names = [fc['class_name'] for fc in forms_with_clean]
                return {'passed': True, 'message': f"clean() method in: {', '.join(form_names)}"}
            else:
                return {'passed': False, 'message': "No clean() method found"}
        
        elif validation_type == 'field_validation':
            required_field = pattern.get('field_name')
            if required_field:
                matching = [f for f in form_fields if f['name'] == required_field]
                if matching:
                    field = matching[0]
                    return {'passed': True, 'message': f"Field '{required_field}' ({field['field_type']}) found"}
                else:
                    return {'passed': False, 'message': f"Field '{required_field}' not found"}
            else:
                if form_fields:
                    field_types = set(f['field_type'] for f in form_fields)
                    return {'passed': True, 'message': f"Form fields: {', '.join(field_types)}"}
                return {'passed': False, 'message': "No form fields found"}
        
        elif validation_type == 'clean_field':
            # Check for clean_<fieldname>() methods
            field_name = pattern.get('field_name')
            if field_name:
                clean_method = f"clean_{field_name}"
                has_method = any(
                    clean_method in [m['name'] for m in fc.get('methods', [])]
                    for fc in form_classes
                )
                if has_method:
                    return {'passed': True, 'message': f"clean_{field_name}() method found"}
                else:
                    return {'passed': False, 'message': f"clean_{field_name}() method not found"}
            return {'passed': False, 'message': "No field name specified"}
        
        elif validation_type == 'model_form':
            model_forms = [fc for fc in form_classes if 'ModelForm' in fc.get('parent_class', '')]
            if model_forms:
                form_names = [fc['class_name'] for fc in model_forms]
                return {'passed': True, 'message': f"ModelForm classes: {', '.join(form_names)}"}
            else:
                return {'passed': False, 'message': "No ModelForm classes found"}
        
        return {'passed': False, 'message': f"Unknown form validation type: {validation_type}"}


    def _validate_django_signal_handler(self, pattern: Dict, semantics: Dict, code: str) -> Dict:
        """Validate Django signal handler patterns"""
        signal_handlers = semantics.get('signal_handlers', [])
        signal_connections = semantics.get('signal_connections', [])
        
        handler_type = pattern.get('handler_type', 'any')
        signal_name = pattern.get('signal')
        
        if handler_type == 'any':
            if signal_handlers or signal_connections:
                details = []
                if signal_handlers:
                    receiver_count = len([h for h in signal_handlers if h['type'] == 'receiver'])
                    connect_count = len([h for h in signal_handlers if h['type'] == 'connect'])
                    if receiver_count:
                        details.append(f"{receiver_count} @receiver decorators")
                    if connect_count:
                        details.append(f"{connect_count} .connect() calls")
                if signal_connections:
                    details.append(f"{len(signal_connections)} signal connections")
                return {'passed': True, 'message': f"Signal handlers: {', '.join(details)}"}
            else:
                return {'passed': False, 'message': "No signal handlers found"}
        
        elif handler_type == 'receiver':
            receiver_handlers = [h for h in signal_handlers if h['type'] == 'receiver']
            if signal_name:
                matching = [h for h in receiver_handlers if signal_name in h.get('params', '')]
                if matching:
                    return {'passed': True, 'message': f"@receiver decorator for {signal_name} found"}
                else:
                    return {'passed': False, 'message': f"@receiver decorator for {signal_name} not found"}
            else:
                if receiver_handlers:
                    return {'passed': True, 'message': f"@receiver decorators found ({len(receiver_handlers)})"}
                return {'passed': False, 'message': "No @receiver decorators found"}
        
        elif handler_type == 'connect':
            connect_handlers = [h for h in signal_handlers if h['type'] == 'connect']
            if connect_handlers or signal_connections:
                total = len(connect_handlers) + len(signal_connections)
                return {'passed': True, 'message': f".connect() calls found ({total})"}
            else:
                return {'passed': False, 'message': "No .connect() calls found"}
        
        elif handler_type == 'pre_save':
            if 'pre_save' in code or 'pre_save' in str(signal_handlers):
                return {'passed': True, 'message': "pre_save signal detected"}
            else:
                return {'passed': False, 'message': "pre_save signal not found"}
        
        elif handler_type == 'post_save':
            if 'post_save' in code or 'post_save' in str(signal_handlers):
                return {'passed': True, 'message': "post_save signal detected"}
            else:
                return {'passed': False, 'message': "post_save signal not found"}
        
        elif handler_type == 'pre_delete':
            if 'pre_delete' in code or 'pre_delete' in str(signal_handlers):
                return {'passed': True, 'message': "pre_delete signal detected"}
            else:
                return {'passed': False, 'message': "pre_delete signal not found"}
        
        elif handler_type == 'post_delete':
            if 'post_delete' in code or 'post_delete' in str(signal_handlers):
                return {'passed': True, 'message': "post_delete signal detected"}
            else:
                return {'passed': False, 'message': "post_delete signal not found"}
        
        return {'passed': False, 'message': f"Unknown signal handler type: {handler_type}"}


    def _validate_django_test_case(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate Django test case patterns"""
        test_classes = semantics.get('test_classes', [])
        test_methods = semantics.get('test_methods', [])
        
        test_type = pattern.get('test_type', 'any')
        
        if test_type == 'any':
            if test_classes or test_methods:
                details = []
                if test_classes:
                    class_names = [tc['class_name'] for tc in test_classes]
                    details.append(f"{len(test_classes)} test classes")
                if test_methods:
                    details.append(f"{len(test_methods)} test methods")
                return {'passed': True, 'message': f"Tests found: {', '.join(details)}"}
            else:
                return {'passed': False, 'message': "No test cases found"}
        
        elif test_type == 'test_case':
            testcase_classes = [tc for tc in test_classes if 'TestCase' in tc.get('parent_class', '')]
            if testcase_classes:
                class_names = [tc['class_name'] for tc in testcase_classes]
                return {'passed': True, 'message': f"TestCase classes: {', '.join(class_names)}"}
            else:
                return {'passed': False, 'message': "No TestCase classes found"}
        
        elif test_type == 'api_test':
            api_test_classes = [tc for tc in test_classes if 'APITestCase' in tc.get('parent_class', '')]
            if api_test_classes:
                class_names = [tc['class_name'] for tc in api_test_classes]
                return {'passed': True, 'message': f"APITestCase classes: {', '.join(class_names)}"}
            else:
                return {'passed': False, 'message': "No APITestCase classes found"}
        
        elif test_type == 'test_method':
            required_method = pattern.get('method_name')
            if required_method:
                if required_method in test_methods:
                    return {'passed': True, 'message': f"Test method '{required_method}' found"}
                else:
                    return {'passed': False, 'message': f"Test method '{required_method}' not found"}
            else:
                if test_methods:
                    return {'passed': True, 'message': f"Test methods: {', '.join(test_methods[:5])}"}
                return {'passed': False, 'message': "No test methods found"}
        
        elif test_type == 'setup_method':
            has_setup = any(
                'setUp' in [m for m in tc.get('test_methods', [])]
                for tc in test_classes
            )
            if has_setup:
                return {'passed': True, 'message': "setUp() method found"}
            else:
                return {'passed': False, 'message': "setUp() method not found"}
        
        elif test_type == 'teardown_method':
            has_teardown = any(
                'tearDown' in [m for m in tc.get('test_methods', [])]
                for tc in test_classes
            )
            if has_teardown:
                return {'passed': True, 'message': "tearDown() method found"}
            else:
                return {'passed': False, 'message': "tearDown() method not found"}
        
        return {'passed': False, 'message': f"Unknown test type: {test_type}"}  





    
    # React-specific validation methods
    def _validate_react_hook_call(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate React hook call pattern"""
        hook_name = pattern.get('hook')
        min_calls = pattern.get('min_calls', 1)
        
        hook_calls = semantics.get('hook_calls', [])
        matching_hooks = [h for h in hook_calls if h['hook'] == hook_name]
        
        if not matching_hooks:
            return {'passed': False, 'message': f"{hook_name} not called (required: {min_calls})"}
        
        actual_calls = len(matching_hooks)
        
        if actual_calls >= min_calls:
            return {'passed': True, 'message': f"{hook_name} called {actual_calls} times (required: {min_calls})"}
        else:
            return {'passed': False, 'message': f"{hook_name} called only {actual_calls} times (required: {min_calls})"}
    
    def _validate_react_component_props(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate React component props pattern"""
        props_patterns = semantics.get('component_props', [])
        
        if props_patterns:
            prop_types = set(p['type'] for p in props_patterns)
            return {'passed': True, 'message': f"Component props found: {', '.join(prop_types)}"}
        else:
            return {'passed': False, 'message': "No component props patterns found"}
    
    def _validate_react_state_management(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate React state management pattern"""
        state_declarations = semantics.get('state_declarations', [])
        
        # Check for 'state_type' field (from validation spec) or 'type' field
        state_management = pattern.get('state_type', pattern.get('type', 'any'))
        
        if state_management == 'any':
            if state_declarations:
                state_types = set(s['type'] for s in state_declarations)
                return {'passed': True, 'message': f"State management: {', '.join(state_types)}"}
            else:
                return {'passed': False, 'message': "No state management found"}
        
        elif state_management == 'useState':
            useState_declarations = [s for s in state_declarations if s['type'] == 'useState']
            if useState_declarations:
                return {'passed': True, 'message': f"useState used ({len(useState_declarations)} declarations)"}
            else:
                return {'passed': False, 'message': "useState not used"}
        
        elif state_management == 'useReducer':
            useReducer_declarations = [s for s in state_declarations if s['type'] == 'useReducer']
            if useReducer_declarations:
                return {'passed': True, 'message': f"useReducer used ({len(useReducer_declarations)} declarations)"}
            else:
                return {'passed': False, 'message': "useReducer not used"}
        
        return {'passed': False, 'message': f"Unknown state management type: {state_management}"}   
     
    def _validate_react_effect_usage(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate React effect usage pattern"""
        effects = semantics.get('effect_usage', [])
        
        if effects:
            effect_count = len(effects)
            empty_deps_count = sum(1 for e in effects if e.get('empty_deps', False))
            return {'passed': True, 'message': f"useEffect used {effect_count} times ({empty_deps_count} with empty deps)"}
        else:
            return {'passed': False, 'message': "useEffect not used"}
    
    def _validate_react_api_call(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate React API call pattern"""
        api_calls = semantics.get('api_calls', [])
        
        if api_calls:
            call_types = set(c['type'] for c in api_calls)
            return {'passed': True, 'message': f"API calls: {', '.join(call_types)}"}
        else:
            return {'passed': False, 'message': "No API calls found"}

        
    def _validate_react_conditional_rendering(self, pattern: Dict, semantics: Dict, code: str) -> Dict:
        """Validate React conditional rendering patterns"""
        conditional_type = pattern.get('conditional_type', 'any')
        
        # Check for ternary operators
        ternary_pattern = r'\?\s*[^:]+\s*:\s*'
        ternary_count = len(list(re.finditer(ternary_pattern, code)))
        
        # Check for && operator (short-circuit evaluation)
        and_conditional_pattern = r'{\s*\w+\s*&&\s*'
        and_conditional_count = len(list(re.finditer(and_conditional_pattern, code)))
        
        # Check for if statements in JSX
        if_statement_pattern = r'if\s*\([^)]+\)\s*{[^}]*return'
        if_count = len(list(re.finditer(if_statement_pattern, code, re.DOTALL)))
        
        # Check for switch statements
        switch_pattern = r'switch\s*\([^)]+\)'
        switch_count = len(list(re.finditer(switch_pattern, code)))
        
        total_conditionals = ternary_count + and_conditional_count + if_count + switch_count
        
        if conditional_type == 'any':
            if total_conditionals > 0:
                details = []
                if ternary_count > 0:
                    details.append(f"{ternary_count} ternary")
                if and_conditional_count > 0:
                    details.append(f"{and_conditional_count} && conditional")
                if if_count > 0:
                    details.append(f"{if_count} if statement")
                if switch_count > 0:
                    details.append(f"{switch_count} switch")
                return {'passed': True, 'message': f"Conditional rendering: {', '.join(details)}"}
            else:
                return {'passed': False, 'message': "No conditional rendering found"}
        
        elif conditional_type == 'ternary':
            if ternary_count > 0:
                return {'passed': True, 'message': f"Ternary operator used ({ternary_count} instances)"}
            else:
                return {'passed': False, 'message': "Ternary operator not found"}
        
        elif conditional_type == 'logical_and':
            if and_conditional_count > 0:
                return {'passed': True, 'message': f"Logical && used ({and_conditional_count} instances)"}
            else:
                return {'passed': False, 'message': "Logical && not found"}
        
        elif conditional_type == 'if_statement':
            if if_count > 0:
                return {'passed': True, 'message': f"If statement used ({if_count} instances)"}
            else:
                return {'passed': False, 'message': "If statement not found"}
        
        return {'passed': False, 'message': f"Unknown conditional type: {conditional_type}"}

    def _validate_react_event_handler(self, pattern: Dict, semantics: Dict, code: str) -> Dict:
        """Validate React event handler patterns"""
        event_handlers = semantics.get('event_handlers', [])
        event_type = pattern.get('event_type')
        handler_style = pattern.get('handler_style', 'any')  # 'inline', 'function_reference', 'arrow'
        
        if not event_handlers:
            return {'passed': False, 'message': "No event handlers found"}
        
        # If specific event type is required
        if event_type:
            matching_handlers = [h for h in event_handlers if h.get('event') == event_type.replace('on', '')]
            
            if not matching_handlers:
                return {'passed': False, 'message': f"Event handler '{event_type}' not found"}
            
            # Check handler style if specified
            if handler_style != 'any':
                if handler_style == 'inline':
                    inline_handlers = [h for h in matching_handlers if h.get('type') == 'inline']
                    if inline_handlers:
                        return {'passed': True, 'message': f"Inline {event_type} handler found"}
                    else:
                        return {'passed': False, 'message': f"{event_type} not using inline handler"}
                
                elif handler_style == 'function_reference':
                    ref_handlers = [h for h in matching_handlers if h.get('type') == 'function_reference']
                    if ref_handlers:
                        return {'passed': True, 'message': f"Function reference {event_type} handler found"}
                    else:
                        return {'passed': False, 'message': f"{event_type} not using function reference"}
                
                elif handler_style == 'arrow':
                    arrow_handlers = [h for h in matching_handlers if h.get('is_arrow_function')]
                    if arrow_handlers:
                        return {'passed': True, 'message': f"Arrow function {event_type} handler found"}
                    else:
                        return {'passed': False, 'message': f"{event_type} not using arrow function"}
            
            return {'passed': True, 'message': f"Event handler '{event_type}' found"}
        
        # General event handler check
        handler_types = set(h.get('type', 'unknown') for h in event_handlers)
        return {'passed': True, 'message': f"Event handlers found: {', '.join(handler_types)}"}
    


    def _validate_react_form_handling(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate React form handling patterns"""
        form_patterns = semantics.get('form_handling', {})
        form_type = pattern.get('form_type', 'any')
        
        controlled = form_patterns.get('controlled_components', [])
        uncontrolled = form_patterns.get('uncontrolled_components', [])
        form_libs = form_patterns.get('form_libraries', [])
        
        if form_type == 'any':
            if controlled or uncontrolled or form_libs:
                details = []
                if controlled:
                    details.append(f"{len(controlled)} controlled")
                if uncontrolled:
                    details.append(f"{len(uncontrolled)} uncontrolled")
                if form_libs:
                    details.append(f"libraries: {', '.join(form_libs)}")
                return {'passed': True, 'message': f"Form handling: {', '.join(details)}"}
            else:
                return {'passed': False, 'message': "No form handling found"}
        
        elif form_type == 'controlled':
            if controlled:
                return {'passed': True, 'message': f"Controlled components found ({len(controlled)})"}
            else:
                return {'passed': False, 'message': "No controlled components found"}
        
        elif form_type == 'uncontrolled':
            if uncontrolled:
                return {'passed': True, 'message': f"Uncontrolled components found ({len(uncontrolled)})"}
            else:
                return {'passed': False, 'message': "No uncontrolled components found"}
        
        elif form_type in ['formik', 'react-hook-form', 'final-form', 'redux-form']:
            if form_type in form_libs:
                return {'passed': True, 'message': f"{form_type} library detected"}
            else:
                return {'passed': False, 'message': f"{form_type} library not found"}
        
        return {'passed': False, 'message': f"Unknown form type: {form_type}"}


    def _validate_react_memoization(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate React memoization patterns"""
        memoization = semantics.get('memoization_usage', {})
        
        memo_type = pattern.get('memo_type', 'any')
        
        if memo_type == 'any':
            if any([
                memoization.get('react_memo'),
                memoization.get('use_memo'),
                memoization.get('use_callback'),
                memoization.get('pure_components')
            ]):
                details = []
                if memoization.get('memo_components_count', 0) > 0:
                    details.append(f"{memoization['memo_components_count']} React.memo")
                if memoization.get('use_memo_count', 0) > 0:
                    details.append(f"{memoization['use_memo_count']} useMemo")
                if memoization.get('use_callback_count', 0) > 0:
                    details.append(f"{memoization['use_callback_count']} useCallback")
                if memoization.get('pure_components'):
                    details.append("PureComponent")
                return {'passed': True, 'message': f"Memoization: {', '.join(details)}"}
            else:
                return {'passed': False, 'message': "No memoization found"}
        
        elif memo_type == 'react_memo':
            react_memo = memoization.get('react_memo', [])
            if react_memo:
                components = [m['component'] for m in react_memo]
                return {'passed': True, 'message': f"React.memo used on: {', '.join(components)}"}
            else:
                return {'passed': False, 'message': "React.memo not used"}
        
        elif memo_type == 'use_memo':
            use_memo = memoization.get('use_memo', [])
            if use_memo:
                return {'passed': True, 'message': f"useMemo used ({len(use_memo)} instances)"}
            else:
                return {'passed': False, 'message': "useMemo not used"}
        
        elif memo_type == 'use_callback':
            use_callback = memoization.get('use_callback', [])
            if use_callback:
                return {'passed': True, 'message': f"useCallback used ({len(use_callback)} instances)"}
            else:
                return {'passed': False, 'message': "useCallback not used"}
        
        elif memo_type == 'pure_component':
            if memoization.get('pure_components'):
                count = memoization['pure_components'][0].get('count', 0)
                return {'passed': True, 'message': f"PureComponent used ({count} classes)"}
            else:
                return {'passed': False, 'message': "PureComponent not used"}
        
        return {'passed': False, 'message': f"Unknown memoization type: {memo_type}"}

    def _validate_react_routing(self, pattern: Dict, semantics: Dict, code: str) -> Dict:
        """Validate React routing patterns"""
        routing = semantics.get('routing_usage', {})
        
        routing_type = pattern.get('routing_type', 'any')
        
        if not routing.get('router_detected'):
            return {'passed': False, 'message': "No routing library detected"}
        
        router_lib = routing.get('router_library', 'unknown')
        routes = routing.get('routes', [])
        nav_methods = routing.get('navigation_methods', [])
        route_params = routing.get('route_params', [])
        
        if routing_type == 'any':
            details = [f"Library: {router_lib}"]
            if routes:
                details.append(f"{len(routes)} routes")
            if nav_methods:
                details.append(f"Navigation: {', '.join(set(nav_methods))}")
            if route_params:
                params = [rp['param'] for rp in route_params]
                details.append(f"Parameters: {', '.join(set(params))}")
            return {'passed': True, 'message': f"Routing: {', '.join(details)}"}
        
        elif routing_type == 'react-router':
            if router_lib == 'react-router':
                return {'passed': True, 'message': "React Router detected"}
            else:
                return {'passed': False, 'message': f"React Router not found (found: {router_lib})"}
        
        elif routing_type == 'route_definition':
            required_path = pattern.get('path')
            if required_path:
                matching = [r for r in routes if required_path in r.get('path', '')]
                if matching:
                    return {'passed': True, 'message': f"Route '{required_path}' found"}
                else:
                    return {'passed': False, 'message': f"Route '{required_path}' not found"}
            else:
                if routes:
                    paths = [r.get('path', 'unknown') for r in routes]
                    return {'passed': True, 'message': f"Routes defined: {', '.join(paths)}"}
                return {'passed': False, 'message': "No routes defined"}
        
        elif routing_type == 'navigation':
            required_method = pattern.get('method')
            if required_method:
                if required_method in nav_methods:
                    return {'passed': True, 'message': f"Navigation method '{required_method}' found"}
                else:
                    return {'passed': False, 'message': f"Navigation method '{required_method}' not found"}
            else:
                if nav_methods:
                    return {'passed': True, 'message': f"Navigation methods: {', '.join(set(nav_methods))}"}
                return {'passed': False, 'message': "No navigation methods found"}
        
        elif routing_type == 'route_params':
            required_param = pattern.get('param')
            if required_param:
                param_names = [rp['param'] for rp in route_params]
                if required_param in param_names:
                    return {'passed': True, 'message': f"Route parameter ':{required_param}' found"}
                else:
                    return {'passed': False, 'message': f"Route parameter ':{required_param}' not found"}
            else:
                if route_params:
                    params = [rp['param'] for rp in route_params]
                    return {'passed': True, 'message': f"Route parameters: {', '.join(set(params))}"}
                return {'passed': False, 'message': "No route parameters found"}
        
        elif routing_type == 'nested_routes':
            if routing.get('nested_routes'):
                return {'passed': True, 'message': "Nested routes detected"}
            else:
                return {'passed': False, 'message': "No nested routes found"}
        
        elif routing_type == 'link_component':
            if 'link_component' in nav_methods or 'navlink_component' in nav_methods:
                return {'passed': True, 'message': "Link component used"}
            else:
                return {'passed': False, 'message': "Link component not found"}
        
        return {'passed': False, 'message': f"Unknown routing type: {routing_type}"}              


    def _validate_react_custom_hook(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate React custom hook patterns"""
        custom_hooks = semantics.get('custom_hooks', [])
        
        hook_name = pattern.get('hook_name')
        must_use_hooks = pattern.get('must_use_react_hooks', False)
        must_return = pattern.get('must_return', False)
        
        if not custom_hooks:
            return {'passed': False, 'message': "No custom hooks found"}
        
        if hook_name:
            matching = [h for h in custom_hooks if h['name'] == hook_name]
            if not matching:
                return {'passed': False, 'message': f"Custom hook '{hook_name}' not found"}
            
            hook = matching[0]
            
            # Check if it uses React hooks
            if must_use_hooks and not hook.get('uses_react_hooks'):
                return {'passed': False, 'message': f"Custom hook '{hook_name}' doesn't use React hooks"}
            
            # Check if it returns a value
            if must_return and not hook.get('returns_value'):
                return {'passed': False, 'message': f"Custom hook '{hook_name}' doesn't return a value"}
            
            details = []
            if hook.get('uses_react_hooks'):
                details.append("uses React hooks")
            if hook.get('returns_value'):
                details.append("returns value")
            params = hook.get('params', [])
            if params:
                details.append(f"params: {', '.join(params)}")
            
            return {'passed': True, 'message': f"Custom hook '{hook_name}' found ({', '.join(details)})"}
        
        else:
            # General validation
            hook_names = [h['name'] for h in custom_hooks]
            hooks_using_react = [h for h in custom_hooks if h.get('uses_react_hooks')]
            
            details = [f"{len(custom_hooks)} custom hooks: {', '.join(hook_names)}"]
            if hooks_using_react:
                details.append(f"{len(hooks_using_react)} use React hooks")
            
            return {'passed': True, 'message': '; '.join(details)}


    def _validate_react_context_usage(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate React Context API usage"""
        component_state = semantics.get('component_state', {})
        context_state = component_state.get('context_state', [])
        
        context_type = pattern.get('context_type', 'any')
        
        if not context_state:
            return {'passed': False, 'message': "No Context usage found"}
        
        if context_type == 'any':
            create_contexts = [c for c in context_state if c['type'] == 'create_context']
            use_contexts = [c for c in context_state if c['type'] == 'use_context']
            
            details = []
            if create_contexts:
                details.append(f"{len(create_contexts)} createContext calls")
            if use_contexts:
                details.append(f"{len(use_contexts)} useContext calls")
            
            return {'passed': True, 'message': f"Context usage: {', '.join(details)}"}
        
        elif context_type == 'create_context':
            create_contexts = [c for c in context_state if c['type'] == 'create_context']
            if create_contexts:
                return {'passed': True, 'message': f"createContext used ({len(create_contexts)} instances)"}
            else:
                return {'passed': False, 'message': "createContext not found"}
        
        elif context_type == 'use_context':
            use_contexts = [c for c in context_state if c['type'] == 'use_context']
            if use_contexts:
                contexts = [c.get('context_ref', 'unknown') for c in use_contexts]
                return {'passed': True, 'message': f"useContext used: {', '.join(contexts)}"}
            else:
                return {'passed': False, 'message': "useContext not found"}
        
        elif context_type == 'provider':
            # Check for Context.Provider in code
            provider_pattern = r'\.Provider'
            # This would need to be checked in the actual code
            # For now, check if createContext exists (providers typically follow)
            create_contexts = [c for c in context_state if c['type'] == 'create_context']
            if create_contexts:
                return {'passed': True, 'message': "Context provider likely present"}
            else:
                return {'passed': False, 'message': "Context provider not detected"}
        
        elif context_type == 'consumer':
            # Check for Context.Consumer pattern
            use_contexts = [c for c in context_state if c['type'] == 'use_context']
            if use_contexts:
                return {'passed': True, 'message': f"Context consumer pattern found ({len(use_contexts)})"}
            else:
                return {'passed': False, 'message': "Context consumer pattern not found"}
        
        return {'passed': False, 'message': f"Unknown context type: {context_type}"}


    def _validate_react_ref_usage(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate React ref usage patterns"""
        hook_calls = semantics.get('hook_calls', [])
        
        ref_type = pattern.get('ref_type', 'any')
        
        # Find useRef calls
        use_ref_calls = [h for h in hook_calls if h['hook'] == 'useRef']
        
        # Find useImperativeHandle calls
        imperative_handle_calls = [h for h in hook_calls if h['hook'] == 'useImperativeHandle']
        
        # Find createRef calls (class components)
        # This would be in semantics if we tracked it
        
        if ref_type == 'any':
            if use_ref_calls or imperative_handle_calls:
                details = []
                if use_ref_calls:
                    details.append(f"{len(use_ref_calls)} useRef")
                if imperative_handle_calls:
                    details.append(f"{len(imperative_handle_calls)} useImperativeHandle")
                return {'passed': True, 'message': f"Ref usage: {', '.join(details)}"}
            else:
                return {'passed': False, 'message': "No ref usage found"}
        
        elif ref_type == 'use_ref':
            if use_ref_calls:
                return {'passed': True, 'message': f"useRef used ({len(use_ref_calls)} instances)"}
            else:
                return {'passed': False, 'message': "useRef not found"}
        
        elif ref_type == 'imperative_handle':
            if imperative_handle_calls:
                return {'passed': True, 'message': f"useImperativeHandle used ({len(imperative_handle_calls)} instances)"}
            else:
                return {'passed': False, 'message': "useImperativeHandle not found"}
        
        elif ref_type == 'forward_ref':
            # Check for React.forwardRef in component types
            component_types = semantics.get('component_types', {})
            forward_ref_count = component_types.get('forward_ref_components', 0)
            if forward_ref_count > 0:
                return {'passed': True, 'message': f"forwardRef used ({forward_ref_count} components)"}
            else:
                return {'passed': False, 'message': "forwardRef not found"}
        
        elif ref_type == 'callback_ref':
            # Check for callback refs (ref={callbackFunction})
            # This is hard to detect without parsing JSX attributes
            # For now, check if refs are used at all
            if use_ref_calls:
                return {'passed': True, 'message': "Ref usage detected (possible callback ref)"}
            else:
                return {'passed': False, 'message': "Callback ref not detected"}
        
        elif ref_type == 'dom_ref':
            # Check if useRef is used (typically for DOM refs)
            if use_ref_calls:
                # Check initial values - DOM refs typically initialized with null
                null_init = [h for h in use_ref_calls if h.get('params', '').strip() in ['null', '(null)', '']]
                if null_init:
                    return {'passed': True, 'message': f"DOM ref found ({len(null_init)} instances)"}
                else:
                    return {'passed': True, 'message': f"useRef found ({len(use_ref_calls)} instances, possibly DOM refs)"}
            else:
                return {'passed': False, 'message': "DOM ref not found"}
        
        elif ref_type == 'mutable_ref':
            # Check if useRef is used with non-null initial value (for mutable values)
            if use_ref_calls:
                non_null = [h for h in use_ref_calls if h.get('params', '').strip() not in ['null', '(null)', '']]
                if non_null:
                    return {'passed': True, 'message': f"Mutable ref found ({len(non_null)} instances)"}
                else:
                    return {'passed': False, 'message': "Mutable ref not found (all refs initialized with null)"}
            else:
                return {'passed': False, 'message': "No ref usage found"}
        
        return {'passed': False, 'message': f"Unknown ref type: {ref_type}"}

    
    # Generic validation methods
    def _validate_generic_pattern(self, pattern_type: str, pattern: Dict, semantics: Dict, code: str) -> Dict:
        """Validate generic patterns"""
        if pattern_type == 'constructor_call':
            return self._validate_constructor_call(pattern, semantics)
        elif pattern_type == 'method_call':
            return self._validate_method_call(pattern, semantics)
        elif pattern_type == 'async_pattern':
            return self._validate_async_pattern(pattern, semantics)
        elif pattern_type == 'return_statement':
            return self._validate_return_statement(pattern, semantics)
        elif pattern_type == 'cleanup_function':
            return self._validate_cleanup_function(pattern, semantics)
        else:
            return {'passed': False, 'message': f"Unknown pattern type: {pattern_type}"}
    
    def _validate_constructor_call(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate constructor call pattern"""
        class_name = pattern.get('class')
        context = pattern.get('context')
        
        constructors = semantics.get('constructor_calls', [])
        matching = [c for c in constructors if c['class'] == class_name]
        
        if not matching:
            return {'passed': False, 'message': f"new {class_name}() not found"}
        
        if context == 'inside_function':
            inside = [c for c in matching if c['context'] == 'inside_function']
            if inside:
                return {'passed': True, 'message': f"new {class_name}() found inside function"}
            else:
                return {'passed': False, 'message': f"new {class_name}() not inside function"}
        
        return {'passed': True, 'message': f"new {class_name}() found"}
    
    def _validate_method_call(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate method call pattern"""
        obj = pattern.get('object')
        method = pattern.get('method')
        
        method_calls = semantics.get('method_calls', {})
        
        if obj in method_calls and method in method_calls[obj]:
            return {'passed': True, 'message': f"{obj}.{method}() call found"}
        else:
            return {'passed': False, 'message': f"{obj}.{method}() call not found"}
    
    def _validate_async_pattern(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate async pattern"""
        context = pattern.get('context')
        
        async_patterns = semantics.get('async_patterns', [])
        
        if not async_patterns:
            return {'passed': False, 'message': "No async functions found"}
        
        if context == 'fetch_call':
            with_fetch = [p for p in async_patterns if p.get('uses_fetch')]
            if with_fetch:
                return {'passed': True, 'message': "async/await with fetch found"}
            else:
                return {'passed': False, 'message': "async function exists but doesn't use fetch"}
        
        return {'passed': True, 'message': f"async functions found: {len(async_patterns)}"}
    
    def _validate_return_statement(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate return statement pattern"""
        returns_spec = pattern.get('returns', {})
        required_props = returns_spec.get('required_properties', [])
        
        returns = semantics.get('return_statements', [])
        
        if not returns:
            return {'passed': False, 'message': "No return statement found"}
        
        for ret in returns:
            if all(prop in ret['properties'] for prop in required_props):
                return {'passed': True, 'message': f"Return contains: {', '.join(required_props)}"}
        
        return {'passed': False, 'message': f"Return missing: {', '.join(required_props)}"}
    
    def _validate_cleanup_function(self, pattern: Dict, semantics: Dict) -> Dict:
        """Validate cleanup function pattern"""
        cleanups = semantics.get('cleanup_functions', [])
        
        if not cleanups:
            return {'passed': False, 'message': "useEffect not found"}
        
        with_cleanup = [c for c in cleanups if c['has_cleanup']]
        
        if with_cleanup:
            return {'passed': True, 'message': "useEffect returns cleanup function"}
        else:
            return {'passed': False, 'message': "useEffect doesn't return cleanup function"}
    
    def _validate_legacy_pattern(self, pattern: str, code: str) -> Dict:
        """Fallback for old string patterns"""
        keywords = [kw.lower() for kw in pattern.split() if len(kw) > 3]
        if any(keyword in code.lower() for keyword in keywords):
            return {'passed': True, 'message': pattern}
        else:
            return {'passed': False, 'message': pattern}
    
    # Placeholder methods for other framework patterns
    def _validate_express_pattern(self, pattern_type: str, pattern: Dict, semantics: Dict, code: str) -> Dict:
        return {'passed': False, 'message': f"Express pattern validation not implemented: {pattern_type}"}
    
    def _validate_angular_pattern(self, pattern_type: str, pattern: Dict, semantics: Dict, code: str) -> Dict:
        return {'passed': False, 'message': f"Angular pattern validation not implemented: {pattern_type}"}
    


# ===== Enhanced Validation Engine (UPDATED to use both validators) =====

class EnhancedValidationEngine:
    """Enhanced validation engine with comprehensive framework support"""
    
    def __init__(self):
        self.validators = [
            BeginnerValidator(),  # Original beginner validator
            EnhancedIntermediateValidator(),  # New enhanced intermediate validator
            # Add ProValidator when needed
        ]
    
    def validate_submission(self, parsed_code: Dict[str, Any], validation_spec: Dict[str, Any], code: str) -> Dict[str, Any]:
        """Main validation entry point"""
        difficulty = validation_spec.get('difficulty', 'beginner')
        framework = validation_spec.get('framework', 'unknown')
        
        logger.info(f"Validation: {difficulty}/{framework}")
        
        # Find appropriate validator
        validator = self._select_validator(difficulty, framework)
        
        if not validator:
            logger.error(f"No validator for {difficulty}/{framework}")
            return {
                'error': f'No validator found for difficulty: {difficulty}, framework: {framework}',
                'overall_score': 0,
                'passed': False
            }
        
        logger.debug(f"Using {validator.__class__.__name__}")
        
        # Run validation
        try:
            results = validator.validate(parsed_code, validation_spec, code)
        except Exception as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            return {
                'error': f'Validation error: {str(e)}',
                'overall_score': 0,
                'passed': False,
                'imports': {'passed': False, 'score': 0, 'details': []},
                'structure': {'passed': False, 'score': 0, 'details': [str(e)]},
                'behavior': {'passed': False, 'score': 0, 'details': []}
            }
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(results, validation_spec)
        
        logger.info(f"Score: {overall_score:.1f}")
        
        return {
            **results,
            'overall_score': overall_score,
            'passed': overall_score >= validation_spec.get('passing_score', 70),
            'validator_used': validator.__class__.__name__
        }
    
    def _select_validator(self, difficulty: str, framework: str) -> Optional[BaseValidator]:
        for validator in self.validators:
            if validator.can_handle(difficulty, framework):
                return validator
        return None
    
    def _calculate_overall_score(self, results: Dict[str, Any], validation_spec: Dict[str, Any]) -> float:
        """Calculate weighted overall score"""
        scoring = validation_spec.get('scoring', {})
        import_weight = scoring.get('import_weight', 15)
        structure_weight = scoring.get('structure_weight', 25)
        behavior_weight = scoring.get('behavior_weight', 60)
        
        total_score = 0.0
        total_weight = 0.0
        
        components = [
            ('imports', import_weight),
            ('structure', structure_weight),
            ('behavior', behavior_weight)
        ]
        
        for component_name, weight in components:
            if component_name in results and isinstance(results[component_name], dict):
                component_score = results[component_name].get('score', 0)
                total_score += component_score * (weight / 100)
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return (total_score / total_weight) * 100