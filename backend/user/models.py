from django.db import models
from django.contrib.auth.models import AbstractUser


class Term(models.Model):
    """协议与条款"""
    name = models.CharField(max_length=100)
    content = models.TextField()
    enabled = models.BooleanField()


class User(AbstractUser):
    phone_number = models.CharField(max_length=14, null=True)
    token = models.TextField()
    terms = models.ManyToManyField(Term, through='Agreement')


class Agreement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    agreed = models.BooleanField()


class Group(models.Model):
    name = models.CharField(max_length=100)
    rule_has_phone_number = models.BooleanField()
    rule_has_email = models.BooleanField()
    rule_email_suffix = models.CharField(max_length=50)
    rule_has_name = models.BooleanField()
    rule_must_be_verified_by_admin = models.BooleanField()
    rule_apply_hint = models.TextField(verbose_name='给申请者的提示')
    verified = models.BooleanField(verbose_name='是否为认证过的组')
    verify_message = models.TextField()


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
