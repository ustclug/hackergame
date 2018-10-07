from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.db.transaction import atomic
from django.db.utils import ProgrammingError
from django.utils.decorators import classproperty
from django.utils.functional import cached_property
from django.utils.timezone import now

import otp
from utils.models import DictMixin, NameMixin, SingletonMixin

User = get_user_model()


class Page(SingletonMixin, models.Model):
    title = models.TextField(default='Hackergame')
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True, default='Hackergame,CTF')
    content = models.TextField(blank=True, help_text='Will be put into a div as HTML.')

    def __str__(self):
        return self.title


class TimerSwitch(models.Model):
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

    def _clear_cache(**kwargs):
        _ = kwargs
        key = 'timer_switch__is_on_now'
        cache.delete(key)

    models.signals.post_save.connect(_clear_cache, sender='ctf.TimerSwitch')
    models.signals.post_delete.connect(_clear_cache, sender='ctf.TimerSwitch')


class Problem(DictMixin, NameMixin, models.Model):
    slug = models.SlugField(primary_key=True)
    is_open = models.BooleanField(default=False)
    name = models.TextField()
    detail = models.TextField(blank=True)
    url = models.TextField(blank=True)
    index = models.IntegerField(default=0, db_index=True)

    class Meta:
        ordering = ('index',)

    @classproperty
    def open_objects(cls):
        return cls.objects.filter(is_open=True)

    @classproperty
    def total_score(cls):
        return cls.open_objects.aggregate(total_score=models.Sum('flag__score'))['total_score']

    @property
    def flags(self):
        return [dict(flag) for flag in self.flag_set.all()]

    @property
    def user_solved(self):
        flag_count = self.flag_set.count()
        if flag_count == 0:
            return 0
        elif flag_count == 1:
            return self.flag_set.all()[0].user_solved
        key = f'problem__{self.pk}__user_solved'
        cached = cache.get(key)
        if cached is None:
            solve_count = models.Count('solve', filter=models.Q(solve__flag__problem=self))
            cached = User.objects.annotate(solve_count=solve_count).filter(solve_count=flag_count).count()
            cache.set(key, cached)
        return cached

    def _clear_cache_solve(instance, **kwargs):
        _ = kwargs
        key = f'problem__{instance.flag.problem_id}__user_solved'
        cache.delete(key)

    models.signals.post_save.connect(_clear_cache_solve, sender='ctf.Solve')
    models.signals.post_delete.connect(_clear_cache_solve, sender='ctf.Solve')

    def _clear_cache_flag(instance, **kwargs):
        _ = kwargs
        key = f'problem__{instance.problem_id}__user_solved'
        cache.delete(key)

    models.signals.post_save.connect(_clear_cache_flag, sender='ctf.Flag')
    models.signals.post_delete.connect(_clear_cache_flag, sender='ctf.Flag')


class Flag(DictMixin, models.Model):
    problem = models.ForeignKey(Problem, models.CASCADE)
    name = models.TextField(blank=True)
    flag = models.TextField(unique=True)
    score = models.IntegerField(default=100)
    index = models.IntegerField(default=0, db_index=True)

    class Meta:
        ordering = ('index',)

    @property
    def user_solved(self):
        key = f'flag__{self.pk}__user_solved'
        cached = cache.get(key)
        if cached is None:
            cached = self.solve_set.count()
            cache.set(key, cached)
        return cached

    def _clear_cache(instance, **kwargs):
        _ = kwargs
        key = f'flag__{instance.flag_id}__user_solved'
        cache.delete(key)

    models.signals.post_save.connect(_clear_cache, sender='ctf.Solve')
    models.signals.post_delete.connect(_clear_cache, sender='ctf.Solve')

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

    class Meta:
        unique_together = ('user', 'flag')

    def __str__(self):
        return f'{self.flag} - {self.user}'


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
    def first_backend(self):
        try:
            return otp.site.backends_dict[self.user.device_set.all()[0].backend]
        except IndexError:
            return None

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
        if not self.first_backend:
            return 0
        return User.objects.filter(device__backend=self.first_backend.id)\
                           .filter(models.Q(userscorecache__score__gt=self.score)
                                   | models.Q(userscorecache__score=self.score, userscorecache__time__lt=self.time))\
                           .count() + 1

    @property
    def local_rank_total(self):
        if not self.first_backend:
            return 0
        return User.objects.filter(device__backend=self.first_backend.id).count()


class UserScoreCache(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    score = models.IntegerField(db_index=True)
    time = models.DateTimeField(db_index=True)

    def __str__(self):
        return f'{self.user}: {self.score}'

    @property
    def info(self):
        return CtfInfo(self.user)

    @classmethod
    def clear_cache(cls, user=None, **kwargs):
        _ = kwargs
        if user:
            with atomic():
                info = CtfInfo(user)
                cls.objects.filter(user=user).delete()
                cls.objects.create(user=user, score=info.score, time=info.time)
        else:
            for user in User.objects.all():
                cls.clear_cache(user)

    def _clear_cache_one(instance, **kwargs):
        _ = kwargs
        UserScoreCache.clear_cache(instance.user)

    models.signals.post_save.connect(_clear_cache_one, sender='ctf.Solve')
    models.signals.post_delete.connect(_clear_cache_one, sender='ctf.Solve')

    def _clear_cache_all(**kwargs):
        _ = kwargs
        UserScoreCache.clear_cache()

    models.signals.post_save.connect(_clear_cache_all, sender='ctf.Problem')
    models.signals.post_delete.connect(_clear_cache_all, sender='ctf.Problem')
    models.signals.post_save.connect(_clear_cache_all, sender='ctf.Flag')
    models.signals.post_delete.connect(_clear_cache_all, sender='ctf.Flag')
