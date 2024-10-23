from datetime import timedelta

from django.urls import path

from .base import UserRegexAndDomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '上海大学'}
    provider = 'shu'
    group = 'shu'


class GetCodeView(ExternalGetCodeView):
    provider = 'shu'
    duration = timedelta(hours=1)
    validate_identity = UserRegexAndDomainEmailValidator('shu.edu.cn', r'^[a-z0-9_-]{3,50}$')


urlpatterns = [
    path('shu/login/', LoginView.as_view()),
    path('shu/get_code/', GetCodeView.as_view()),
]
