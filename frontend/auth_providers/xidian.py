from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '西安电子科技大学'}
    provider = 'xidian'
    group = 'xidian'


class GetCodeView(ExternalGetCodeView):
    provider = 'xidian'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('stu.xidian.edu.cn')


urlpatterns = [
    path('xidian/login/', LoginView.as_view()),
    path('xidian/get_code/', GetCodeView.as_view()),
]
