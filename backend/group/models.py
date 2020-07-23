from django.db import models
from django.db.models import Q

from user.models import User


class Group(models.Model):
    name = models.TextField()
    users = models.ManyToManyField(User)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="group_admin")
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
        ('accepted', 'the user is now in the group'),
        ('rejected', 'rejected'),
        ('pending', 'pending'),
        ('deleted', 'the user is deleted from the group')
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apply_message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')

    def save(self, *args, **kwargs):
        if self.status == 'accepted':
            self.group.users.add(self.user)
        if self.status == 'deleted':
            self.group.users.remove(self.user)
        super().save(*args, **kwargs)

    class Meta:
        default_permissions = []
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'group'],
                condition=Q(status='pending') | Q(status='accepted'),
                name='unique_application'
            )
        ]
