from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.views import View

from server.user.interface import User
from server.context import Context
from ..models import Account

backend = 'django.contrib.auth.backends.ModelBackend'


# noinspection PyMethodMayBeStatic
class LoginView(View):
    def get(self, request):
        return TemplateResponse(request, 'login_debug.html')

    def post(self, request):
        provider = request.POST['provider']
        identity = request.POST['identity']
        account, created = Account.objects.get_or_create(
            provider=provider,
            identity=identity,
        )
        if not account.user:
            account.user = User.create(
                Context.from_request(request),
                group={
                    'debug': 'other',
                    'ustc': 'ustc',
                    'nankai': 'nankai',
                    'sms': 'other',
                }[provider],
            ).user
            account.save()
        login(request, account.user, backend)
        return redirect('hub')


urlpatterns = [
    path('debug/login/', LoginView.as_view()),
] if settings.DEBUG else []
