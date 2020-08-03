from django.db import models
from django.db.models import Q

from user.models import User


class Group(models.Model):
    """组, 区分参赛者所属的组织"""
    name = models.TextField()
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                              blank=True, related_name="group_admin")
    rule_has_phone_number = models.BooleanField()
    rule_has_email = models.BooleanField()
    rule_email_suffix = models.CharField(max_length=50, null=True, blank=True)
    rule_has_name = models.BooleanField()
    rule_must_be_verified_by_admin = models.BooleanField()
    apply_hint = models.TextField(verbose_name='给申请者的提示', blank=True)
    verified = models.BooleanField(verbose_name='是否为认证过的组', default=False)
    verify_message = models.TextField(blank=True)

    def __str__(self):
        return f'{self.id}:{self.name}'

    @property
    def users(self):
        applications = Application.objects.filter(group=self, status='accepted')
        return list(map(lambda appl: appl.user, applications))

    def save(self, *args, **kwargs):
        flg = 0
        if not self.pk:
            flg = 1
        super().save(*args, **kwargs)
        # 为创建组的用户添加 Application
        if flg:
            Application.objects.create(group=self, user=self.admin, status='accepted')

    class Meta:
        default_permissions = []


class Application(models.Model):
    """加入某个组的申请"""
    STATUS = (
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
        ('pending', 'pending'),
        ('deleted', 'deleted'),
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apply_message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')

    def __str__(self):
        return f'{self.id}:{self.group.name}:{self.user}'

    def save(self, *args, **kwargs):
        from submission.models import Submission, SubChallengeFirstBlood, ChallengeFirstBlood, update_firstblood

        super().save(*args, **kwargs)

        if self.status == 'accepted':
            # 用户加入组后更新该组的一血榜
            for submission in Submission.objects.filter(user=self.user):
                values = {
                    'sub_challenge': submission.sub_challenge_clear,
                    'group': self.group,
                }
                update_firstblood(SubChallengeFirstBlood, submission, values)
                if submission.challenge_clear:
                    values = {
                        'challenge': submission.challenge,
                        'group': self.group,
                    }
                    update_firstblood(ChallengeFirstBlood, submission, values)


    class Meta:
        default_permissions = []
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'group'],
                condition=Q(status='pending') | Q(status='accepted'),
                name='unique_application'
            )
        ]
