from datetime import timedelta
import json
from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import EmailMessage
from django.core.validators import validate_email, ValidationError
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.views import View

from server.user.interface import User
from server.context import Context
from ..models import Account, Code

backend = 'django.contrib.auth.backends.ModelBackend'


# noinspection PyMethodMayBeStatic
class LoginView(View):
    def get(self, request):
        return TemplateResponse(request, 'login_nankai.html')

    def post(self, request):
        identity = request.POST.get('identity')
        code = request.POST.get('code')
        if not Code.authenticate('nankai', identity, code):
            messages.error(request, '校验码错误')
            return redirect('hub')
        account, created = Account.objects.get_or_create(
            provider='nankai',
            identity=identity,
        )
        if not account.user:
            account.user = User.create(
                Context.from_request(request),
                group='nankai',
                email=identity,
            ).user
            account.save()
        login(request, account.user, backend)
        return redirect('hub')


# noinspection PyMethodMayBeStatic
class GetCodeView(View):
    def post(self, request):
        identity = json.loads(request.body).get('identity')
        try:
            validate_email(identity)
        except ValidationError:
            return JsonResponse({'error': '邮箱格式错误'}, status=400)
        if not identity.endswith('@mail.nankai.edu.cn'):
            return JsonResponse({'error': '不是南开大学邮箱'}, status=400)
        try:
            code = Code.generate('nankai', identity, timedelta(hours=1))
        except Code.TooMany:
            return JsonResponse({'error': '校验码发送过于频繁'}, status=429)
        try:
            EmailMessage(
                subject=f'登录校验码：{code.code}',
                body=f'{code.code}\n'
                     f'请使用该校验码登录 {request.build_absolute_uri("/")}\n',
                to=[identity],
            ).send()
        except SMTPException:
            return JsonResponse({'error': '校验码发送失败'}, status=400)
        return JsonResponse({})


urlpatterns = [
    path('nankai/login/', LoginView.as_view()),
    path('nankai/get_code/', GetCodeView.as_view()),
]
