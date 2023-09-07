from datetime import timedelta

from django.urls import path

from .base import UserRegexAndDomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '同济大学'}
    provider = 'tongji'
    group = 'tongji'


class GetCodeView(ExternalGetCodeView):
    provider = 'tongji'
    duration = timedelta(hours=1)
    validate_identity = UserRegexAndDomainEmailValidator('tongji.edu.cn', r'^\d{7}$')


urlpatterns = [
    path('tongji/login/', LoginView.as_view()),
    path('tongji/get_code/', GetCodeView.as_view()),
]
