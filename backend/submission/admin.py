from django.contrib import admin

from submission.models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    ...
