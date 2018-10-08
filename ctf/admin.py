from django.contrib import admin

from .models import Page, TimerSwitch, Problem, Flag, Solve, Log, UserScoreCache

admin.site.register((Page, TimerSwitch, Solve, Log, UserScoreCache))


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
