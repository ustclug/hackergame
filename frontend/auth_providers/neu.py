from datetime import timedelta
import requests

from django.conf import settings
from django.shortcuts import redirect
from django.urls import path
from django.core.mail import EmailMessage

from .base import BaseLoginView, BaseGetCodeView, DomainEmailValidator, UserRegexAndDomainEmailValidator


class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '东北大学'}
    provider = 'neu'
    group = 'neu'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')

    def normalize_identity(self):
        return self.identity.casefold()


class GetCodeView(BaseGetCodeView):
    provider = 'neu'
    duration = timedelta(hours=1)
    validate_identity = UserRegexAndDomainEmailValidator('stu.neu.edu.cn', r'^((20(19|20|21|22)1?\d{4})|((19|20|21|22)\d{5}))$')

    def send(self, identity, code):
        EmailMessage(
            subject=f'Hackergame 登录校验码：{code}',
            body=f'{code}\n请使用该校验码登录 Hackergame\n',
            to=[identity],
        ).send()


urlpatterns = [
    path('neu/login/', LoginView.as_view()),
    path('neu/get_code/', GetCodeView.as_view()),
]
