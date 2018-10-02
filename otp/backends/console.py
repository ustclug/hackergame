import json
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.db.transaction import atomic
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import path
from django.views import generic

from .base import Backend


class Login(generic.TemplateView):
    template_name = 'otp/console/login.html'

    @staticmethod
    def post(request):
        from ..models import User, Device, Token
        with atomic():
            device = Device.objects.get(backend='console', identity=request.POST['username'])
            token = Token.authenticate(device, request.POST['token'])
            if token:
                if not token.device.user:
                    token.device.user = User.objects.create_user(str(uuid4()))
                    token.device.save()
                login(request, token.device.user)
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.error(request, '验证码错误')
                return redirect('otp:console')


class GetChallenge(generic.View):
    @staticmethod
    def post(request):
        from ..models import Device, Token
        username = json.loads(request.body)['username']
        with atomic():
            device, created = Device.objects.get_or_create(backend='console', identity=username)
            try:
                token = Token.generate(device)
            except Token.TooMany:
                return JsonResponse({'error': 'too many'}, status=429)
            print(f'{device}, token: {token.token}')
            return JsonResponse({})


class Console(Backend):
    @property
    def urls(self):
        return [
            path('', Login.as_view(), name='console'),
            path('get_challenge/', GetChallenge.as_view(), name='console__get_challenge'),
        ]
