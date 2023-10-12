from xml.etree import ElementTree

from django.urls import path

from typing import Optional

from ..models import UstcSnos
from .cas import CASBaseLoginView


class LoginView(CASBaseLoginView):
    provider = 'ustc'
    group = 'other'  # XXX: 先加入 other，确认在读后移动至 ustc
    service: str
    ticket: str
    sno: str

    cas_name = '统一身份认证平台'
    cas_login_url = 'https://passport.ustc.edu.cn/login'
    cas_service_validate_url = 'https://passport.ustc.edu.cn/serviceValidate'

    def check_ticket(self) -> Optional[ElementTree.Element]:
        tree = super().check_ticket()
        if not tree:
            return None
        self.identity = tree.find('attributes').find(self.YALE_CAS_URL + 'gid').text.strip()
        self.sno = tree.find(self.YALE_CAS_URL + 'user').text.strip()
        return tree

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
