from datetime import timedelta
import requests

from django.conf import settings
from django.shortcuts import redirect
from django.urls import path

from .base import BaseLoginView, BaseGetCodeView, DomainEmailValidator


class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '哈尔滨工业大学'}
    provider = 'hit'
    group = 'hit'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')


class GetCodeView(BaseGetCodeView):
    provider = 'hit'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator(('hit.edu.cn', 'stu.hit.edu.cn'))

    def send(self, identity, code):
        requests.post(
            url='https://lug.hit.edu.cn/api/v1/sendmail',
            headers={'Authorization': 'Bearer ' + settings.HIT_MAIL_API_KEY},
            data={
                'to': identity,
                'subject': f'Hackergame 登录校验码：{code}',
                'body': f'{code}\n请使用该校验码登录 Hackergame\n',
            },
        )


urlpatterns = [
    path('hit/login/', LoginView.as_view()),
    path('hit/get_code/', GetCodeView.as_view()),
]
