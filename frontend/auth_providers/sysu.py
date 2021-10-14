from datetime import timedelta

from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import path

from .base import BaseLoginView, BaseGetCodeView, DomainEmailValidator


class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '中山大学'}
    provider = 'sysu'
    group = 'sysu'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')

    def normalize_identity(self):
        return self.identity.casefold()


class GetCodeView(BaseGetCodeView):
    provider = 'sysu'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('mail2.sysu.edu.cn')

    def send(self, identity, code):
        EmailMessage(
            subject=f'Hackergame 登录校验码：{code}',
            body=f'{code}\n请使用该校验码登录 Hackergame\n',
            to=[identity],
        ).send()


urlpatterns = [
    path('sysu/login/', LoginView.as_view()),
    path('sysu/get_code/', GetCodeView.as_view()),
]
