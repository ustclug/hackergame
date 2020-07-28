from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from user.models import User


class Challenge(models.Model):
    index = models.IntegerField(db_index=True, verbose_name='顺序')
    name = models.TextField(unique=True)
    category = models.TextField()
    detail = models.TextField(
        verbose_name='题目描述',
        help_text='会被放入 div 的 HTML，其中的 {token} 会被替换为 URL encode 后的用户 token'
    )
    prompt = models.TextField(blank=True, verbose_name='提示')

    def __str__(self):
        return self.name

    @property
    def enabled(self):
        for s in SubChallenge.objects.filter(challenge=self):
            if s.enabled is True:
                return True
        return False

    class Meta:
        default_permissions = ()
        permissions = [
            ('full', '管理题目'),
            ('view', '查看题目'),
        ]
        ordering = ['index']


class SubChallenge(models.Model):
    """子题"""
    FLAG_TYPE = (
        ('expr', 'a Python expression'),
        ('text', 'plain text'),
    )
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='sub_challenge')
    name = models.TextField(blank=True, help_text="若只有一个子题则不填")
    score = models.SmallIntegerField()
    enabled = models.BooleanField(
        help_text="""
        设为无效的题目不会被看到，也不会产生任何分数。 将题目改为无效时，它产生的分数会被移除，但并不删除此前的提交记录。
        将题目改为有效时，此前的提交记录会重新产生分数。
        <em>注意：在比赛开始后修改此项信息会重算排行榜，产生较大开销。</em>
        """
    )
    flag_type = models.CharField(max_length=5, choices=FLAG_TYPE)
    flag = models.TextField(
        help_text="""
        若 flag 类型为表达式, 则填写一个 Python 表达式，其计算结果为 flag。 示例：
        'flag{' + md5('secret' + token)[:16] + '}'。 可以使用的变量及函数： token, base64, md5, sha1, sha224,
        sha256, sha384, sha512, sha3_224, sha3_256, sha3_384, sha3_512
        """
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        from challenge.utils import eval_token_expression
        if self.flag_type == 'expr':
            # 每次保存更新 ExprFlag 表
            # TODO: 创建用户也要更新 ExprFlag 表
            users = User.objects.all()
            # 若 flag 表达式无变化则跳过更新
            try:
                obj = ExprFlag.objects.get(user=users[0], sub_challenge=self)
                flag = eval_token_expression(self.flag, users[0].token)
                if obj.flag == flag:
                    return
            except ObjectDoesNotExist:
                pass

            for user in users:
                flag = eval_token_expression(self.flag, user.token)
                obj = ExprFlag(user=user, sub_challenge=self, flag=flag)
                obj.save()


class ExprFlag(models.Model):
    """表达式 Flag 的实际值"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub_challenge = models.ForeignKey(SubChallenge, on_delete=models.CASCADE)
    flag = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'sub_challenge'], name='unique_flag')
        ]
