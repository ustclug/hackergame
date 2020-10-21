from datetime import timedelta

from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import path

from .base import BaseLoginView, BaseGetCodeView, DomainEmailValidator


class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '南开大学'}
    provider = 'nankai'
    group = 'nankai'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')


class GetCodeView(BaseGetCodeView):
    provider = 'nankai'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('mail.nankai.edu.cn')

    def send(self, identity, code):
        EmailMessage(
            subject=f'Hackergame 2020 登录校验码：{code}',
            body=f'{code}\n请使用该校验码登录 Hackergame 2020\n',
            to=[identity],
        ).send()


urlpatterns = [
    path('nankai/login/', LoginView.as_view()),
    path('nankai/get_code/', GetCodeView.as_view()),
]
