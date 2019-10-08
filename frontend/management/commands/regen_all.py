from django.core.management.base import BaseCommand

from server.challenge.interface import Challenge
from server.submission.interface import Submission
from server.context import Context


class Command(BaseCommand):
    help = '重算所有数据库缓存'

    def handle(self, *args, **options):
        context = Context(elevated=True)
        Challenge.regen_all(context)
        Submission.regen_all(context)
