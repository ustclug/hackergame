from django.urls import path

from submission.views import SubmissionAPI, ScoreboardAPI, FirstBloodBoardAPI, ChallengeClearAPI

urlpatterns = [
    path('submission/', SubmissionAPI.as_view()),
    path('board/score/', ScoreboardAPI.as_view()),
    path('board/firstblood/', FirstBloodBoardAPI.as_view()),
    path('challenge/clear/', ChallengeClearAPI.as_view()),
]
