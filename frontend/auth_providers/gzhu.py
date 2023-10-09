from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '广州大学'}
    provider = 'gzhu'
    group = 'gzhu'


class GetCodeView(ExternalGetCodeView):
    provider = 'gzhu'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator(['e.gzhu.edu.cn'])


urlpatterns = [
    path('gzhu/login/', LoginView.as_view()),
    path('gzhu/get_code/', GetCodeView.as_view()),
]
