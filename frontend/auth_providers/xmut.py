from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '厦门理工学院'}
    provider = 'xmut'
    group = 'xmut'


class GetCodeView(ExternalGetCodeView):
    provider = 'xmut'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator(['s.xmut.edu.cn'])


urlpatterns = [
    path('xmut/login/', LoginView.as_view()),
    path('xmut/get_code/', GetCodeView.as_view()),
]
