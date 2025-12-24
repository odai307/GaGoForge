"""
Management command to validate problem JSON files.
Usage: python manage.py validate_problems [path]
"""

from django.core.management.base import BaseCommand
from pathlib import Path
import json
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Validate problem JSON files for correctness'

    def add_arguments(self, parser):
        parser.add_argument(
            'path',
            nargs='?',
            type=str,
            default='problems_data',
            help='Path to problems directory (default: problems_data)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed validation information',
        )

    def handle(self, *args, **options):
        path = Path(options['path'])
        verbose = options['verbose']

        if not path.exists():
            self.stdout.write(self.style.ERROR(f'Path does not exist: {path}'))
            return

        # Find all JSON files
        json_files = list(path.rglob('*.json'))
        
        # Exclude category_mappings.json
        json_files = [f for f in json_files if f.name != 'category_mappings.json']

        if not json_files:
            self.stdout.write(self.style.WARNING('No problem JSON files found'))
            return

        self.stdout.write(f'Found {len(json_files)} problem files to validate\n')

        valid_count = 0
        invalid_count = 0
        errors = []

        required_fields = [
            'problem_id', 'title', 'framework', 'category', 'difficulty',
            'description', 'validation_spec', 'hints'
        ]

        valid_difficulties = ['beginner', 'intermediate', 'pro', 'veteran']
        valid_frameworks = ['django', 'react', 'angular', 'express']

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                file_errors = []

                # Check required fields
                for field in required_fields:
                    if field not in data:
                        file_errors.append(f'Missing required field: {field}')

                # Validate framework
                if 'framework' in data and data['framework'] not in valid_frameworks:
                    file_errors.append(f'Invalid framework: {data["framework"]}')

                # Validate difficulty
                if 'difficulty' in data and data['difficulty'] not in valid_difficulties:
                    file_errors.append(f'Invalid difficulty: {data["difficulty"]}')

                # Validate validation_spec structure
                if 'validation_spec' in data:
                    if not isinstance(data['validation_spec'], dict):
                        file_errors.append('validation_spec must be a dictionary')

                # Validate hints
                if 'hints' in data:
                    if not isinstance(data['hints'], list):
                        file_errors.append('hints must be a list')

                # Validate patterns if present
                if 'patterns' in data:
                    if not isinstance(data['patterns'], list):
                        file_errors.append('patterns must be a list')

                if file_errors:
                    invalid_count += 1
                    errors.append({
                        'file': str(json_file.relative_to(path)),
                        'errors': file_errors
                    })
                    self.stdout.write(
                        self.style.ERROR(f'✗ {json_file.relative_to(path)}')
                    )
                    if verbose:
                        for error in file_errors:
                            self.stdout.write(f'  - {error}')
                else:
                    valid_count += 1
                    if verbose:
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ {json_file.relative_to(path)}')
                        )

            except json.JSONDecodeError as e:
                invalid_count += 1
                errors.append({
                    'file': str(json_file.relative_to(path)),
                    'errors': [f'Invalid JSON: {str(e)}']
                })
                self.stdout.write(
                    self.style.ERROR(f'✗ {json_file.relative_to(path)} - Invalid JSON')
                )
            except Exception as e:
                invalid_count += 1
                errors.append({
                    'file': str(json_file.relative_to(path)),
                    'errors': [f'Error: {str(e)}']
                })
                self.stdout.write(
                    self.style.ERROR(f'✗ {json_file.relative_to(path)} - {str(e)}')
                )

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('VALIDATION SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total files: {len(json_files)}')
        self.stdout.write(self.style.SUCCESS(f'Valid: {valid_count}'))
        if invalid_count > 0:
            self.stdout.write(self.style.ERROR(f'Invalid: {invalid_count}'))
            self.stdout.write('\nErrors found:')
            for error_info in errors:
                self.stdout.write(f'\n{error_info["file"]}:')
                for error in error_info['errors']:
                    self.stdout.write(f'  - {error}')
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ All problem files are valid!'))