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


@admin.register(UserScoreCache)
class UserScoreCache(admin.ModelAdmin):
    list_display = ('user', 'backend', 'score', 'time')
    list_filter = ('backend',)
    search_fields = ('user',)
    ordering = ('-score', 'time')

    def __getattr__(self, item):
        if item.startswith('flag_'):
            return partial(self.flag_, item[5:])
        raise AttributeError(item)

    def get_list_display(self, request):
        flags = tuple(f'flag_{flag.pk}' for flag in Flag.objects.order_by('problem__index', 'index'))
        return self.list_display + flags

    @staticmethod
    def backend(obj):
        return obj.info.first_backend.name

    @staticmethod
    def flag_(flag, obj):
        try:
            Solve.objects.get(user=obj, flag_id=flag)
            return True
        except Solve.DoesNotExist:
            return False
