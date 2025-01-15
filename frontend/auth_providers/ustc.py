from xml.etree import ElementTree

from django.urls import path

from typing import Optional, Any

from ..models import AccountLog
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

    def login_attrs(self) -> dict[str, Any]:
        return {
            "sno": self.sno,
        }

    def check_ticket(self) -> Optional[ElementTree.Element]:
        tree = super().check_ticket()
        if tree is None:
            return None
        attributes = tree.find(self.YALE_CAS_URL + 'attributes')
        if attributes is None:
            # compatibility with old ustc cas
            attributes = tree.find('attributes')
        self.identity = attributes.find(self.YALE_CAS_URL + 'gid').text.strip()
        self.sno = tree.find(self.YALE_CAS_URL + 'user').text.strip()
        return tree

    def on_get_account(self, account):
        def to_set(s):
            return set(s.split(',')) if s else set()
        def from_set(vs):
            return ','.join(sorted(vs))
        try:
            o = AccountLog.objects.get(account=account, content_type='学号')
            new_snos = from_set(to_set(o.contents) | {self.sno})
            if new_snos != o.contents:
                o.contents = new_snos
                o.save()
        except AccountLog.DoesNotExist:
            AccountLog.objects.create(account=account, contents=f"{self.sno}", content_type='学号')
        return account


urlpatterns = [
    path('ustc/login/', LoginView.as_view()),
]
