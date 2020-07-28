from django.urls import path

from challenge.views import ChallengeAPI

urlpatterns = [
    path('', ChallengeAPI.as_view()),
]
