from functools import partial

from django.contrib import admin

from .models import Page, TimerSwitch, Problem, Flag, Solve, Log, UserScoreCache

admin.site.register((Page, TimerSwitch, Solve, Log))


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
    list_display = ('user', 'backend', 'score', 'time')
    list_filter = ('user__device__backend', HaveScoreFilter)
    search_fields = ('user',)
    ordering = ('-score', 'time')

    def __getattr__(self, item):
        if not item.startswith('flag_'):
            raise AttributeError(item)
        flag = Flag.objects.get(pk=item[5:])
        p = partial(self.flag_, flag)
        p.__name__ = str(flag)
        p.boolean = True
        return p

    def get_list_display(self, request):
        flags = tuple(f'flag_{flag.pk}' for flag in Flag.objects.order_by('problem__index', 'index'))
        return self.list_display + flags

    @staticmethod
    def backend(obj):
        return obj.info.first_backend.name

    @staticmethod
    def flag_(flag, obj):
        try:
            Solve.objects.get(user=obj.user, flag=flag)
            return True
        except Solve.DoesNotExist:
            return False
