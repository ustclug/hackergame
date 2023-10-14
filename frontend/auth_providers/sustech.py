from xml.etree import ElementTree

from django.urls import path

from typing import Any, Optional

from ..models import AccountLog
from .cas import CASBaseLoginView


class LoginView(CASBaseLoginView):
    provider = 'sustech'
    group = 'sustech'
    service: str
    ticket: str
    sno: str

    cas_name = 'CRA SSO / SUSTech CAS'
    cas_login_url = 'https://sso.cra.ac.cn/realms/cra-service-realm/protocol/cas/login'
    cas_service_validate_url = 'https://sso.cra.ac.cn/realms/cra-service-realm/protocol/cas/serviceValidate'

    def login_attrs(self) -> dict[str, Any]:
        return {
            "sno": self.identity,
            "email": self.email,
            "name": self.name,
        }

    def check_ticket(self) -> Optional[ElementTree.Element]:
        tree = super().check_ticket()
        if not tree:
            return None
        self.identity = tree.find(self.YALE_CAS_URL + 'user').text.strip()
        self.email = tree.find(self.YALE_CAS_URL + 'attributes').find(self.YALE_CAS_URL + 'mail').text.strip()
        self.name = tree.find(self.YALE_CAS_URL + 'attributes').find(self.YALE_CAS_URL + 'cn').text.strip()
        return tree

    def on_get_account(self, account):
        def to_set(s):
            return set(s.split(',')) if s else set()
        def from_set(vs):
            return ','.join(sorted(vs))
        custom_attrs: list[tuple[str, str]] = [
            ('邮箱', self.email),
            ('姓名', self.name)
        ]
        for display_name, self_value in custom_attrs:
            try:
                o = AccountLog.objects.get(account=account, content_type=display_name)
                new_value = from_set(to_set(o.contents) | {self_value})
                if new_value != o.contents:
                    o.contents = new_value
                    o.save()
            except AccountLog.DoesNotExist:
                AccountLog.objects.create(account=account, contents=f"{self_value}", content_type=display_name)
        return account


urlpatterns = [
    path('sustech/login/', LoginView.as_view()),
]
