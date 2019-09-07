from django.contrib import admin
from django.urls import path

from . import otp
from .ctf.views import Board, Hub
from .local.views import FirstBlood
from .logout.views import Logout
from .nickname.views import Nickname
from .terms.views import TermsList
from .upload.views import Upload

urlpatterns = [
    path('', Hub.as_view(), name='hub'),
    path('board/', Board.as_view(), name='board'),
    path('board/<backend>/', Board.as_view(), name='board'),
    path('first_blood/', FirstBlood.as_view(), name='first_blood'),
    path('logout/', Logout.as_view(), name='logout'),
    path('nickname/', Nickname.as_view(), name='nickname'),
    path('otp/', otp.site.urls),
    path('terms/', TermsList.as_view(), name='terms'),
    path('upload/', Upload.as_view(), name='upload'),
    path('admin/', admin.site.urls),
]
