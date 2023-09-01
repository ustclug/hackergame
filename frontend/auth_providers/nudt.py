from datetime import timedelta

from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import path
from django.conf import settings

from typing import List

from .base import BaseLoginView, BaseGetCodeView, AllowlistEmailValidator

NUDT_ALLOWLIST: List[str] = []

with open(settings.NUDT_ALLOWLIST, "r") as f:
    NUDT_ALLOWLIST.extend(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), f.readlines())))
    
nudt_validator = AllowlistEmailValidator(NUDT_ALLOWLIST)

class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '国防科技大学'}
    provider = 'nudt'
    group = 'nudt'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')

    def normalize_identity(self):
        return self.identity.casefold()


class GetCodeView(BaseGetCodeView):
    provider = 'nudt'
    duration = timedelta(hours=1)
    validate_identity = nudt_validator

    def send(self, identity, code):
        EmailMessage(
            subject=f'Hackergame 登录校验码：{code}',
            body=f'{code}\n请使用该校验码登录 Hackergame\n',
            to=[identity],
        ).send()


urlpatterns = [
    path('nudt/login/', LoginView.as_view()),
    path('nudt/get_code/', GetCodeView.as_view()),
]
