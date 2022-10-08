from datetime import timedelta

from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import path

from .base import BaseLoginView, BaseGetCodeView, DomainEmailValidator, UserRegexAndDomainEmailValidator


class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '复旦大学'}
    provider = 'fdu'
    group = 'fdu'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')

    def normalize_identity(self):
        return self.identity.casefold()


class GetCodeView(BaseGetCodeView):
    provider = 'fdu'
    duration = timedelta(hours=1)
    validate_identity = UserRegexAndDomainEmailValidator('fudan.edu.cn', r'^\d{11}$')

    def send(self, identity, code):
        EmailMessage(
            subject=f'Hackergame 登录校验码：{code}',
            body=f'{code}\n请使用该校验码登录 Hackergame\n',
            to=[identity],
        ).send()


urlpatterns = [
    path('fdu/login/', LoginView.as_view()),
    path('fdu/get_code/', GetCodeView.as_view()),
]
