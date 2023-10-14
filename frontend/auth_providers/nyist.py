from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '南阳理工学院'}
    provider = 'nyist'
    group = 'nyist'


class GetCodeView(ExternalGetCodeView):
    provider = 'nyist'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('nyist.edu.cn')


urlpatterns = [
    path('nyist/login/', LoginView.as_view()),
    path('nyist/get_code/', GetCodeView.as_view()),
]
