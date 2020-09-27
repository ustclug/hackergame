from django.db import models
from django.db.models import F
from django.utils import timezone

from user.models import User
from group.models import Group
from challenge.models import Challenge, SubChallenge


class SubmissionManager(models.Manager):
    def regen_challenge_clear(self, challenge: Challenge):
        ChallengeClear.objects.filter(challenge=challenge).delete()
        for submission in self.filter(challenge=challenge):
            submission.update_challenge_clear()

    def regen_scoreboard(self):
        Scoreboard.objects.all().delete()
        for submission in self.all():
            submission.update_scoreboard()
            submission.update_scoreboard(submission.challenge.category)

    def regen_first_blood(self):
        ChallengeFirstBlood.objects.all().delete()
        SubChallengeFirstBlood.objects.all().delete()
        for submission in self.all():
            submission.update_first_blood()

    def regen_board(self):
        self.regen_scoreboard()
        self.regen_first_blood()


class Submission(models.Model):
    """每一次提交"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    flag = models.TextField()

    # 以下字段无需在创建时指定
    created_time = models.DateTimeField(default=timezone.now, db_index=True)
    correctness = models.BooleanField(default=False)
    sub_challenge_clear = models.ForeignKey(SubChallenge, on_delete=models.CASCADE, null=True)
    violation_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='violation_submission',
                                       null=True, verbose_name="和该用户的某一 flag 重复")

    objects = SubmissionManager()

    def __str__(self):
        return f'Submission {self.id} user={self.user}, challenge={self.challenge}, ' \
               f'created_time={self.created_time}, sub_challenge_clear={self.sub_challenge_clear}'

    def save(self, *args, **kwargs):
        # 重复提交无需更新 sub_challenge_clear, violation_user
        if Submission.objects.filter(user=self.user, challenge=self.challenge, flag=self.flag,
                                     sub_challenge_clear__isnull=False).exists():
            self.correctness = True

        # sub_challenge_clear, violation_user, correctness 不会在创建后被改变
        elif not self.pk:
            for sub_challenge in self.challenge.sub_challenge.filter(enabled=True):
                if sub_challenge.check_correctness(self.flag, self.user):
                    self.correctness = True
                    self.sub_challenge_clear = sub_challenge
                else:
                    violation_user = sub_challenge.check_violation(self.flag, self.user)
                    if violation_user is not None:
                        self.violation_user = violation_user

        super().save(*args, **kwargs)

        self.update_challenge_clear()
        self.update_board()

    def update_challenge_clear(self) -> None:
        if self.sub_challenge_clear is None or self.sub_challenge_clear.enabled is False:
            return

        correct_challenge_submission = Submission.objects.filter(
            challenge=self.challenge,
            user=self.user,
            sub_challenge_clear__isnull=False,
            sub_challenge_clear__enabled=True,
        ).exclude(
            id=self.id
        ).filter(
            created_time__lt=self.created_time
        )
        if correct_challenge_submission.count() == \
                self.challenge.sub_challenge.filter(enabled=True).count() - 1:
            ChallengeClear.objects.create(user=self.user, time=self.created_time, challenge=self.challenge)

    def update_board(self) -> None:
        """更新榜单"""
        if self.sub_challenge_clear:
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
        if self.user.groups.filter(name='no_score').exists():
            return
        if group:
            groups = [group]
        else:
            groups = list(Group.objects.filter(application__user=self.user, application__status='accepted')) \
                     + [None]
        for g in groups:
            if self.sub_challenge_clear and self.sub_challenge_clear.enabled is True:
                self._update_first_blood_obj(SubChallengeFirstBlood, g,
                                             {'sub_challenge': self.sub_challenge_clear})
            if ChallengeClear.objects.filter(user=self.user, challenge=self.challenge).exists():
                self._update_first_blood_obj(ChallengeFirstBlood, g, {'challenge': self.challenge})

    def update_scoreboard(self, category: str = '') -> None:
        """累加某题的分数, 若分类为空则为总榜"""
        if self.user.groups.filter(name='no_score').exists():
            return
        # 必须是一个过题的提交且该子题为启用状态
        if self.sub_challenge_clear is None or self.sub_challenge_clear.enabled is False:
            return
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
                time=self.created_time  # FIXME: 是否会出现榜单时间并不属于最新提交?
            )

    class Meta:
        default_permissions = []
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'sub_challenge_clear'],
                name='unique_sub_challenge_clear'
            ),
        ]


class ChallengeClear(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    time = models.DateTimeField()

    class Meta:
        default_permissions = []
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'challenge'],
                name='unique_challenge_clear'
            )
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
        default_permissions = []
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
        default_permissions = []
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
        default_permissions = []
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'category'],
                name='unique_score_category'
            ),
        ]
