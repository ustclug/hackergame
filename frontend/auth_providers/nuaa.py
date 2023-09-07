from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '南京航空航天大学'}
    provider = 'nuaa'
    group = 'nuaa'


class GetCodeView(ExternalGetCodeView):
    provider = 'nuaa'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('nuaa.edu.cn')


urlpatterns = [
    path('nuaa/login/', LoginView.as_view()),
    path('nuaa/get_code/', GetCodeView.as_view()),
]
