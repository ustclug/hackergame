from datetime import timedelta

from django.urls import path

from .base import DomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '广东工业大学'}
    provider = 'gdut'
    group = 'gdut'


class GetCodeView(ExternalGetCodeView):
    provider = 'gdut'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator(['mail2.gdut.edu.cn'])


urlpatterns = [
    path('gdut/login/', LoginView.as_view()),
    path('gdut/get_code/', GetCodeView.as_view()),
]
