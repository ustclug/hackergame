from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '中山大学'}
    provider = 'sysu'
    group = 'sysu'


class GetCodeView(ExternalGetCodeView):
    provider = 'sysu'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('mail2.sysu.edu.cn')


urlpatterns = [
    path('sysu/login/', LoginView.as_view()),
    path('sysu/get_code/', GetCodeView.as_view()),
]
