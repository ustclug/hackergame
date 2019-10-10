from django.db import models


class User(models.Model):
    user = models.IntegerField(unique=True)
    group = models.TextField()
    nickname = models.TextField(null=True)
    name = models.TextField(null=True)
    sno = models.TextField(null=True)
    tel = models.TextField(null=True)
    email = models.TextField(null=True)
    gender = models.TextField(null=True)
    qq = models.TextField(null=True)
    token = models.TextField()

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理个人信息'),
        ]
