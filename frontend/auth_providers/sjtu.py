from datetime import timedelta

from django.urls import path

from .base import UserRegexAndDomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '上海交通大学'}
    provider = 'sjtu'
    group = 'sjtu'


class GetCodeView(ExternalGetCodeView):
    provider = 'sjtu'
    duration = timedelta(hours=1)
    validate_identity = UserRegexAndDomainEmailValidator('sjtu.edu.cn', r'^\w+([-+.]\w+)*$')


urlpatterns = [
    path('sjtu/login/', LoginView.as_view()),
    path('sjtu/get_code/', GetCodeView.as_view()),
]
