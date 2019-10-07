from datetime import timedelta
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import path
from django.views import generic

from .base import Backend


class Login(generic.TemplateView):
    backend = None
    template_name = 'otp/console.html'

    def post(self, request):
        from ..models import Device, Token
        with atomic():
            try:
                device = Device.objects.get(backend=self.backend.id, identity=request.POST['identity'])
            except Device.DoesNotExist:
                device = None
            token = Token.authenticate(device, request.POST['token'])
            if token:
                if not token.device.user:
                    token.device.user = self.create_user(request, device)
                    token.device.save()
                login(request, token.device.user, 'django.contrib.auth.backends.ModelBackend')
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.error(request, '验证码错误')
                return redirect(f'otp:{self.backend.id}')

    def get_context_data(self, **kwargs):
        return super().get_context_data(backend=self.backend, **kwargs)

    @staticmethod
    def create_user(request, device, **kwargs):
        from server.user.interface import User
        from server.context import Context
        return User.create(
            Context.from_request(request),
            group=device.backend,
            nickname=device.identity.partition('@')[0],
            **kwargs,
        ).user


class GetChallenge(generic.View):
    backend = None
    identity_validator = UnicodeUsernameValidator()
    token_valid_period = timedelta(minutes=10)

    def post(self, request):
        from ..models import Device, Token
        identity = json.loads(request.body)['identity']
        try:
            self.identity_validator(identity)
        except ValidationError:
            return JsonResponse({'error': 'wrong identity'}, status=400)
        with atomic():
            device, created = Device.objects.get_or_create(backend=self.backend.id, identity=identity)
            try:
                token = Token.generate(device, period=self.token_valid_period)
            except Token.TooMany:
                return JsonResponse({'error': 'too many'}, status=429)
            return self.send(token)

    @staticmethod
    def send(token):
        print(f'{token.device}, token: {token.token}')
        return JsonResponse({})


class Console(Backend):
    name = '测试用户'
    LoginView = Login
    GetChallengeView = GetChallenge

    @property
    def urls(self):
        return [
            path('', self.login_view, name=self.id),
            path('get_challenge/', self.get_challenge_view, name=f'{self.id}__get_challenge'),
        ]

    @property
    def login_view(self):
        return self.LoginView.as_view(backend=self)

    @property
    def get_challenge_view(self):
        return self.GetChallengeView.as_view(backend=self)
