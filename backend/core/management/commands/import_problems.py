"""
Management command to import problems from JSON files.
Usage: python manage.py import_problems [path]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from pathlib import Path
import json
from core.models import Framework, Category
from problems.models import Problem, Pattern
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Import problems from JSON files into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            'path',
            nargs='?',
            type=str,
            default='problems_data',
            help='Path to problems directory (default: problems_data)'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing problems before importing',
        )
        parser.add_argument(
            '--skip-validation',
            action='store_true',
            help='Skip validation and import anyway',
        )

    def handle(self, *args, **options):
        path = Path(options['path'])
        reset = options['reset']
        skip_validation = options['skip_validation']

        if not path.exists():
            self.stdout.write(self.style.ERROR(f'Path does not exist: {path}'))
            return

        # Get or create admin user for created_by field
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@gagoforge.com',
                'is_staff': True,
                'is_superuser': True
            }
        )

        if reset:
            self.stdout.write(self.style.WARNING('Deleting existing problems and patterns...'))
            Pattern.objects.all().delete()
            Problem.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Deleted successfully\n'))

        # Find all JSON files
        json_files = list(path.rglob('*.json'))
        json_files = [f for f in json_files if f.name != 'category_mappings.json']

        if not json_files:
            self.stdout.write(self.style.WARNING('No problem JSON files found'))
            return

        self.stdout.write(f'Found {len(json_files)} problem files\n')

        created_count = 0
        updated_count = 0
        error_count = 0
        skipped_count = 0

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Basic validation
                required_fields = ['problem_id', 'title', 'framework', 'category', 'difficulty']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields and not skip_validation:
                    self.stdout.write(
                        self.style.ERROR(f'✗ {json_file.name} - Missing fields: {", ".join(missing_fields)}')
                    )
                    error_count += 1
                    continue

                # Get framework and category
                try:
                    framework = Framework.objects.get(name=data['framework'])
                except Framework.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'✗ {json_file.name} - Framework not found: {data["framework"]}')
                    )
                    error_count += 1
                    continue

                try:
                    category = Category.objects.get(
                        framework=framework,
                        name=data['category']
                    )
                except Category.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'✗ {json_file.name} - Category not found: {data["category"]}')
                    )
                    error_count += 1
                    continue

                # Prepare problem data
                problem_data = {
                    'title': data['title'],
                    'framework': framework,
                    'category': category,
                    'difficulty': data['difficulty'],
                    'description': data.get('description', ''),
                    'description_preview': data.get('description_preview', ''),
                    'context_code': data.get('context_code', ''),
                    'starter_code': data.get('starter_code', ''),
                    'target_area': data.get('target_area', ''),
                    'validation_spec': data.get('validation_spec', {}),
                    'hints': data.get('hints', []),
                    'learning_resources': data.get('learning_resources', []),
                    'tags': data.get('tags', []),
                    'estimated_time_minutes': data.get('estimated_time_minutes', 30),
                    'created_by': admin_user,
                }

                # Add scoring weights if provided
                if 'import_weight' in data:
                    problem_data['import_weight'] = data['import_weight']
                if 'structure_weight' in data:
                    problem_data['structure_weight'] = data['structure_weight']
                if 'behavior_weight' in data:
                    problem_data['behavior_weight'] = data['behavior_weight']
                if 'passing_score' in data:
                    problem_data['passing_score'] = data['passing_score']

                # Generate slug if not provided
                if 'slug' not in data:
                    problem_data['slug'] = slugify(data['title'])
                else:
                    problem_data['slug'] = data['slug']

                with transaction.atomic():
                    # Create or update problem
                    problem, created = Problem.objects.update_or_create(
                        problem_id=data['problem_id'],
                        defaults=problem_data
                    )

                    # Import patterns if provided
                    if 'patterns' in data and isinstance(data['patterns'], list):
                        for pattern_data in data['patterns']:
                            Pattern.objects.update_or_create(
                                problem=problem,
                                pattern_id=pattern_data.get('pattern_id', f"{data['problem_id']}-pattern-1"),
                                defaults={
                                    'name': pattern_data.get('name', 'Default Pattern'),
                                    'description': pattern_data.get('description', ''),
                                    'ast_representation': pattern_data.get('ast_representation', {}),
                                    'behavior_signature': pattern_data.get('behavior_signature', {}),
                                    'example_code': pattern_data.get('example_code', ''),
                                    'required_imports': pattern_data.get('required_imports', []),
                                    'required_structure': pattern_data.get('required_structure', {}),
                                    'forbidden_patterns': pattern_data.get('forbidden_patterns', []),
                                    'is_primary': pattern_data.get('is_primary', True),
                                    'confidence_threshold': pattern_data.get('confidence_threshold', 85.00),
                                }
                            )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {problem.problem_id} - {problem.title}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'○ Updated: {problem.problem_id} - {problem.title}')
                    )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ {json_file.name} - Error: {str(e)}')
                )

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('IMPORT SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total files processed: {len(json_files)}')
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'Updated: {updated_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        if skipped_count > 0:
            self.stdout.write(f'Skipped: {skipped_count}')
        
        total_problems = Problem.objects.count()
        total_patterns = Pattern.objects.count()
        self.stdout.write(f'\nDatabase totals:')
        self.stdout.write(f'  Problems: {total_problems}')
        self.stdout.write(f'  Patterns: {total_patterns}')
        self.stdout.write(self.style.SUCCESS('\n✓ Import completed!'))