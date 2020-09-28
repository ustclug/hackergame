import logging

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from dirtyfields import DirtyFieldsMixin

from user.models import User


logger = logging.getLogger(__name__)


class Group(models.Model):
    """组, 区分参赛者所属的组织"""
    name = models.TextField()
    admin = models.ManyToManyField(User, related_name='admin_group')
    rule_has_phone_number = models.BooleanField()
    rule_has_email = models.BooleanField()
    rule_email_suffix = models.CharField(max_length=50, blank=True)
    rule_has_name = models.BooleanField()
    rule_must_be_verified_by_admin = models.BooleanField()
    apply_hint = models.TextField(blank=True, help_text='给申请者的提示')
    verified = models.BooleanField(default=False, help_text='是否为认证过的组')
    verify_message = models.TextField(blank=True)

    def __str__(self):
        return f'{self.id}:{self.name}'

    @property
    def users(self):
        applications = Application.users.filter(group=self)
        return list(map(lambda appl: appl.user, applications))

    class Meta:
        default_permissions = []


@receiver(m2m_changed, sender=Group.admin.through)
def admin_changed(instance, action, pk_set, **kwargs):
    # 为组管理员添加 Application
    if action == 'post_add':
        for user_pk in pk_set:
            Application.objects.create(group=instance, user_id=user_pk, status='accepted')


class ApplicationUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='accepted')


class Application(models.Model, DirtyFieldsMixin):
    """加入某个组的申请, 同时表示了一个组的成员"""
    STATUS = (
        ('accepted', 'accepted'),
        ('pending', 'pending'),
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apply_message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')

    users = ApplicationUserManager()  # The default manager
    objects = models.Manager()

    # def __str__(self):
    #     return f'{self.id}:{self.group.name}:{self.user}'  # FIXME: 每个 Application 都会有一个 SQL query

    def save(self, *args, **kwargs):
        from submission.models import Submission

        if self.pk and self.get_dirty_fields().get('status') == 'accepted':
            raise ValidationError("状态无法从 accepted 改为 pending.")

        super().save(*args, **kwargs)

        # 用户加入组后
        if self.status == 'accepted':
            # 用该用户的提交更新该组的一血榜
            for submission in Submission.objects.filter(user=self.user, sub_challenge_clear__isnull=False):
                submission.update_first_blood(self.group)

    class Meta:
        default_permissions = []
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'group'],
                condition=Q(status='pending') | Q(status='accepted'),
                name='unique_application'
            )
        ]


@receiver(post_delete, sender=Application)
def post_delete_application(sender, instance, **kwargs):
    """QuerySet 的 delete() 或级联删除将不会触发模型的 delete(), 故使用信号."""
    from submission.models import Submission, SubChallengeFirstBlood, ChallengeFirstBlood

    # 退出组后更新一血榜
    user_sub_first = SubChallengeFirstBlood.objects.filter(group=instance.group, user=instance.user)
    sub_challenges_null = list(user_sub_first.values_list('sub_challenge', flat=True))
    user_sub_first.delete()

    ChallengeFirstBlood.objects.filter(group=instance.group, user=instance.user).delete()

    for sub_challenge in sub_challenges_null:
        try:
            first = Submission.objects.filter(
                user__in=instance.group.users,
                sub_challenge_clear=sub_challenge,
                sub_challenge_clear__enabled=True
            ).earliest('created_time')
            first.update_first_blood(instance.group)
        except Submission.DoesNotExist:
            pass
