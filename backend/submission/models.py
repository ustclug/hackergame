from django.db import models
from django.db.models import Q

from user.models import User
from group.models import Group
from challenge.models import Challenge, SubChallenge


class Submission(models.Model):
    """每一次提交"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    flag = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    challenge_clear = models.BooleanField(default=False)
    sub_challenge_clear = models.ForeignKey(SubChallenge, on_delete=models.CASCADE, null=True)
    violation_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='violation_submission',
                                       null=True, verbose_name="和该用户的某一 flag 重复")

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理提交记录'),
            ('view', '查看提交记录'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'challenge_clear'],
                condition=Q(challenge_clear=True),
                name='unique_challenge_clear'
            ),
            models.UniqueConstraint(
                fields=['user', 'sub_challenge_clear'],
                name='unique_sub_challenge_clear'
            ),
        ]


class ChallengeFirstBlood(models.Model):
    """题目一血榜单"""
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)  # 为 null 时即为总榜单
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=['challenge', 'group'],
                name='unique_challenge_first'
            ),
        ]


class SubChallengeFirstBlood(models.Model):
    """子题一血榜单"""
    sub_challenge = models.ForeignKey(SubChallenge, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=['sub_challenge', 'group'],
                name='unique_sub_challenge_first'
            ),
        ]


class Scoreboard(models.Model):
    """分数榜单"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.TextField(blank=True)  # 为空的话为总分
    score = models.IntegerField()
    time = models.DateTimeField(verbose_name='最后一次更新榜单的时间')

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'category'],
                name='unique_score_category'
            ),
        ]
