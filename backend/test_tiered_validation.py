"""
Test script for tiered validation system
"""

from validation.services.parser_service import ParserService
from validation.services.tiered_validator import ValidationEngine

# Test beginner-level Django code
beginner_code = """
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True, db_index=True)
    published_date = models.DateField()
    pages = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
"""

# Parse code
parsed = ParserService.parse_python(beginner_code)

# Validation spec
validation_spec = {
    'difficulty': 'beginner',
    'framework': 'django',
    'required_imports': ['django.db.models'],
    'required_structure': {
        'class_name': 'Book',
        'parent_class': 'models.Model',
        'methods': ['__str__']
    },
    'behavior_patterns': [
        'CharField with max_length',
        'unique=True on isbn',
        'BooleanField with default'
    ],
    'scoring': {
        'import_weight': 15,
        'structure_weight': 40,
        'behavior_weight': 45
    },
    'passing_score': 75
}

# Run validation
engine = ValidationEngine()
results = engine.validate_submission(parsed, validation_spec, beginner_code)

print("="*60)
print("TIERED VALIDATION TEST RESULTS")
print("="*60)
print(f"Validator Used: {results.get('validator_used')}")
print(f"Overall Score: {results.get('overall_score'):.2f}")
print(f"Passed: {results.get('passed')}")
print("\nImports:")
print(f"  Score: {results.get('imports', {}).get('score', 0):.2f}")
print(f"  Details: {results.get('imports', {}).get('details', [])}")
print("\nStructure:")
print(f"  Score: {results.get('structure', {}).get('score', 0):.2f}")
print(f"  Details: {results.get('structure', {}).get('details', [])}")
print("\nBehavior:")
print(f"  Score: {results.get('behavior', {}).get('score', 0):.2f}")
print(f"  Details: {results.get('behavior', {}).get('details', [])}")
print("="*60)