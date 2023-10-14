from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree import ElementTree

from django.http import HttpRequest
from django.contrib import messages
from django.shortcuts import redirect

from typing import Optional, Any

from .base import BaseLoginView


class CASBaseLoginView(BaseLoginView):
    cas_name: str
    cas_login_url: str
    cas_service_validate_url: str

    YALE_CAS_URL = "{http://www.yale.edu/tp/cas}"

    def login_attrs(self) -> dict[str, Any]:
        raise NotImplementedError("CAS 登录需要实现 login_attrs()")

    def get(self, request: HttpRequest):
        self.service = request.build_absolute_uri(request.path)
        self.ticket = request.GET.get("ticket")
        if not self.ticket:
            return redirect(
                self.cas_login_url + "?" + urlencode({"service": self.service})
            )
        if self.check_ticket():
            self.login(**self.login_attrs())
        return redirect("hub")

    def check_ticket(self) -> Optional[ElementTree.Element]:
        try:
            with urlopen(
                self.cas_service_validate_url
                + "?"
                + urlencode({"service": self.service, "ticket": self.ticket}),
                timeout=15,
            ) as req:
                tree = ElementTree.fromstring(req.read())[0]
        except URLError:
            messages.error(self.request, f"连接{self.cas_name}出错")
            return None
        cas = "{http://www.yale.edu/tp/cas}"
        if tree.tag != cas + "authenticationSuccess":
            messages.error(self.request, "登录失败")
            return None
        return tree
