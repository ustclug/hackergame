from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '吉林大学'}
    provider = 'jlu'
    group = 'jlu'


class GetCodeView(ExternalGetCodeView):
    provider = 'jlu'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('mails.jlu.edu.cn')


urlpatterns = [
    path('jlu/login/', LoginView.as_view()),
    path('jlu/get_code/', GetCodeView.as_view()),
]
