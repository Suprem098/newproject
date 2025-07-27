from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'List all users and their profile roles'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            try:
                role = user.profile.role
            except Exception as e:
                role = f'Error: {str(e)}'
            self.stdout.write(f'User: {user.username}, Role: {role}')
