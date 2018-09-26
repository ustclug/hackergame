from django.contrib import admin
from django.urls import path

from ctf.views import Hub

urlpatterns = [
    path('', Hub.as_view(), name='hub'),
    path('admin/', admin.site.urls),
]
