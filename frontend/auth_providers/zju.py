from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '浙江大学'}
    provider = 'zju'
    group = 'zju'


class GetCodeView(ExternalGetCodeView):
    provider = 'zju'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('zju.edu.cn')


urlpatterns = [
    path('zju/login/', LoginView.as_view()),
    path('zju/get_code/', GetCodeView.as_view()),
]
