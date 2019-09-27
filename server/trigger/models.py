from django.db import models


class Trigger(models.Model):
    time = models.DateTimeField()
    state = models.BooleanField()
    note = models.TextField(null=True)

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理定时器'),
        ]
