from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '南方科技大学'}
    provider = 'sustech'
    group = 'sustech'


class GetCodeView(ExternalGetCodeView):
    provider = 'sustech'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator(['sustech.edu.cn', 'mail.sustech.edu.cn'])


urlpatterns = [
    path('sustech/login/', LoginView.as_view()),
    path('sustech/get_code/', GetCodeView.as_view()),
]
