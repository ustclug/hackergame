from datetime import timedelta

from django.conf import settings
from django.shortcuts import redirect
from django.urls import path
from django.core.mail import EmailMessage

from .base import BaseLoginView, BaseGetCodeView, UserRegexAndDomainEmailValidator


class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '同济大学'}
    provider = 'tongji'
    group = 'tongji'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')

    def normalize_identity(self):
        return self.identity.casefold()


class GetCodeView(BaseGetCodeView):
    provider = 'tongji'
    duration = timedelta(hours=1)
    validate_identity = UserRegexAndDomainEmailValidator('tongji.edu.cn', r'^\d{7}$')

    def send(self, identity, code):
        EmailMessage(
            subject=f'Hackergame 登录校验码：{code}',
            body=f'{code}\n请使用该校验码登录 Hackergame\n',
            to=[identity],
        ).send()


urlpatterns = [
    path('tongji/login/', LoginView.as_view()),
    path('tongji/get_code/', GetCodeView.as_view()),
]
