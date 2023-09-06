from datetime import timedelta

from django.urls import path

from .base import RegexDomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '哈尔滨工业大学'}
    provider = 'hit'
    group = 'hit'


class GetCodeView(ExternalGetCodeView):
    provider = 'hit'
    duration = timedelta(hours=1)
    validate_identity = RegexDomainEmailValidator(r'^(\w+\.)?hit(wh|sz|)\.edu\.cn$')


urlpatterns = [
    path('hit/login/', LoginView.as_view()),
    path('hit/get_code/', GetCodeView.as_view()),
]
