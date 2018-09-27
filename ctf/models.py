from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.db.transaction import atomic
from django.utils.functional import cached_property

from utils.models import DictMixin, NameMixin

User = get_user_model()


class ProblemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_open=True)


class Problem(DictMixin, NameMixin, models.Model):
    slug = models.SlugField(primary_key=True)
    is_open = models.BooleanField(default=False)
    name = models.TextField()
    detail = models.TextField(blank=True)
    url = models.TextField(blank=True)

    manager = ProblemManager()

    @staticmethod
    def annotated(queryset):
        return queryset\
            .prefetch_related('flag_set')\
            .annotate(score=models.Sum('flag__score'))\
            .order_by('score')

    @property
    def flags(self):
        return [dict(flag) for flag in self.flag_set.all()]

    def keys(self):
        yield from super().keys()
        for key in ('score',):
            if hasattr(self, key):
                yield key


class Flag(DictMixin, models.Model):
    problem = models.ForeignKey(Problem, models.CASCADE)
    name = models.TextField(blank=True)
    flag = models.TextField(unique=True)
    score = models.IntegerField(default=100)

    @property
    def user_solved(self):
        key = f'flag__{self.pk}__user_solved'
        cached = cache.get(key)
        if cached is None:
            cached = self.solve_set.count()
            cache.set(key, cached)
        return cached

    def __str__(self):
        return f'{self.problem}/{self.name}' if self.name else f'{self.problem}'

    def keys(self):
        yield 'pk'
        yield 'name'
        yield 'score'
        yield 'user_solved'


class Solve(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    flag = models.ForeignKey(Flag, models.PROTECT)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.flag} - {self.user}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        key = f'flag__{self.pk}__user_solved'
        cache.delete(key)


class Log(models.Model):
    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    problem = models.ForeignKey(Problem, models.PROTECT)
    flag = models.TextField()
    match = models.ForeignKey(Flag, models.PROTECT, null=True, blank=True)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.problem} - {self.user}: {self.flag}'


class CtfInfo:
    def __init__(self, user):
        self.user = user

    @cached_property
    def score(self):
        return self.user.solve_set.aggregate(score=models.Sum('flag__score'))['score'] or 0

    @property
    def solved_flags(self):
        return [solve.flag_id for solve in self.user.solve_set.all()]

    @cached_property
    def time(self):
        return self.user.solve_set.aggregate(time=models.Max('time'))['time'] or datetime(1970, 1, 1, 0, 0, 0)

    @property
    def rank(self):
        return User.objects.filter(models.Q(userscorecache__score__gt=self.score)
                                   | models.Q(userscorecache__score=self.score, userscorecache__time__lt=self.time))\
                           .count() + 1

    @property
    def rank_total(self):
        return User.objects.count()

    @property
    def local_rank(self):
        return User.objects.filter(last_name=self.user.last_name)\
                           .filter(models.Q(userscorecache__score__gt=self.score)
                                   | models.Q(userscorecache__score=self.score, userscorecache__time__lt=self.time))\
                           .count() + 1

    @property
    def local_rank_total(self):
        return User.objects.filter(last_name=self.user.last_name).count()


class UserScoreCache(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    score = models.IntegerField(db_index=True)
    time = models.DateTimeField(db_index=True)

    def __str__(self):
        return f'{self.user}: {self.score}'

    @classmethod
    def update(cls, user=None):
        if user:
            with atomic():
                info = CtfInfo(user)
                cls.objects.filter(user=user).delete()
                cls.objects.create(user=user, score=info.score, time=info.time)
        else:
            for user in User.objects.all():
                cls.update(user)
