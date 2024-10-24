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
    website = models.TextField(null=True)
    school = models.TextField(null=True)
    grade = models.TextField(null=True)
    major = models.TextField(null=True)
    campus = models.TextField(null=True)
    aff = models.TextField(null=True)
    token = models.TextField()
    suspicious = models.BooleanField(default=False)
    suspicious_reason = models.TextField(null=True)
    suspicious_ddl = models.DateTimeField(null=True)

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理个人信息'),
            ('view', '查看个人信息'),
            ('view_ustc', '查看中国科学技术大学个人信息'),
            ('view_zju', '查看浙江大学个人信息'),
            ('view_jlu', '查看吉林大学个人信息'),
            ('view_nuaa', '查看南京航空航天大学个人信息'),
            ('view_neu', '查看东北大学个人信息'),
            ('view_sysu', '查看中山大学个人信息'),
            ('view_xidian', '查看西安电子科技大学个人信息'),
            ('view_hit', '查看哈尔滨工业大学个人信息'),
            ('view_fdu', '查看复旦大学个人信息'),
            ('view_tongji', '查看同济大学个人信息'),
            ('view_gdou', '查看广东海洋大学个人信息'),
            ('view_sustech', '查看南方科技大学个人信息'),
            ('view_xmut', '查看厦门理工学院个人信息'),
            ('view_shu', '查看上海大学个人信息'),
            ('view_nyist', '查看南阳理工学院个人信息'),
            ('view_sjtu', '查看上海交通大学个人信息'),
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
    website = models.TextField(null=True)
    school = models.TextField(null=True)
    grade = models.TextField(null=True)
    major = models.TextField(null=True)
    campus = models.TextField(null=True)
    aff = models.TextField(null=True)
    token = models.TextField()
    suspicious = models.BooleanField(default=False)
    suspicious_reason = models.TextField(null=True)
    suspicious_ddl = models.DateTimeField(null=True)

    class Meta:
        default_permissions = ()
