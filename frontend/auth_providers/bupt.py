from datetime import timedelta

from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import path

from .base import BaseLoginView, BaseGetCodeView, DomainEmailValidator


class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '北京邮电大学'}
    provider = 'bupt'
    group = 'bupt'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')


class GetCodeView(BaseGetCodeView):
    provider = 'bupt'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('bupt.edu.cn')

    def send(self, identity, code):
        EmailMessage(
            subject=f'Hackergame 2020 登录校验码：{code}',
            body=f'{code}\n请使用该校验码登录 Hackergame 2020\n',
            to=[identity],
        ).send()


urlpatterns = [
    path('bupt/login/', LoginView.as_view()),
    path('bupt/get_code/', GetCodeView.as_view()),
]
