"""
Management command to export problems to JSON files.
Usage: python manage.py export_problems [output_path]
"""

from django.core.management.base import BaseCommand
from pathlib import Path
import json
from problems.models import Problem, Pattern


class Command(BaseCommand):
    help = 'Export problems from database to JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            'output_path',
            nargs='?',
            type=str,
            default='problems_export',
            help='Output directory for exported problems (default: problems_export)'
        )
        parser.add_argument(
            '--problem-id',
            type=str,
            help='Export specific problem by problem_id',
        )
        parser.add_argument(
            '--framework',
            type=str,
            help='Export problems for specific framework',
        )

    def handle(self, *args, **options):
        output_path = Path(options['output_path'])
        problem_id = options.get('problem_id')
        framework = options.get('framework')

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        # Filter problems
        problems = Problem.objects.all()
        
        if problem_id:
            problems = problems.filter(problem_id=problem_id)
        
        if framework:
            problems = problems.filter(framework__name=framework)

        if not problems.exists():
            self.stdout.write(self.style.WARNING('No problems found to export'))
            return

        self.stdout.write(f'Exporting {problems.count()} problems...\n')

        exported_count = 0

        for problem in problems:
            # Create directory structure
            problem_dir = output_path / problem.framework.name / problem.category.name / problem.difficulty
            problem_dir.mkdir(parents=True, exist_ok=True)

            # Prepare problem data
            problem_data = {
                'problem_id': problem.problem_id,
                'title': problem.title,
                'slug': problem.slug,
                'framework': problem.framework.name,
                'category': problem.category.name,
                'difficulty': problem.difficulty,
                'description': problem.description,
                'description_preview': problem.description_preview,
                'context_code': problem.context_code,
                'starter_code': problem.starter_code,
                'target_area': problem.target_area,
                'validation_spec': problem.validation_spec,
                'import_weight': float(problem.import_weight),
                'structure_weight': float(problem.structure_weight),
                'behavior_weight': float(problem.behavior_weight),
                'passing_score': float(problem.passing_score),
                'hints': problem.hints,
                'learning_resources': problem.learning_resources,
                'tags': problem.tags,
                'estimated_time_minutes': problem.estimated_time_minutes,
            }

            # Add patterns
            patterns = problem.patterns.all()
            if patterns.exists():
                problem_data['patterns'] = []
                for pattern in patterns:
                    pattern_data = {
                        'pattern_id': pattern.pattern_id,
                        'name': pattern.name,
                        'description': pattern.description,
                        'ast_representation': pattern.ast_representation,
                        'behavior_signature': pattern.behavior_signature,
                        'example_code': pattern.example_code,
                        'required_imports': pattern.required_imports,
                        'required_structure': pattern.required_structure,
                        'forbidden_patterns': pattern.forbidden_patterns,
                        'is_primary': pattern.is_primary,
                        'confidence_threshold': float(pattern.confidence_threshold),
                    }
                    problem_data['patterns'].append(pattern_data)

            # Write to file
            file_path = problem_dir / f'{problem.problem_id}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(problem_data, f, indent=2, ensure_ascii=False)

            exported_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'✓ Exported: {problem.problem_id} -> {file_path.relative_to(output_path)}')
            )

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('EXPORT SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Exported {exported_count} problems to: {output_path}')
        self.stdout.write(self.style.SUCCESS('\n✓ Export completed!'))