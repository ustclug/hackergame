from django.db import models


class Announcement(models.Model):
    content = models.TextField()
    time = models.DateTimeField()

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理公告'),
        ]
        ordering = ('-time',)
