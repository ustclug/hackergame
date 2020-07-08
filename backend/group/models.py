from django.db import models
from user.models import User


class Group(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)
    rule_has_phone_number = models.BooleanField()
    rule_has_email = models.BooleanField()
    rule_email_suffix = models.CharField(max_length=50, null=True)
    rule_has_name = models.BooleanField()
    rule_must_be_verified_by_admin = models.BooleanField()
    rule_apply_hint = models.TextField(verbose_name='给申请者的提示', null=True)
    verified = models.BooleanField(verbose_name='是否为认证过的组')
    verify_message = models.TextField(null=True)


class Application(models.Model):
    """加入某个组的申请"""
    STATUS = (
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
        ('pending', 'pending')
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apply_message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS, default='pending')

