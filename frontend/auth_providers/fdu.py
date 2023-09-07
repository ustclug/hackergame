from datetime import timedelta

from django.urls import path

from .base import UserRegexAndDomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '复旦大学'}
    provider = 'fdu'
    group = 'fdu'


class GetCodeView(ExternalGetCodeView):
    provider = 'fdu'
    duration = timedelta(hours=1)
    validate_identity = UserRegexAndDomainEmailValidator(['fudan.edu.cn', 'm.fudan.edu.cn'], r'^\d{11}$')


urlpatterns = [
    path('fdu/login/', LoginView.as_view()),
    path('fdu/get_code/', GetCodeView.as_view()),
]
