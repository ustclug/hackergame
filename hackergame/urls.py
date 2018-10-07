from django.contrib import admin
from django.urls import path

import otp
from ctf.views import Board, Hub
from logout.views import Logout
from nickname.views import Nickname
from terms.views import TermsList

urlpatterns = [
    path('', Hub.as_view(), name='hub'),
    path('board/', Board.as_view(), name='board'),
    path('board/<backend>/', Board.as_view(), name='board'),
    path('logout/', Logout.as_view(), name='logout'),
    path('nickname/', Nickname.as_view(), name='nickname'),
    path('otp/', otp.site.urls),
    path('terms/', TermsList.as_view(), name='terms'),
    path('admin/', admin.site.urls),
]
