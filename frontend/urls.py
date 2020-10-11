from django.contrib import admin
from django.urls import path, include

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
    path('user/', views.UserView.as_view()),

    path('profile/ustc/', views.UstcProfileView.as_view(), name='ustcprofile'),

    path('accounts/', include('frontend.auth_providers.debug')),
    path('accounts/', include('frontend.auth_providers.ustc')),
    path('accounts/', include('frontend.auth_providers.jlu')),
    path('accounts/', include('frontend.auth_providers.nankai')),
    path('accounts/', include('frontend.auth_providers.bupt')),
    path('accounts/', include('frontend.auth_providers.cqu')),
    path('accounts/', include('frontend.auth_providers.hit')),
    path('accounts/', include('frontend.auth_providers.neu')),
    path('accounts/', include('frontend.auth_providers.sms')),
    path('accounts/', include('allauth.socialaccount.providers.google.urls')),
    path('accounts/', include('allauth.socialaccount.providers.microsoft.urls')),

    path('admin/announcement/', views.AnnouncementAdminView.as_view()),
    path('admin/challenge/', views.ChallengeAdminView.as_view()),
    path('admin/submission/', views.SubmissionAdminView.as_view()),
    path('admin/terms/', views.TermsAdminView.as_view()),
    path('admin/trigger/', views.TriggerAdminView.as_view()),
    path('admin/user/', views.UserAdminView.as_view()),
    path('admin/', admin.site.urls),
]
