from django.urls import path

from announcement.views import AnnouncementAPI

urlpatterns = [
    path('', AnnouncementAPI.as_view()),
]
