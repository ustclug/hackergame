from urllib.request import urlopen
from xml.etree import ElementTree

from django.conf import settings
from django.contrib.auth import login
from django.db.transaction import atomic
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, path
from django.views import generic

from .base import Backend


class Login(generic.View):
    backend = None
    cas_url = 'https://passport.ustc.edu.cn/'

    @property
    def service_url(self):
        return settings.HOST + reverse(f'otp:{self.backend.id}')

    @property
    def login_url(self):
        return self.cas_url + 'login?service=' + self.service_url

    @property
    def validate_url(self):
        return self.cas_url + 'serviceValidate?service=' + self.service_url + '&ticket={ticket}'

    def get(self, request):
        from ..models import Device
        if request.GET.get('ticket'):
            with urlopen(self.validate_url.format(ticket=request.GET['ticket'])) as req:
                result = ElementTree.fromstring(req.read())[0]
            cas = '{http://www.yale.edu/tp/cas}'
            if result.tag != cas + 'authenticationSuccess':
                return HttpResponseForbidden()
            login_name = result.find(cas + 'user').text.strip()
            identity = result.find('attributes').find(cas + 'gid').text.strip()
            with atomic():
                device, created = Device.objects.get_or_create(
                    backend=self.backend.id, identity=identity)
                if not device.user:
                    device.user = self.create_user(request, device, sno=login_name)
                    device.save()
                login(request, device.user)
                return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return HttpResponseRedirect(self.login_url)

    @staticmethod
    def create_user(request, device, **kwargs):
        from server.user.interface import User
        from server.context import Context
        return User.create(
            Context.from_request(request),
            group=device.backend,
            nickname=device.identity,
            **kwargs,
        ).user


class Ustc(Backend):
    name = '中国科学技术大学'
    LoginView = Login

    @property
    def urls(self):
        return [
            path('', self.login_view, name=self.id),
        ]

    @property
    def login_view(self):
        return self.LoginView.as_view(backend=self)
