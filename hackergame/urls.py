from django.contrib import admin
from django.urls import path

import otp
from ctf.views import Hub

urlpatterns = [
    path('', Hub.as_view(), name='hub'),
    path('otp/', otp.site.urls),
    path('admin/', admin.site.urls),
]
