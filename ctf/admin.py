from django.contrib import admin

from .models import Page, TimerSwitch, Problem, Flag, Solve, Log, UserScoreCache

admin.site.register((Page, TimerSwitch, Problem, Flag, Solve, Log, UserScoreCache))
