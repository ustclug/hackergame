from django.contrib import admin

from .models import Problem, Flag, Solve, Log, UserScoreCache

admin.site.register((Problem, Flag, Solve, Log, UserScoreCache))
