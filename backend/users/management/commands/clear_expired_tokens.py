# users/management/commands/clear_expired_tokens.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

class Command(BaseCommand):
    help = 'Clear expired tokens from blacklist'

    def handle(self, *args, **kwargs):
        # Delete expired tokens
        OutstandingToken.objects.filter(expires_at__lte=timezone.now()).delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleared expired tokens'))