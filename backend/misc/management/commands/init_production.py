import os
from datetime import datetime

from django.core.management.base import BaseCommand

from user.models import User
from contest.models import Stage


class Command(BaseCommand):
    help = 'Create production environments.'

    def handle(self, **options):
        if Stage.objects.count() != 0:
            print("The database has already been initialized.")
            return

        start_time = datetime.fromisoformat(os.environ.get('START_TIME', '2020-01-01T08:00+08:00'))
        end_time = datetime.fromisoformat(os.environ.get('END_TIME', '2030-01-01T08:00+08:00'))
        practice_start_time = datetime.fromisoformat(os.environ.get('PRACTICE_START_TIME', '2040-01-01T08:00+08:00'))
        Stage.objects.create(start_time=start_time, end_time=end_time, practice_start_time=practice_start_time)

        User.objects.create_superuser(username='root', password=os.environ.get('ROOT_PASSWD', 'root'))
