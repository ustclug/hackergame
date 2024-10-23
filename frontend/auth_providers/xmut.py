from datetime import timedelta

from django.urls import path

from .base import UserRegexAndDomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '厦门理工学院'}
    provider = 'xmut'
    group = 'xmut'


class GetCodeView(ExternalGetCodeView):
    provider = 'xmut'
    duration = timedelta(hours=1)
    validate_identity = UserRegexAndDomainEmailValidator('s.xmut.edu.cn', r'^[0-9]{9}$')


urlpatterns = [
    path('xmut/login/', LoginView.as_view()),
    path('xmut/get_code/', GetCodeView.as_view()),
]
