from django.contrib import admin

from contest.models import Stage, Pause


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Stage 表只允许一行数据
        return False


@admin.register(Pause)
class PauseAdmin(admin.ModelAdmin):
    ...
