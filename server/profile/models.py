from django.contrib.auth import get_user_model
from django.db import models

from server.ctf.models import CtfInfo

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, models.CASCADE, primary_key=True)
    name = models.TextField(blank=True)
    sno = models.TextField(blank=True)
    tel = models.TextField(blank=True)
    email = models.TextField(blank=True)

    def __str__(self):
        return str(self.user)

    @property
    def ok(self):
        if CtfInfo(self.user).first_backend.id != 'ustc':
            return True
        return all((self.name, self.sno, self.tel, self.email))

    def _update(instance, **kwargs):
        _ = kwargs
        try:
            instance.profile
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)

    models.signals.post_save.connect(_update, sender='auth.User')
