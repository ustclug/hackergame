from django.db import models
from django.contrib.auth.models import AbstractUser

from user.utils import generate_uuid_and_token
from challenge.utils import eval_token_expression


class TermManager(models.Manager):
    def enabled_term(self):
        return self.get_queryset().filter(enabled=True)


class Term(models.Model):
    """协议与条款"""
    name = models.CharField(max_length=100)
    content = models.TextField()
    date_modified = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)

    objects = TermManager()

    def save(self, *args, **kwargs):
        # 任何条款变化后都需要用户重新同意
        # FIXME: 清除登录状态
        for user in User.objects.all():
            user.term_agreed = False
            user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id}:{self.name}'

    class Meta:
        default_permissions = []


class User(AbstractUser):
    phone_number = models.CharField(max_length=14, blank=True)
    token = models.TextField(blank=True)
    term_agreed = models.BooleanField(default=False)
    uuid = models.UUIDField(editable=False)

    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        from challenge.models import SubChallenge, ExprFlag  # to avoid circuit import

        created = 0
        if not self.pk:
            created = 1
            self.uuid, self.token = generate_uuid_and_token()

        super().save(*args, **kwargs)
        # 创建完成后更新 ExprFlag 表
        if created:
            for sub_challenge in SubChallenge.objects.filter(flag_type='expr'):
                flag = eval_token_expression(sub_challenge.flag, self.token)
                ExprFlag.objects.create(user=self, sub_challenge=sub_challenge, flag=flag)

    class Meta:
        default_permissions = []
        db_table = 'user'
