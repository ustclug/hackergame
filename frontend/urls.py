from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.HubView.as_view(), name='hub'),
    path('announcements/', views.AnnouncementsView.as_view(),
         name='announcements'),
    path('board/', views.BoardView.as_view(), name='board'),
    path('first/', views.FirstView.as_view(), name='first'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('user/', views.UserView.as_view()),
    path('qa/', views.QaView.as_view(), name='qa'),
    path('credits/', views.CreditsView.as_view(), name='credits'),
    path('account/', views.AccountView.as_view(), name='account'),
    path('error/', views.ErrorView.as_view()),
    path('data/core.json', views.CoreDataView.as_view(), name='coredata'),
    path('challenge/<int:challenge_id>/', views.ChallengeURLView.as_view(), name='challenge_url'),
    path('score/', views.ScoreView.as_view(), name='score'),

    path('profile/ustc/', views.UstcProfileView.as_view(), name='ustcprofile'),

    path('accounts/', include('frontend.auth_providers.debug')),
    path('accounts/', include('frontend.auth_providers.ustc')),
    path('accounts/', include('frontend.auth_providers.zju')),
    path('accounts/', include('frontend.auth_providers.jlu')),
    path('accounts/', include('frontend.auth_providers.nuaa')),
    path('accounts/', include('frontend.auth_providers.neu')),
    path('accounts/', include('frontend.auth_providers.sysu')),
    path('accounts/', include('frontend.auth_providers.xidian')),
    path('accounts/', include('frontend.auth_providers.hit')),
    path('accounts/', include('frontend.auth_providers.fdu')),
    path('accounts/', include('frontend.auth_providers.tongji')),
    path('accounts/', include('frontend.auth_providers.gdou')),
    path('accounts/', include('frontend.auth_providers.sustech')),
    path('accounts/', include('frontend.auth_providers.xmut')),
    path('accounts/', include('frontend.auth_providers.shu')),
    path('accounts/', include('frontend.auth_providers.nyist')),
    path('accounts/', include('frontend.auth_providers.sjtu')),
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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
