"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from challenge.admin_views import ImageUploadView

urlpatterns = [
    path('admin/challenge/upload_image/', ImageUploadView.as_view()),
    path('admin/', admin.site.urls),
    path('api/user/', include('user.urls')),
    path('api/group/', include('group.urls')),
    path('api/stage/', include('contest.urls')),
    path('api/challenge/', include('challenge.urls')),
    path('api/', include('submission.urls')),
    path('api/announcement/', include('announcement.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += staticfiles_urlpatterns()
