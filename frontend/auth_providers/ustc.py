from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree import ElementTree

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import path
from django.views import View

from server.user.interface import User
from server.context import Context
from ..models import Account

backend = 'django.contrib.auth.backends.ModelBackend'
cas_login_url = 'https://passport.ustc.edu.cn/login?'
cas_validate_url = 'https://passport.ustc.edu.cn/serviceValidate?'
service_path = '/accounts/ustc/login/'


# noinspection PyMethodMayBeStatic
class LoginView(View):
    def get(self, request):
        service = request.build_absolute_uri(service_path)
        ticket = request.GET.get('ticket')
        if not ticket:
            url = cas_login_url + urlencode({'service': service})
            return redirect(url)
        url = cas_validate_url + urlencode({'service': service,
                                            'ticket': ticket})
        with urlopen(url) as req:
            result = ElementTree.fromstring(req.read())[0]
        cas = '{http://www.yale.edu/tp/cas}'
        if result.tag != cas + 'authenticationSuccess':
            messages.error(request, '登录失败')
            return redirect('hub')
        identity = result.find('attributes').find(cas + 'gid').text.strip()
        account, created = Account.objects.get_or_create(
            provider='ustc',
            identity=identity,
        )
        if not account.user:
            account.user = User.create(
                Context.from_request(request),
                group='ustc',
                nickname=identity,
                sno=result.find(cas + 'user').text.strip(),
            ).user
            account.save()
        login(request, account.user, backend)
        return redirect('hub')


urlpatterns = [
    path('ustc/login/', LoginView.as_view()),
]
