from datetime import timedelta
from random import randrange

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

from . import site

User = get_user_model()

backend_choices = [(backend.id, backend.name) for backend in site.backends]


class Device(models.Model):
    backend = models.TextField(choices=backend_choices, db_index=True)
    identity = models.TextField()
    user = models.ForeignKey(User, models.CASCADE, null=True)

    def __str__(self):
        return f'{self.backend}: {self.identity}'

    class Meta:
        unique_together = ('backend', 'identity')


class Token(models.Model):
    device = models.ForeignKey(Device, models.CASCADE)
    token = models.TextField()
    expiration = models.DateTimeField(db_index=True)

    def __str__(self):
        return f'{self.device}'

    class TooMany(Exception):
        pass

    @classmethod
    def generate(cls, device, period=timedelta(minutes=10), limit=3):
        if cls.objects.filter(device=device, expiration__gt=now()).count() >= limit:
            raise cls.TooMany
        token = str(randrange(100000, 1000000))
        expiration = now() + period
        return cls.objects.create(device=device, token=token, expiration=expiration)

    @classmethod
    def authenticate(cls, device, token):
        try:
            token = cls.objects.get(device=device, token=token, expiration__gt=now())
            token.delete()
            return token
        except cls.DoesNotExist:
            return None
