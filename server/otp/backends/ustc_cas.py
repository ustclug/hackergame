from urllib.request import urlopen
from uuid import uuid4
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
            legacy_identity = result.find(cas + 'user').text.strip()
            identity = result.find('attributes').find(cas + 'gid').text.strip()
            with atomic():
                device, created = Device.objects.get_or_create(backend=self.backend.id, identity=identity)
                legacy_device = None
                if legacy_identity != identity:
                    try:
                        legacy_device = Device.objects.get(
                            backend=self.backend.id, identity=legacy_identity)
                    except Device.DoesNotExist:
                        pass
                if legacy_device:
                    if legacy_device.user in (None, device.user):
                        # Remove useless legacy devices
                        legacy_device.delete()
                        legacy_device = None
                if legacy_device:
                    if not device.user:
                        # Migrate legacy devices
                        device.user = legacy_device.user
                        device.save()
                        legacy_device.delete()
                        legacy_device = None
                if not device.user:
                    device.user = self.create_user(device)
                    device.save()
                if legacy_device:
                    # Log in legacy devices which cannot be migrated
                    login(request, legacy_device.user)
                else:
                    login(request, device.user)
                return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return HttpResponseRedirect(self.login_url)

    @staticmethod
    def create_user(device):
        from ..models import User
        _ = device
        return User.objects.create_user(str(uuid4()))


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
