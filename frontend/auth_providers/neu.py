from datetime import timedelta
import requests

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.shortcuts import redirect
from django.urls import path

from .base import BaseLoginView, BaseGetCodeView, DomainEmailValidator


class LoginView(BaseLoginView):
    template_name = 'login_email.html'
    template_context = {'provider_name': '东北大学'}
    provider = 'neu'
    group = 'neu'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')


class GetCodeView(BaseGetCodeView):
    provider = 'neu'
    duration = timedelta(hours=1)
    validate_identity = DomainEmailValidator('stu.neu.edu.cn')

    def send(self, identity, code):
        url = self.request.build_absolute_uri("/")
        requests.post(
            url='https://api.sendgrid.com/v3/mail/send',
            json={
                'personalizations': [{
                    'to': [{'email': identity}],
                }],
                'from': {
                    'name': settings.DEFAULT_FROM_EMAIL_NAME,
                    'email': settings.DEFAULT_FROM_EMAIL_EMAIL,
                },
                'subject': f'登录校验码：{code}',
                'content': [{
                    'type': 'text/plain',
                    'value': f'{code}\n请使用该校验码登录 {url}\n',
                }]},
            headers={'Authorization': 'Bearer ' + settings.SENDGRID_API_KEY},
        )


urlpatterns = [
    path('neu/login/', LoginView.as_view()),
    path('neu/get_code/', GetCodeView.as_view()),
]
