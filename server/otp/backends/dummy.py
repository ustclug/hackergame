from django.conf import settings
from django.contrib.auth import login
from django.db.transaction import atomic
from django.shortcuts import redirect
from django.urls import path

from .console import Console


class Login(Console.LoginView):
    backend = None
    template_name = 'otp/dummy.html'

    def post(self, request):
        from ..models import Device
        with atomic():
            device, created = Device.objects.get_or_create(backend=self.backend.id, identity=request.POST['identity'])
            if not device.user:
                device.user = self.create_user(device)
                device.save()
            login(request, device.user)
            return redirect(settings.LOGIN_REDIRECT_URL)


class Dummy(Console):
    LoginView = Login

    @property
    def urls(self):
        return [
            path('', self.login_view, name=self.id),
        ]

    @property
    def login_view(self):
        return self.LoginView.as_view(backend=self)
