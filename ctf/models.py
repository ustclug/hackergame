from django.contrib.auth import get_user_model
from django.db import models

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
            .annotate(score=models.Sum('flag__score'),
                      user_solved=models.Count('flag__solve__user', distinct=True))\
            .order_by('score')

    @property
    def flags(self):
        return [dict(flag) for flag in self.flag_set.all()]

    def keys(self):
        yield from super().keys()
        for key in ('score', 'user_solved'):
            if hasattr(self, key):
                yield key


class Flag(DictMixin, models.Model):
    problem = models.ForeignKey(Problem, models.CASCADE)
    name = models.TextField(blank=True)
    flag = models.TextField(unique=True)
    score = models.IntegerField(default=100)

    @property
    def user_solved(self):
        return self.solve_set.count()

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


class Log(models.Model):
    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    problem = models.ForeignKey(Problem, models.PROTECT)
    flag = models.TextField()
    match = models.ForeignKey(Flag, models.PROTECT, null=True, blank=True)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.problem} - {self.user}: {self.flag}'
