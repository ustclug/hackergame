from django.db import models


class Terms(models.Model):
    name = models.TextField()
    content = models.TextField()
    enabled = models.BooleanField()

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理用户条款'),
        ]


class Agreement(models.Model):
    user = models.IntegerField(db_index=True)
    terms = models.ForeignKey(Terms, models.CASCADE)

    class Meta:
        default_permissions = ()
