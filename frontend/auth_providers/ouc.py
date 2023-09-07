from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '中国海洋大学'}
    provider = 'ouc'
    group = 'ouc'


class GetCodeView(ExternalGetCodeView):
    provider = 'ouc'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('stu.ouc.edu.cn')


urlpatterns = [
    path('ouc/login/', LoginView.as_view()),
    path('ouc/get_code/', GetCodeView.as_view()),
]
