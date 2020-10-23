from django.db import models


class User(models.Model):
    user = models.IntegerField(unique=True)
    group = models.TextField()
    nickname = models.TextField(null=True)
    name = models.TextField(null=True)
    sno = models.TextField(null=True)
    tel = models.TextField(null=True)
    email = models.TextField(null=True)
    gender = models.TextField(null=True)
    qq = models.TextField(null=True)
    school = models.TextField(null=True)
    grade = models.TextField(null=True)
    aff = models.TextField(null=True)
    token = models.TextField()

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理个人信息'),
            ('view_ustc', '查看中国科学技术大学个人信息'),
            ('view_zju', '查看浙江大学个人信息'),
            ('view_hit', '查看哈尔滨工业大学个人信息'),
            ('view_xjtu', '查看西安交通大学个人信息'),
            ('view_cqu', '查看重庆大学个人信息'),
            ('view_bupt', '查看北京邮电大学个人信息'),
            ('view_jlu', '查看吉林大学个人信息'),
            ('view_neu', '查看东北大学个人信息'),
            ('view_nuaa', '查看南京航空航天大学个人信息'),
        ]


class UserLog(models.Model):
    context_user = models.IntegerField(null=True)
    context_time = models.DateTimeField()
    context_elevated = models.BooleanField()
    user = models.IntegerField()
    group = models.TextField()
    nickname = models.TextField(null=True)
    name = models.TextField(null=True)
    sno = models.TextField(null=True)
    tel = models.TextField(null=True)
    email = models.TextField(null=True)
    gender = models.TextField(null=True)
    qq = models.TextField(null=True)
    school = models.TextField(null=True)
    grade = models.TextField(null=True)
    aff = models.TextField(null=True)
    token = models.TextField()

    class Meta:
        default_permissions = ()
