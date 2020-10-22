from django.db import models


class Submission(models.Model):
    user = models.IntegerField(db_index=True)
    group = models.TextField(db_index=True)
    challenge = models.IntegerField(db_index=True)
    text = models.TextField()
    time = models.DateTimeField()

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理提交记录'),
            ('view', '查看提交记录'),
        ]


class ChallengeClear(models.Model):
    user = models.IntegerField(db_index=True)
    group = models.TextField(db_index=True)
    challenge = models.IntegerField(db_index=True)
    time = models.DateTimeField(db_index=True)

    class Meta:
        default_permissions = ()
        unique_together = ('user', 'challenge')


class FlagClear(models.Model):
    submission = models.ForeignKey(Submission, models.CASCADE)
    user = models.IntegerField(db_index=True)
    group = models.TextField(db_index=True)
    challenge = models.IntegerField(db_index=True)
    flag = models.IntegerField()
    time = models.DateTimeField(db_index=True)

    class Meta:
        default_permissions = ()
        unique_together = ('user', 'challenge', 'flag')


class FlagViolation(models.Model):
    submission = models.ForeignKey(Submission, models.CASCADE)
    violation_flag = models.IntegerField()
    violation_user = models.IntegerField()

    class Meta:
        default_permissions = ()


class ChallengeFirst(models.Model):
    challenge = models.IntegerField()
    group = models.TextField(db_index=True)
    user = models.IntegerField()
    time = models.DateTimeField()

    class Meta:
        default_permissions = ()
        unique_together = ('challenge', 'group')


class FlagFirst(models.Model):
    challenge = models.IntegerField()
    flag = models.IntegerField()
    group = models.TextField(db_index=True)
    user = models.IntegerField()
    time = models.DateTimeField()

    class Meta:
        default_permissions = ()
        unique_together = ('challenge', 'flag', 'group')


class Score(models.Model):
    user = models.IntegerField(db_index=True)
    group = models.TextField()
    category = models.TextField(db_index=True)
    score = models.IntegerField()
    time = models.DateTimeField()

    class Meta:
        default_permissions = ()
        unique_together = ('user', 'category')
