from django.contrib import admin
from django.urls import path

import otp
from ctf.views import Hub
from logout.views import Logout
from nickname.views import Nickname

urlpatterns = [
    path('', Hub.as_view(), name='hub'),
    path('logout/', Logout.as_view(), name='logout'),
    path('nickname/', Nickname.as_view(), name='nickname'),
    path('otp/', otp.site.urls),
    path('admin/', admin.site.urls),
]
