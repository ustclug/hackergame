import random

from django.db import models


def gen_hash():
    return f'{random.randrange(10000):04d}'


class User(models.Model):
    user = models.IntegerField(unique=True)
    hash = models.TextField(default=gen_hash)
    group = models.TextField()
    nickname = models.TextField(null=True)
    name = models.TextField(null=True)
    sno = models.TextField(null=True)
    tel = models.TextField(null=True)
    email = models.TextField(null=True)
    token = models.TextField()

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理个人信息'),
        ]
