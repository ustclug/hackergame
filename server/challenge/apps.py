from django.apps import AppConfig


class ChallengeConfig(AppConfig):
    name = 'server.challenge'

    def ready(self):
        from .interface import Challenge
        Challenge.app_ready()
