from django.db import models
from dirtyfields import DirtyFieldsMixin

from user.models import User
from challenge.utils import eval_token_expression

from typing import Union


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
        default_permissions = []
        ordering = ['index']


class SubChallenge(models.Model, DirtyFieldsMixin):
    """子题"""
    FLAG_TYPE = (
        ('expr', 'a Python expression'),
        ('text', 'plain text'),
    )
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='sub_challenge')
    name = models.TextField(blank=True, help_text="若只有一个子题则可不填")
    score = models.SmallIntegerField()
    enabled = models.BooleanField(
        help_text="""
        设为无效的题目不会被看到，也不会产生任何分数。 将题目改为无效时，它产生的分数会被移除，但并不删除此前的提交记录。
        将题目改为有效时，此前的提交记录会重新产生分数。
        <em>注意：在比赛开始后修改此项信息会重算排行榜，产生较大开销。</em>
        """,
        default=True,
    )
    flag_type = models.CharField(max_length=5, choices=FLAG_TYPE)
    flag = models.TextField(
        help_text="""
        若 flag 类型为表达式, 则填写一个 Python 表达式，其计算结果为 flag。 示例：
        'flag{' + md5('secret' + token)[:16] + '}'。 可以使用的变量及函数： token, base64, md5, sha1, sha224,
        sha256, sha384, sha512, sha3_224, sha3_256, sha3_384, sha3_512
        """
    )

    def check_correctness(self, flag: str, user: User) -> bool:
        if self.flag_type == 'text' and flag == self.flag:
            return True
        elif self.flag_type == 'expr':
            if ExprFlag.objects.filter(sub_challenge=self, flag=flag, user=user).exists():
                return True
        return False

    def check_violation(self, flag: str, user: User) -> Union[User, None]:
        if self.flag_type == 'expr':
            violation = ExprFlag.objects.filter(sub_challenge=self, flag=flag).exclude(user=user)
            if violation.exists():
                return violation[0].user
        return None

    def save(self, *args, **kwargs):
        from submission.models import Submission

        # 启用状态改变时更新榜单
        if self.pk and self.get_dirty_fields().get('enabled'):
            enabled = True
        else:
            enabled = False

        flag_updated = True if self.get_dirty_fields().get('flag') else False

        super().save(*args, **kwargs)

        # 这一步必须在模型保存之后, 否则查询到的 enabled 仍为 True
        if enabled:
            Submission.regen_challenge_clear(self.challenge)
            Submission.regen_scoreboard()
            Submission.regen_first_blood()

        # flag 表达式有更新时更新 ExprFlag 表, ExprFlag 有 SubChallenge 的外键故更新要放到 save() 之后
        if self.flag_type == 'expr' and flag_updated:
            for user in User.objects.all():
                flag = eval_token_expression(self.flag, user.token)
                ExprFlag.objects.update_or_create(
                    user=user, sub_challenge=self,
                    defaults={'flag': flag}
                )

    class Meta:
        default_permissions = []


class ExprFlag(models.Model):
    """表达式 Flag 的实际值"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub_challenge = models.ForeignKey(SubChallenge, on_delete=models.CASCADE)
    flag = models.TextField()

    class Meta:
        default_permissions = []
        constraints = [
            models.UniqueConstraint(fields=['user', 'sub_challenge'], name='unique_flag_for_every_user')
        ]
