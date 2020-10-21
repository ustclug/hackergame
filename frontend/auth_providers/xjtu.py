from datetime import timedelta

from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import path

from .base import BaseLoginView, BaseGetCodeView, DomainEmailValidator


class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '西安交通大学'}
    provider = 'xjtu'
    group = 'xjtu'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')


class GetCodeView(BaseGetCodeView):
    provider = 'xjtu'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('stu.xjtu.edu.cn')

    def send(self, identity, code):
        EmailMessage(
            subject=f'Hackergame 2020 登录校验码：{code}',
            body=f'{code}\n请使用该校验码登录 Hackergame 2020\n',
            to=[identity],
        ).send()


urlpatterns = [
    path('xjtu/login/', LoginView.as_view()),
    path('xjtu/get_code/', GetCodeView.as_view()),
]
