from datetime import timedelta

from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import path

from .base import BaseLoginView, BaseGetCodeView, DomainEmailValidator


class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '西安电子科技大学'}
    provider = 'xidian'
    group = 'xidian'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')


class GetCodeView(BaseGetCodeView):
    provider = 'xidian'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('stu.xidian.edu.cn')

    def send(self, identity, code):
        EmailMessage(
            subject=f'Hackergame 登录校验码：{code}',
            body=f'{code}\n请使用该校验码登录 Hackergame\n',
            to=[identity],
        ).send()


urlpatterns = [
    path('xidian/login/', LoginView.as_view()),
    path('xidian/get_code/', GetCodeView.as_view()),
]
