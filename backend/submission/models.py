from django.db import models
from django.db.models import Q, F

from user.models import User
from group.models import Group
from challenge.models import Challenge, SubChallenge


class Submission(models.Model):
    """每一次提交"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    flag = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    correctness = models.BooleanField(default=False)
    challenge_clear = models.BooleanField(default=False)
    sub_challenge_clear = models.ForeignKey(SubChallenge, on_delete=models.CASCADE, null=True)
    violation_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='violation_submission',
                                       null=True, verbose_name="和该用户的某一 flag 重复")

    def save(self, *args, **kwargs):
        self.update_clear_status()

        super().save(*args, **kwargs)

        self.update_board()

    def update_clear_status(self) -> bool:
        # 判断重复提交
        if Submission.objects.filter(user=self.user, challenge=self.challenge, flag=self.flag,
                                     sub_challenge_clear=True).exists():
            return True

        self.correctness = False
        self.challenge_clear = False
        self.sub_challenge_clear = None
        self.violation_user = None

        # 更新 clear 状态
        for sub_challenge in self.challenge.sub_challenge.filter(enabled=True):
            if sub_challenge.check_correctness(self.flag, self.user):
                self.correctness = True
                self.sub_challenge_clear = sub_challenge
            violation_user = sub_challenge.check_violation(self.flag, self.user)
            if violation_user is not None:
                self.violation_user = violation_user

        if self.sub_challenge_clear is not None:
            correct_challenge_submission = Submission.objects.filter(challenge=self.challenge, user=self.user,
                                                                     sub_challenge_clear__isnull=False)
            if correct_challenge_submission.count() == self.challenge.sub_challenge.count() - 1:
                self.challenge_clear = True

        return self.correctness

    def update_board(self) -> None:
        """更新榜单"""
        if self.sub_challenge_clear and not self.user.groups.filter(name='no_score').exists():
            # FIXME no score group
            self.update_first_blood()
            self.update_scoreboard()
            self.update_scoreboard(self.challenge.category)

    def _update_first_blood_obj(self, board, group, values) -> None:
        try:
            s = board.objects.get(group=group, **values)
            if self.created_time < s.time:
                s.user = self.user
                s.time = self.created_time
                s.save()
        except board.DoesNotExist:
            board.objects.create(user=self.user, time=self.created_time, group=group, **values)

    def update_first_blood(self, group=None) -> None:
        """更新一血榜"""
        if group:
            groups = [group]
        else:
            groups = list(Group.objects.filter(application__user=self.user, application__status='accepted')) \
                     + [None]
        for g in groups:
            if self.sub_challenge_clear:
                self._update_first_blood_obj(SubChallengeFirstBlood, g,
                                             {'sub_challenge': self.sub_challenge_clear})
            if self.challenge_clear:
                self._update_first_blood_obj(ChallengeFirstBlood, g, {'challenge': self.challenge})

    def update_scoreboard(self, category: str = '') -> None:
        """更新分数榜, 若分类为空则为总榜"""
        try:
            scoreboard = Scoreboard.objects.get(user=self.user, category=category)
            scoreboard.score = F('score') + self.sub_challenge_clear.score
            scoreboard.time = self.created_time
            scoreboard.save()
        except Scoreboard.DoesNotExist:
            Scoreboard.objects.create(
                user=self.user,
                category=category,
                score=self.sub_challenge_clear.score,
                time=self.created_time
            )

    def regen_clear_status(self, challenge: Challenge):
        ...  # TODO

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


class FirstBlood(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)  # 为 null 时即为总榜单
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField()

    class Meta:
        abstract = True


class ChallengeFirstBlood(FirstBlood):
    """题目一血榜单"""
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=['challenge', 'group'],
                name='unique_challenge_first'
            ),
        ]


class SubChallengeFirstBlood(FirstBlood):
    """子题一血榜单"""
    sub_challenge = models.ForeignKey(SubChallenge, on_delete=models.CASCADE)

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
