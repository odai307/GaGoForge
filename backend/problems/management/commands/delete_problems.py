from django.core.management.base import BaseCommand
from problems.models import Problem

class Command(BaseCommand):
    help = 'Delete problems by problem_id or filter'

    def add_arguments(self, parser):
        parser.add_argument('--problem-id', type=str, help='Specific problem_id')
        parser.add_argument('--framework', type=str, help='Framework name')
        parser.add_argument('--difficulty', type=str, help='Difficulty level')
        parser.add_argument('--confirm', action='store_true', help='Confirm deletion')

    def handle(self, *args, **options):
        queryset = Problem.objects.all()
        
        if options['problem_id']:
            queryset = queryset.filter(problem_id=options['problem_id'])
        if options['framework']:
            queryset = queryset.filter(framework__name=options['framework'])
        if options['difficulty']:
            queryset = queryset.filter(difficulty=options['difficulty'])
        
        count = queryset.count()
        self.stdout.write(f"Found {count} problems to delete")
        
        if not options['confirm']:
            self.stdout.write(self.style.WARNING('Add --confirm to actually delete'))
            return
        
        queryset.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} problems'))