from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, UserManager

from user.utils import generate_uuid_and_token


class TermManager(models.Manager):
    def enabled_term(self):
        return self.get_queryset().get(enabled=True)


# TODO: 只允许一条启用的条款 (admin page)
class Term(models.Model):
    """协议与条款"""
    name = models.CharField(max_length=100)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)

    objects = TermManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            for user in User.objects.all():
                user.term_agreed = False
                user.save()
        super().save(*args, **kwargs)

    class Meta:
        default_permissions = []
        constraints = [
            models.UniqueConstraint(
                fields=['enabled'],
                condition=Q(enabled=True),
                name='only_one_enabled_term'
            )
        ]


class MyUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        uid, sig = generate_uuid_and_token()
        user = super().create_user(username, email, password, uuid=uid, token=sig, **extra_fields)
        return user


class User(AbstractUser):
    phone_number = models.CharField(max_length=14, blank=True)
    token = models.TextField(blank=True)
    term_agreed = models.BooleanField(default=False)
    uuid = models.UUIDField(editable=False)

    objects = MyUserManager()

    REQUIRED_FIELDS = []

    class Meta:
        default_permissions = []
        permissions = [
            ('update_profile', 'can update his own profile')
        ]
