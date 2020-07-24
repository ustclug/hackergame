from django.urls import path

from .views import StageAPI, CurrentStageAPI

urlpatterns = [
    path('current/', CurrentStageAPI.as_view()),
    path('', StageAPI.as_view()),
]
