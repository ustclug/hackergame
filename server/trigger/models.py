from django.db import models


class Trigger(models.Model):
    time = models.DateTimeField()
    can_view_challenges = models.BooleanField()
    can_try = models.BooleanField()
    can_submit = models.BooleanField()
    can_update_profile = models.BooleanField()
    note = models.TextField(null=True)

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理定时器'),
        ]
