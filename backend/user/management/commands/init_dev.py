import os

from django.core.management.base import BaseCommand
from django.core import management

from user.models import User, Term


class Command(BaseCommand):
    help = 'Create dev environments.'

    def handle(self, **options):
        management.call_command('makemigrations', 'user', 'group')
        management.call_command('migrate')
        os.environ.setdefault('DJANGO_SUPERUSER_PASSWORD', 'root')
        management.call_command('createsuperuser', '--no-input', username='root')
        Term.objects.create(name='term', content='test')
        User.objects.create_user(username="test_user", password="test_password",
                                 last_name='test_name')
