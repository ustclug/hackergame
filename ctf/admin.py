from django.contrib import admin

from .models import Problem, Flag, Solve, Log

admin.site.register((Problem, Flag, Solve, Log))
