from django.apps import AppConfig


class SubmissionConfig(AppConfig):
    name = 'server.submission'

    def ready(self):
        from .interface import Submission
        Submission.app_ready()
