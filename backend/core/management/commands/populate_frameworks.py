"""
Management command to populate Framework and Category models.
Usage: python manage.py populate_frameworks
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Framework, Category
import json
from pathlib import Path
from django.conf import settings 


class Command(BaseCommand):
    help = 'Populate Framework and Category models with initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing frameworks and categories before populating',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Deleting existing frameworks and categories...'))
            Category.objects.all().delete()
            Framework.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Deleted successfully'))

        # Load category mappings
        #base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        #mappings_file = base_dir / 'problems_data' / 'category_mappings.json'
        mappings_file = settings.BASE_DIR / 'problems_data' / 'category_mappings.json'

        if not mappings_file.exists():
            self.stdout.write(self.style.ERROR(f'Missing file: {mappings_file}'))
            return
        
        with open(mappings_file, 'r') as f:
            category_mappings = json.load(f)

        with transaction.atomic():
            # Create Frameworks
            frameworks_data = [
                {
                    'name': 'django',
                    'display_name': 'Django',
                    'description': 'The web framework for perfectionists with deadlines. A high-level Python web framework that encourages rapid development and clean, pragmatic design.',
                    'version': '4.2',
                    'documentation_url': 'https://docs.djangoproject.com/',
                    'icon_url': 'https://static.djangoproject.com/img/icon-touch.e4872c4da341.png',
                    'is_active': True,
                    'order': 1
                },
                {
                    'name': 'react',
                    'display_name': 'React',
                    'description': 'A JavaScript library for building user interfaces. React makes it painless to create interactive UIs with a component-based architecture.',
                    'version': '18',
                    'documentation_url': 'https://react.dev/',
                    'icon_url': 'https://react.dev/favicon.ico',
                    'is_active': True,
                    'order': 2
                },
                {
                    'name': 'angular',
                    'display_name': 'Angular',
                    'description': 'A TypeScript-based web application framework. Build scalable, enterprise-grade applications with a complete development platform.',
                    'version': '17',
                    'documentation_url': 'https://angular.io/docs',
                    'icon_url': 'https://angular.io/assets/images/logos/angular/angular.png',
                    'is_active': True,
                    'order': 3
                },
                {
                    'name': 'express',
                    'display_name': 'Express',
                    'description': 'Fast, unopinionated, minimalist web framework for Node.js. Express provides a robust set of features for web and mobile applications.',
                    'version': '4',
                    'documentation_url': 'https://expressjs.com/',
                    'icon_url': 'https://expressjs.com/images/favicon.png',
                    'is_active': True,
                    'order': 4
                }
            ]

            created_frameworks = {}
            for fw_data in frameworks_data:
                framework, created = Framework.objects.get_or_create(
                    name=fw_data['name'],
                    defaults=fw_data
                )
                created_frameworks[fw_data['name']] = framework
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created framework: {framework.display_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'○ Framework already exists: {framework.display_name}')
                    )

            # Create Categories for each framework
            categories_created = 0
            categories_existed = 0

            for framework_name, categories in category_mappings.items():
                framework = created_frameworks[framework_name]
                
                for order, (category_name, category_display) in enumerate(categories.items(), start=1):
                    category, created = Category.objects.get_or_create(
                        framework=framework,
                        name=category_name,
                        defaults={
                            'display_name': category_display,
                            'description': f'{category_display} challenges for {framework.display_name}',
                            'order': order,
                            'is_active': True
                        }
                    )
                    
                    if created:
                        categories_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ Created category: {framework.display_name} - {category.display_name}')
                        )
                    else:
                        categories_existed += 1

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Frameworks: {Framework.objects.count()} total')
        self.stdout.write(f'Categories: {Category.objects.count()} total ({categories_created} created, {categories_existed} existed)')
        self.stdout.write(self.style.SUCCESS('\n✓ Database populated successfully!'))