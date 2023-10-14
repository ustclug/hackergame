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

    def __str__(self):
        return f'User {self.user.pk if self.user else "(null)"} ({self.provider}:{self.identity})'

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


# 记录特殊登录方式（例如 USTC CAS）的用户，其登录方式返回的「可靠」信息
class AccountLog(models.Model):
    account = models.ForeignKey(Account, models.CASCADE, db_index=True)
    contents = models.TextField()
    content_type = models.CharField(max_length=32, default='学号')

    def __str__(self):
        return f"Account {self.account.pk} ({self.content_type} {self.contents})"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['account', 'content_type'],
                                    name='unique_account_log_for_each_type'),
        ]


# 记录需要在首次登录后显示换组页面并且已经换组的用户
# 目前只有 USTC 有这个需求
class SpecialProfileUsedRecord(models.Model):
    user = models.OneToOneField(get_user_model(), models.CASCADE, primary_key=True)

    def __str__(self) -> str:
        return f"A used record of User id {self.user.pk}"


class Qa(models.Model):
    content = models.TextField(blank=True, default='<h1>问与答</h1>',
                               help_text='会被放入 <code>div</code> 的 HTML')

    @classmethod
    def get(cls):
        return cls.objects.get_or_create()[0]


class Credits(models.Model):
    content = models.TextField(blank=True,
                               help_text='会被放入 <code>div</code> 的 HTML')
    js = models.TextField(blank=True,
                          help_text='会被放入 <code>script</code> 的 JS')

    @classmethod
    def get(cls):
        return cls.objects.get_or_create()[0]
