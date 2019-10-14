from datetime import timedelta
from random import randrange

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now


class Page(models.Model):
    title = models.TextField(default='Hackergame')
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True, default='Hackergame,CTF')
    content = models.TextField(blank=True, default='<h1>Hackergame</h1>',
                               help_text='会被放入 <code>div</code> 的 HTML')
    js = models.TextField(blank=True,
                          help_text='会被放入 <code>script</code> 的 JS')

    def __str__(self):
        return self.title

    @classmethod
    def get(cls):
        return cls.objects.get_or_create()[0]


class Account(models.Model):
    provider = models.TextField()
    identity = models.TextField()
    user = models.ForeignKey(get_user_model(), models.CASCADE, null=True)

    class Meta:
        unique_together = ('provider', 'identity')


class Code(models.Model):
    provider = models.TextField()
    identity = models.TextField()
    code = models.TextField(db_index=True)
    expiration = models.DateTimeField()

    class TooMany(Exception):
        pass

    @classmethod
    def generate(cls, provider, identity, duration=timedelta(minutes=10),
                 limit=3):
        if cls.objects.filter(
            provider=provider,
            identity=identity,
            expiration__gt=now(),
        ).count() >= limit:
            raise cls.TooMany
        return cls.objects.create(
            provider=provider,
            identity=identity,
            code=str(randrange(100000, 1000000)),
            expiration=now() + duration,
        ).code

    @classmethod
    def authenticate(cls, provider, identity, code):
        try:
            cls.objects.get(
                provider=provider,
                identity=identity,
                code=code,
                expiration__gt=now(),
            ).delete()
            return True
        except cls.DoesNotExist:
            return False
