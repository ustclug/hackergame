from django.db import models


class Challenge(models.Model):
    name = models.TextField(unique=True)
    category = models.TextField()
    enabled = models.BooleanField()
    detail = models.TextField()
    url_orig = models.TextField(null=True)
    prompt = models.TextField(null=True)
    index = models.IntegerField(db_index=True)
    flags = models.TextField()
    check_url_clicked = models.BooleanField(default=False)
    use_web_docker_manager = models.BooleanField(default=False)

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理题目'),
            ('view', '查看题目'),
        ]
        ordering = ['index']


class User(models.Model):
    user = models.IntegerField(unique=True)

    class Meta:
        default_permissions = ()


class Expr(models.Model):
    challenge = models.ForeignKey(Challenge, models.CASCADE)
    flag_index = models.IntegerField()
    expr = models.TextField(db_index=True)

    class Meta:
        default_permissions = ()
        unique_together = ('challenge', 'flag_index')


class ExprFlag(models.Model):
    expr = models.TextField(db_index=True)
    user = models.IntegerField(db_index=True)
    flag = models.TextField(db_index=True)

    class Meta:
        default_permissions = ()
        unique_together = ('expr', 'user')


class ChallengeURLRecord(models.Model):
    challenge = models.ForeignKey(Challenge, models.CASCADE)
    user = models.IntegerField(db_index=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()
        unique_together = ('challenge', 'user')
