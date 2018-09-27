from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.db.transaction import atomic
from django.db.utils import ProgrammingError
from django.utils.functional import cached_property
from django.utils.timezone import now

from utils.models import DictMixin, NameMixin, UpdateCacheMixin

User = get_user_model()


class TimerSwitch(UpdateCacheMixin, models.Model):
    time = models.DateTimeField(default=now)
    on_off = models.BooleanField()
    note = models.TextField(blank=True)

    def __str__(self):
        return f'{self.time} {"on" if self.on_off else "off"}{": " + self.note if self.note else ""}'

    @classmethod
    def is_on_now(cls):
        class State:
            def __init__(self, state, note):
                self.state = state
                self.note = note

            def __bool__(self):
                return self.state

            def __str__(self):
                return self.note

        key = 'timer_switch__is_on_now'
        cached = cache.get(key)
        if cached is None:
            try:
                obj = cls.objects.filter(time__lt=now()).latest('time')
                cached = obj.on_off, obj.note or ('比赛正在进行' if obj.on_off else '比赛暂时关闭')
            except cls.DoesNotExist:
                cached = False, '比赛尚未开始'
            except ProgrammingError:  # we are making migrations
                return State(False, '')
            cache.set(key, cached)
        return State(*cached)

    def update_cache(self):
        key = 'timer_switch__is_on_now'
        cache.delete(key)


class ProblemManager(models.Manager):
    def get_queryset(self):
        if TimerSwitch.is_on_now():
            return super().get_queryset().filter(is_open=True)
        else:
            return super().get_queryset().none()


class Problem(DictMixin, NameMixin, models.Model):
    slug = models.SlugField(primary_key=True)
    is_open = models.BooleanField(default=False)
    name = models.TextField()
    detail = models.TextField(blank=True)
    url = models.TextField(blank=True)

    objects = models.Manager()
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


class Solve(UpdateCacheMixin, models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    flag = models.ForeignKey(Flag, models.PROTECT)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.flag} - {self.user}'

    def update_cache(self):
        key = f'flag__{self.flag_id}__user_solved'
        cache.delete(key)
        UserScoreCache.update(self.user)


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
