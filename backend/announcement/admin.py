from django.contrib import admin

from announcement.models import Announcement


@admin.register(Announcement)
class ChallengeAdmin(admin.ModelAdmin):
    readonly_fields = ['created_time', 'updated_time']
