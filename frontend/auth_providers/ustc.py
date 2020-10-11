from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree import ElementTree

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path

from ..models import UstcSnos
from .base import BaseLoginView


class LoginView(BaseLoginView):
    provider = 'ustc'
    group = 'other'  # XXX: 先加入 other，确认在读后移动至 ustc
    service: str
    ticket: str
    sno: str

    def get(self, request):
        self.service = request.build_absolute_uri('/accounts/ustc/login/')
        self.ticket = request.GET.get('ticket')
        if not self.ticket:
            return redirect('https://passport.ustc.edu.cn/login?' +
                            urlencode({'service': self.service}))
        if self.check_ticket():
            self.login(sno=self.sno)
        return redirect('hub')

    def check_ticket(self):
        try:
            with urlopen(
                'https://passport.ustc.edu.cn/serviceValidate?' +
                urlencode({'service': self.service, 'ticket': self.ticket}),
                timeout=15,
            ) as req:
                tree = ElementTree.fromstring(req.read())[0]
        except URLError:
            messages.error(self.request, '连接统一身份认证平台出错')
            return False
        cas = '{http://www.yale.edu/tp/cas}'
        if tree.tag != cas + 'authenticationSuccess':
            messages.error(self.request, '登录失败')
            return False
        self.identity = tree.find('attributes').find(cas + 'gid').text.strip()
        self.sno = tree.find(cas + 'user').text.strip()
        return True

    def on_get_account(self, account):
        def to_set(s):
            return set(s.split(',')) if s else set()
        def from_set(vs):
            return ','.join(sorted(vs))
        try:
            o = account.ustcsnos
            new_snos = from_set(to_set(o.snos) | {self.sno})
            if new_snos != o.snos:
                o.snos = new_snos
                o.save()
        except UstcSnos.DoesNotExist:
            UstcSnos.objects.create(account=account, snos=self.sno)
        return account


urlpatterns = [
    path('ustc/login/', LoginView.as_view()),
]
