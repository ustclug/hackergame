from django.urls import path

from user.views import RegisterAPI, LoginAPI, LogoutAPI, ProfileAPI

urlpatterns = [
    path('register/', RegisterAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path('logout/', LogoutAPI.as_view()),
    path('', ProfileAPI.as_view()),
]
