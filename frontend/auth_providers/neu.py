from datetime import timedelta

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
        with get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host='smtp.sendgrid.net',
            port=587,
            username='apikey',
            password=settings.SENDGRID_API_KEY,
            use_tls=True,
            use_ssl=False,
        ) as connection:
            EmailMessage(
                subject=f'登录校验码：{code}',
                body=f'{code}\n请使用该校验码登录 {url}\n',
                to=[identity],
                connection=connection,
            ).send()


urlpatterns = [
    path('neu/login/', LoginView.as_view()),
    path('neu/get_code/', GetCodeView.as_view()),
]
