from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = '用配置文件更新数据库'

    def handle(self, *args, **options):
        site = Site.objects.get_current()
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=settings.GOOGLE_APP_ID,
            secret=settings.GOOGLE_APP_SECRET,
            key='',
        )
        app.sites.add(site)
        app = SocialApp.objects.create(
            provider='microsoft',
            name='Microsoft',
            client_id=settings.MICROSOFT_APP_ID,
            secret=settings.MICROSOFT_APP_SECRET,
            key=''
        )
        app.sites.add(site)
