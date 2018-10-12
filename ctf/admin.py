from functools import partial

from django.contrib import admin

from .models import Page, TimerSwitch, Problem, Flag, Solve, Log, UserScoreCache

admin.site.register((Page, TimerSwitch, Solve))


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('name', 'index', 'score', 'is_open')
    list_filter = ('is_open',)
    search_fields = ('slug', 'name', 'detail')
    ordering = ('index',)


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'index', 'score')
    list_filter = ('problem',)
    ordering = ('problem', 'index')


class MatchFilter(admin.SimpleListFilter):
    title = 'match'
    parameter_name = 'match'

    def lookups(self, request, model_admin):
        return (
            ('true', 'true'),
            ('false', 'false'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(match__isnull=False)
        if self.value() == 'false':
            return queryset.filter(match__isnull=True)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'match', 'flag', 'time')
    list_filter = ('problem', MatchFilter, 'user__device__backend')
    search_fields = ('user__username',)
    ordering = ('-time',)


class HaveScoreFilter(admin.SimpleListFilter):
    title = 'score'
    parameter_name = 'score'

    def lookups(self, request, model_admin):
        return (
            ('true', 'score > 0'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(score__gt=0)


@admin.register(UserScoreCache)
class UserScoreCache(admin.ModelAdmin):
    list_display = ('rank', 'user', 'backend', 'identity', 'score', 'time')
    list_filter = ('user__device__backend', HaveScoreFilter)
    search_fields = ('user__username',)
    ordering = ('-score', 'time')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rank_counter = 0

    def __getattr__(self, item):
        if not item.startswith('flag_'):
            raise AttributeError(item)
        flag = Flag.objects.get(pk=item[5:])
        p = partial(self.flag_, flag)
        p.__name__ = str(flag)
        return p

    def get_list_display(self, request):
        flags = tuple(f'flag_{flag.pk}' for flag in Flag.objects.order_by('problem__index', 'index'))
        return self.list_display + flags

    def rank(self, obj):
        self.rank_counter += 1
        return self.rank_counter

    rank.short_description = '#'

    @staticmethod
    def backend(obj):
        try:
            return obj.info.first_backend.name
        except AttributeError:
            return None

    @staticmethod
    def identity(obj):
        try:
            return obj.user.device_set.all()[0].identity
        except IndexError:
            return None

    @staticmethod
    def flag_(flag, obj):
        try:
            return Solve.objects.get(user=obj.user, flag=flag).time
        except Solve.DoesNotExist:
            return None
