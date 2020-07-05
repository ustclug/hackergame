from django.urls import path

from .views import RegisterAPI, LoginAPI

urlpatterns = [
    path('user/registration/', RegisterAPI.as_view()),
    path('user/login/', LoginAPI.as_view())
]