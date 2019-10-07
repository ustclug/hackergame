from django.contrib import admin
from django.urls import path, include, re_path
from allauth.account.views import confirm_email

from apps import otp
from . import views

urlpatterns = [
    path('', views.HubView.as_view(), name='hub'),
    path('announcements/', views.AnnouncementsView.as_view(),
         name='announcements'),
    path('board/', views.BoardView.as_view(), name='board'),
    path('first/', views.FirstView.as_view(), name='first'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('otp/', otp.site.urls),
    path('admin/announcement/', views.AnnouncementAdminView.as_view()),
    path('admin/challenge/', views.ChallengeAdminView.as_view()),
    path('admin/submission/', views.SubmissionAdminView.as_view()),
    path('admin/terms/', views.TermsAdminView.as_view()),
    path('admin/trigger/', views.TriggerAdminView.as_view()),
    path('admin/user/', views.UserAdminView.as_view()),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.socialaccount.providers.google.urls')),
    path('accounts/', include('allauth.socialaccount.providers.microsoft.urls')),
    re_path(r'^accounts/confirm-email/(?P<key>[-:\w]+)/$', confirm_email, name='account_confirm_email'),
]
