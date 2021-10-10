from django.conf import settings
from django.shortcuts import redirect
from django.urls import path

from .base import BaseLoginView


class LoginView(BaseLoginView):
    template_name = 'login_debug.html'

    def post(self, request):
        self.provider = request.POST['provider']
        self.group = {
            'debug': 'other',
            'ustc': 'ustc',
            'sms': 'other',
        }[self.provider]
        self.identity = request.POST['identity']
        self.login()
        return redirect('hub')


urlpatterns = [
    path('debug/login/', LoginView.as_view()),
] if settings.DEBUG else []
