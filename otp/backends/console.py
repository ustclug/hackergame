import json
from uuid import uuid4

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

    def post(self, request):
        from ..models import Device, Token
        with atomic():
            try:
                device = Device.objects.get(backend=self.backend, identity=request.POST['identity'])
            except Device.DoesNotExist:
                device = None
            token = Token.authenticate(device, request.POST['token'])
            if token:
                if not token.device.user:
                    token.device.user = self.create_user(device)
                    token.device.save()
                login(request, token.device.user)
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.error(request, '验证码错误')
                return redirect(f'otp:{self.backend}')

    def get_template_names(self):
        return f'otp/{self.backend}.html'

    @staticmethod
    def create_user(device):
        from ..models import User
        _ = device
        return User.objects.create_user(str(uuid4()))


class GetChallenge(generic.View):
    backend = None
    identity_validator = UnicodeUsernameValidator()

    def post(self, request):
        from ..models import Device, Token
        identity = json.loads(request.body)['identity']
        try:
            self.identity_validator(identity)
        except ValidationError:
            return JsonResponse({'error': 'wrong identity'}, status=400)
        with atomic():
            device, created = Device.objects.get_or_create(backend=self.backend, identity=identity)
            try:
                token = Token.generate(device)
            except Token.TooMany:
                return JsonResponse({'error': 'too many'}, status=429)
            return self.send(token)

    @staticmethod
    def send(token):
        print(f'{token.device}, token: {token.token}')
        return JsonResponse({})


class Console(Backend):
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
        return self.LoginView.as_view(backend=self.id)

    @property
    def get_challenge_view(self):
        return self.GetChallengeView.as_view(backend=self.id)
