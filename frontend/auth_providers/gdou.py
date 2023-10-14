from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '广东海洋大学'}
    provider = 'gdou'
    group = 'gdou'


class GetCodeView(ExternalGetCodeView):
    provider = 'gdou'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator(['stu.gdou.edu.cn'])


urlpatterns = [
    path('gdou/login/', LoginView.as_view()),
    path('gdou/get_code/', GetCodeView.as_view()),
]
