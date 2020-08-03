from django.urls import path

from submission.views import SubmissionAPI, BoardAPI

urlpatterns = [
    path('submission/', SubmissionAPI.as_view()),
    path('board/score/', BoardAPI)
]
