from datetime import timedelta

from django.urls import path

from .base import UserRegexAndDomainEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '东北大学'}
    provider = 'neu'
    group = 'neu'


class GetCodeView(ExternalGetCodeView):
    provider = 'neu'
    duration = timedelta(hours=1)
    validate_identity = UserRegexAndDomainEmailValidator('stu.neu.edu.cn', r'^((20(19|20|21|22)1?\d{4})|((19|20|21|22)\d{5}))$')


urlpatterns = [
    path('neu/login/', LoginView.as_view()),
    path('neu/get_code/', GetCodeView.as_view()),
]
