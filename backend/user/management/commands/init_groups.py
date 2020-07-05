from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = 'Create auth_groups.'

    def handle(self, **options):
        group, created = Group.objects.get_or_create(name='test')
        perm = Permission.objects.get(name='123')
        group.permissions.add(perm)
