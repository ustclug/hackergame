from django.contrib import admin

from submission.models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'challenge', 'flag', 'created_time', 'sub_challenge_clear')
    list_filter = ('violation_user', 'user')
