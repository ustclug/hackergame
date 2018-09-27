from django.contrib import admin

from .models import TimerSwitch, Problem, Flag, Solve, Log, UserScoreCache

admin.site.register((TimerSwitch, Problem, Flag, Solve, Log, UserScoreCache))
