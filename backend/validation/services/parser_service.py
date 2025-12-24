"""
Enhanced Parser Service - Parse code to AST with improved JavaScript support
Handles Python (Django) and JavaScript/TypeScript (React, Angular, Express)
"""

import ast
import json
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('validation')


class ParserService:
    """Enhanced service to parse code into Abstract Syntax Trees"""
    
    @staticmethod
    def parse_code(code: str, language: str) -> Dict[str, Any]:
        """
        Parse code based on language
        
        Args:
            code: Source code to parse
            language: 'python' or 'javascript'
            
        Returns:
            dict: Parsed AST and metadata
        """
        if language == 'python':
            return ParserService.parse_python(code)
        elif language in ['javascript', 'typescript']:
            return ParserService.parse_javascript_enhanced(code)
        else:
            return {
                'success': False,
                'error': f'Unsupported language: {language}',
                'ast': None
            }
    
    @staticmethod
    def parse_python(code: str) -> Dict[str, Any]:
        """
        Parse Python code using ast module
        
        Returns:
            dict: {
                'success': bool,
                'ast': dict or None,
                'error': str or None,
                'imports': list,
                'classes': list,
                'functions': list
            }
        """
        logger.debug(f"Parsing Python: {len(code)} chars")
        try:
            # Parse code to AST
            tree = ast.parse(code)
            
            # Extract components
            imports = ParserService._extract_python_imports(tree)
            classes = ParserService._extract_python_classes(tree)
            functions = ParserService._extract_python_functions(tree)
            
            logger.debug(f"Parse OK: {len(imports)} imports, {len(classes)} classes")
            return {
                'success': True,
                'ast': ast.dump(tree),
                'error': None,
                'imports': imports,
                'classes': classes,
                'functions': functions,
                'tree': tree,  # Keep original tree for detailed analysis
                'language': 'python'
            }
            
        except SyntaxError as e:
            logger.warning(f"Syntax error line {e.lineno}: {e.msg}")
            return {
                'success': False,
                'ast': None,
                'error': f'Line {e.lineno}: {e.msg}',
                'line': e.lineno,
                'offset': e.offset,
                'imports': [],
                'classes': [],
                'functions': [],
                'language': 'python'
            }
        except Exception as e:
            return {
                'success': False,
                'ast': None,
                'error': str(e),
                'imports': [],
                'classes': [],
                'functions': [],
                'language': 'python'
            }
    
    @staticmethod
    def parse_javascript_enhanced(code: str) -> Dict[str, Any]:
        """
        Enhanced JavaScript/TypeScript parsing with fallback to regex patterns
        
        Returns:
            dict: Parsed structure with comprehensive data
        """
        logger.debug(f"Parsing JavaScript: {len(code)} chars")
        
        # First try Node.js with esprima for accurate parsing
        node_result = ParserService._parse_javascript_with_node(code)
        
        if node_result.get('success'):
            logger.debug("JavaScript parsed successfully with Node.js")
            return {**node_result, 'language': 'javascript', 'parser_used': 'esprima'}
        
        # Fallback to regex-based parsing
        logger.debug("Falling back to regex-based JavaScript parsing")
        regex_result = ParserService._parse_javascript_with_regex(code)
        
        return {**regex_result, 'language': 'javascript', 'parser_used': 'regex'}
    
    @staticmethod
    def _parse_javascript_with_regex(code: str) -> Dict[str, Any]:
        """
        Parse JavaScript using regex patterns when Node.js is not available
        
        Returns:
            dict: Parsed structure with regex-extracted components
        """
        try:
            imports = ParserService._extract_js_imports_regex(code)
            classes = ParserService._extract_js_classes_regex(code)
            functions = ParserService._extract_js_functions_regex(code)
            exports = ParserService._extract_js_exports_regex(code)
            
            return {
                'success': True,
                'imports': imports,
                'classes': classes,
                'functions': functions,
                'exports': exports,
                'ast_type': 'regex'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Regex parsing failed: {str(e)}',
                'imports': [],
                'classes': [],
                'functions': []
            }
    
    @staticmethod
    def _parse_javascript_with_node(code: str) -> Dict[str, Any]:
        """Parse JavaScript using Node.js and esprima - SUPPORTS BOTH ES6 AND COMMONJS"""
        try:
            # Create temporary file with JS code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Enhanced parser script with CommonJS support
            parser_script = f"""
    const fs = require('fs');
    const esprima = require('esprima');

    try {{
        const code = fs.readFileSync('{temp_path}', 'utf8');
        const ast = esprima.parseModule(code, {{ 
            jsx: true, 
            tolerant: true,
            range: true,
            tokens: true
        }});
        
        // Extract imports - HANDLES BOTH ES6 AND COMMONJS
        const imports = [];
        
        // ES6 imports: import x from 'module'
        ast.body
            .filter(node => node.type === 'ImportDeclaration')
            .forEach(node => {{
                imports.push({{
                    type: 'import',
                    module: node.source.value,
                    specifiers: node.specifiers.map(spec => ({{
                        type: spec.type,
                        local: spec.local.name,
                        imported: spec.imported ? spec.imported.name : 'default'
                    }})),
                    line: node.loc ? node.loc.start.line : null
                }});
            }});
        
        // CommonJS requires: const x = require('module')
        ast.body
            .filter(node => node.type === 'VariableDeclaration')
            .forEach(node => {{
                node.declarations.forEach(decl => {{
                    if (decl.init && decl.init.type === 'CallExpression' && 
                        decl.init.callee.name === 'require') {{
                        imports.push({{
                            type: 'require',
                            module: decl.init.arguments[0].value,
                            specifiers: [{{
                                type: 'RequireSpecifier',
                                local: decl.id.name,
                                imported: 'default'
                            }}],
                            line: node.loc ? node.loc.start.line : null
                        }});
                    }}
                }});
            }});
        
        // Extract classes with methods and properties
        const classes = ast.body
            .filter(node => node.type === 'ClassDeclaration')
            .map(node => ({{
                name: node.id ? node.id.name : 'anonymous',
                superClass: node.superClass ? node.superClass.name : null,
                methods: node.body.body
                    .filter(method => method.type === 'MethodDefinition')
                    .map(method => ({{
                        name: method.key.name,
                        kind: method.kind,
                        static: method.static,
                        line: method.loc ? method.loc.start.line : null
                    }})),
                line: node.loc ? node.loc.start.line : null
            }}));
        
        // Extract functions (including arrow functions and function expressions)
        const functions = [];
        ast.body.forEach(node => {{
            if (node.type === 'FunctionDeclaration') {{
                functions.push({{
                    name: node.id ? node.id.name : 'anonymous',
                    type: 'function',
                    params: node.params.map(param => param.name),
                    line: node.loc ? node.loc.start.line : null
                }});
            }} else if (node.type === 'VariableDeclaration') {{
                node.declarations.forEach(decl => {{
                    if (decl.init && (
                        decl.init.type === 'FunctionExpression' || 
                        decl.init.type === 'ArrowFunctionExpression'
                    )) {{
                        functions.push({{
                            name: decl.id.name,
                            type: decl.init.type === 'ArrowFunctionExpression' ? 'arrow' : 'function',
                            params: decl.init.params.map(param => param.name),
                            line: decl.loc ? decl.loc.start.line : null
                        }});
                    }}
                }});
            }}
        }});
        
        // Extract exports - SUPPORTS BOTH SYNTAXES
        const exports = [];
        
        // ES6 exports
        ast.body
            .filter(node => node.type === 'ExportNamedDeclaration' || node.type === 'ExportDefaultDeclaration')
            .forEach(node => {{
                exports.push({{
                    type: node.type,
                    declaration: node.declaration ? node.declaration.name : null,
                    line: node.loc ? node.loc.start.line : null
                }});
            }});
        
        // CommonJS module.exports
        ast.body
            .filter(node => node.type === 'AssignmentExpression' || node.type === 'ExpressionStatement')
            .forEach(node => {{
                if (node.type === 'ExpressionStatement' && node.expression.type === 'AssignmentExpression') {{
                    const expr = node.expression;
                    if (expr.left.type === 'MemberExpression' && 
                        expr.left.object.name === 'module' && 
                        expr.left.property.name === 'exports') {{
                        exports.push({{
                            type: 'ModuleExports',
                            declaration: expr.right.name || 'object',
                            line: node.loc ? node.loc.start.line : null
                        }});
                    }}
                }}
            }});
        
        console.log(JSON.stringify({{
            success: true,
            imports: imports,
            classes: classes,
            functions: functions,
            exports: exports,
            ast_type: 'esprima'
        }}));
        
    }} catch (error) {{
        console.log(JSON.stringify({{
            success: false,
            error: error.message,
            line: error.lineNumber
        }}));
    }} finally {{
        try {{
            fs.unlinkSync('{temp_path}');
        }} catch (e) {{
            // Ignore cleanup errors
        }}
    }}
    """
            
            # Try to run with Node.js
            result = subprocess.run(
                ['node', '-e', parser_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                parsed = json.loads(result.stdout)
                logger.debug("JavaScript parsed (ES6 + CommonJS support)")
                return parsed
            else:
                return {
                    'success': False,
                    'error': f'Node.js parser error: {result.stderr}',
                    'imports': [],
                    'classes': [],
                    'functions': []
                }
                
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'Node.js not available for JavaScript parsing',
                'imports': [],
                'classes': [],
                'functions': []
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'JavaScript parsing timeout - code too complex',
                'imports': [],
                'classes': [],
                'functions': []
            }
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': 'Failed to parse JavaScript parser output',
                'imports': [],
                'classes': [],
                'functions': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'JavaScript parsing failed: {str(e)}',
                'imports': [],
                'classes': [],
                'functions': []
            }
    
    @staticmethod
    def _extract_js_imports_regex(code: str) -> list:
        """Extract JavaScript imports using regex patterns"""
        imports = []
        
        # ES6 imports: import { x } from 'module'
        import_pattern = r'import\s+(?:(?:\*\s+as\s+(\w+))|(?:\{([^}]+)\})|([^;]+?))\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, code):
            default_import, named_imports, star_import, module = match.groups()
            
            if default_import:
                imports.append({
                    'type': 'import',
                    'module': module,
                    'specifiers': [{'type': 'ImportDefaultSpecifier', 'local': default_import, 'imported': 'default'}],
                    'line': ParserService._get_line_number(code, match.start())
                })
            elif named_imports:
                for specifier in named_imports.split(','):
                    specifier = specifier.strip()
                    if ' as ' in specifier:
                        imported, local = specifier.split(' as ')
                        imports.append({
                            'type': 'import',
                            'module': module,
                            'specifiers': [{'type': 'ImportSpecifier', 'local': local.strip(), 'imported': imported.strip()}],
                            'line': ParserService._get_line_number(code, match.start())
                        })
                    else:
                        imports.append({
                            'type': 'import',
                            'module': module,
                            'specifiers': [{'type': 'ImportSpecifier', 'local': specifier, 'imported': specifier}],
                            'line': ParserService._get_line_number(code, match.start())
                        })
            elif star_import:
                imports.append({
                    'type': 'import',
                    'module': module,
                    'specifiers': [{'type': 'ImportNamespaceSpecifier', 'local': star_import.strip(), 'imported': '*'}],
                    'line': ParserService._get_line_number(code, match.start())
                })
        
        # CommonJS requires: const x = require('module')
        require_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        for match in re.finditer(require_pattern, code):
            local, module = match.groups()
            imports.append({
                'type': 'require',
                'module': module,
                'specifiers': [{'type': 'RequireSpecifier', 'local': local, 'imported': 'default'}],
                'line': ParserService._get_line_number(code, match.start())
            })
        
        return imports
    
    @staticmethod
    def _extract_js_classes_regex(code: str) -> list:
        """Extract JavaScript classes using regex patterns"""
        classes = []
        
        # Class declarations: class MyClass { ... }
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{([^}]*)\}'
        for match in re.finditer(class_pattern, code, re.DOTALL):
            class_name, super_class, class_body = match.groups()
            
            # Extract methods from class body
            methods = []
            method_pattern = r'(\w+)\s*\([^)]*\)\s*\{[^}]*\}'
            for method_match in re.finditer(method_pattern, class_body):
                methods.append({
                    'name': method_match.group(1),
                    'kind': 'method',
                    'static': 'static' in method_match.group(0),
                    'line': ParserService._get_line_number(code, match.start() + method_match.start())
                })
            
            # Extract constructor
            if 'constructor(' in class_body:
                methods.append({
                    'name': 'constructor',
                    'kind': 'constructor',
                    'static': False,
                    'line': ParserService._get_line_number(code, match.start())
                })
            
            classes.append({
                'name': class_name,
                'superClass': super_class,
                'methods': methods,
                'line': ParserService._get_line_number(code, match.start())
            })
        
        return classes
    
    @staticmethod
    def _extract_js_functions_regex(code: str) -> list:
        """Extract JavaScript functions using regex patterns"""
        functions = []
        
        # Function declarations: function myFunc() { ... }
        func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*\{'
        for match in re.finditer(func_pattern, code):
            func_name, params = match.groups()
            functions.append({
                'name': func_name,
                'type': 'function',
                'params': [p.strip() for p in params.split(',') if p.strip()],
                'line': ParserService._get_line_number(code, match.start())
            })
        
        # Arrow functions: const myFunc = () => { ... }
        arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*\{'
        for match in re.finditer(arrow_pattern, code):
            func_name, params = match.groups()
            functions.append({
                'name': func_name,
                'type': 'arrow',
                'params': [p.strip() for p in params.split(',') if p.strip()],
                'line': ParserService._get_line_number(code, match.start())
            })
        
        # React components: const MyComponent = () => { ... }
        react_pattern = r'(?:const|let|var)\s+([A-Z][\w]*)\s*=\s*(?:\([^)]*\)|\(\))\s*=>\s*\{'
        for match in re.finditer(react_pattern, code):
            comp_name = match.group(1)
            functions.append({
                'name': comp_name,
                'type': 'react_component',
                'params': ['props'],
                'line': ParserService._get_line_number(code, match.start())
            })
        
        return functions
    
    @staticmethod
    def _extract_js_exports_regex(code: str) -> list:
        """Extract JavaScript exports using regex patterns"""
        exports = []
        
        # Named exports: export { name1, name2 }
        named_export_pattern = r'export\s+\{([^}]+)\}'
        for match in re.finditer(named_export_pattern, code):
            exports_list = match.group(1)
            for export_name in exports_list.split(','):
                exports.append({
                    'type': 'ExportNamedDeclaration',
                    'declaration': export_name.strip(),
                    'line': ParserService._get_line_number(code, match.start())
                })
        
        # Default exports: export default MyComponent
        default_export_pattern = r'export\s+default\s+(\w+)'
        for match in re.finditer(default_export_pattern, code):
            export_name = match.group(1)
            exports.append({
                'type': 'ExportDefaultDeclaration',
                'declaration': export_name,
                'line': ParserService._get_line_number(code, match.start())
            })
        
        # Module.exports: module.exports = { ... }
        module_export_pattern = r'module\.exports\s*=\s*(\w+|{)'
        for match in re.finditer(module_export_pattern, code):
            exports.append({
                'type': 'ModuleExports',
                'declaration': match.group(1),
                'line': ParserService._get_line_number(code, match.start())
            })
        
        return exports
    
    @staticmethod
    def _get_line_number(code: str, position: int) -> int:
        """Get line number from character position"""
        return code[:position].count('\n') + 1
    
    # Python-specific methods (unchanged from original)
    @staticmethod
    def _extract_python_imports(tree: ast.AST) -> list:
        """Extract import statements from Python AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
        
        return imports
    
    @staticmethod
    def _extract_python_classes(tree: ast.AST) -> list:
        """Extract class definitions from Python AST"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Get parent classes
                bases = [ParserService._get_node_name(base) for base in node.bases]
                
                # Get methods
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            'name': item.name,
                            'line': item.lineno,
                            'args': [arg.arg for arg in item.args.args],
                            'decorators': [ParserService._get_node_name(dec) for dec in item.decorator_list]
                        })
                
                # Get class variables/fields
                fields = []
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                fields.append(target.id)
                
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'bases': bases,
                    'methods': methods,
                    'fields': fields,
                    'decorators': [ParserService._get_node_name(dec) for dec in node.decorator_list]
                })
        
        return classes
    
    @staticmethod
    def _extract_python_functions(tree: ast.AST) -> list:
        """Extract top-level function definitions from Python AST"""
        functions = []
        
        for node in tree.body:  # Only top-level functions
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [ParserService._get_node_name(dec) for dec in node.decorator_list]
                })
        
        return functions
    
    @staticmethod
    def _get_node_name(node) -> str:
        """Extract name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{ParserService._get_node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return ParserService._get_node_name(node.func)
        else:
            return str(node)