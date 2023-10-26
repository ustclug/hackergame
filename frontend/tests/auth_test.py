from django.test import TestCase, Client
from django.contrib import auth
from django.urls import reverse
from frontend.models import Account
from server.context import Context

from server.user.interface import User
from ..auth_providers.ustc import LoginView as USTCLoginView
from ..auth_providers.sustech import LoginView as SUSTECHLoginView
from unittest import mock
from contextlib import contextmanager
import json


USTC_CAS_EXAMPLE_RESPONSE = """<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
<cas:authenticationSuccess>
<cas:user>SA21011000</cas:user>
<attributes>
<cas:xbm>1</cas:xbm>
<cas:logintime>2020-02-30 12:34:56</cas:logintime>
<cas:gid>2201234567</cas:gid>
<cas:loginip>192.0.2.0</cas:loginip>
</attributes>
</cas:authenticationSuccess>
</cas:serviceResponse>"""

SUSTECH_CAS_EXAMPLE_RESPONSE = """<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
<cas:authenticationSuccess>
    <cas:user>11899999</cas:user>
    <cas:attributes>
      <cas:mail>11899999@mail.sustech.edu.cn</cas:mail>
      <cas:givenName>San</cas:givenName>
      <cas:sn>ZHANG</cas:sn>
      <cas:cn>ZHANG San</cas:cn>
    </cas:attributes>
  </cas:authenticationSuccess>
</cas:serviceResponse>"""


class MockResponse:
    def __init__(self, text):
        self.text = text

    def read(self):
        return self.text.encode("utf-8")


@contextmanager
def mock_urlopen(url, timeout=None):
    success = False
    if "ustc.edu.cn" in url:
        if "serviceValidate" in url:
            success = True
            yield MockResponse(USTC_CAS_EXAMPLE_RESPONSE)
    elif "sso.cra.ac.cn" in url:
        if "serviceValidate" in url:
            success = True
            yield MockResponse(SUSTECH_CAS_EXAMPLE_RESPONSE)
    if not success:
        raise ValueError("Unknown URL")


@mock.patch("frontend.auth_providers.cas.urlopen", new=mock_urlopen)
def ustc_check_ticket():
    v = USTCLoginView()
    v.service = "http://example.com/accounts/ustc/login/"
    v.ticket = "ST-1234567890"
    return v, v.check_ticket()


@mock.patch("frontend.auth_providers.cas.urlopen", new=mock_urlopen)
def sustech_check_ticket():
    v = SUSTECHLoginView()
    v.service = "http://example.com/accounts/sustech/login/"
    v.ticket = "ST-1234567890"
    return v, v.check_ticket()


class AuthProviderCASServiceValidateTest(TestCase):
    def test_ustc(self):
        v, tree = ustc_check_ticket()
        self.assertEqual(tree.tag, "{http://www.yale.edu/tp/cas}authenticationSuccess")
        self.assertEqual(v.identity, "2201234567")
        self.assertEqual(v.sno, "SA21011000")

    def test_sustech(self):
        v, tree = sustech_check_ticket()
        self.assertEqual(tree.tag, "{http://www.yale.edu/tp/cas}authenticationSuccess")
        self.assertEqual(v.identity, "11899999")
        self.assertEqual(v.email, "11899999@mail.sustech.edu.cn")
        self.assertEqual(v.name, "ZHANG San")


class AuthProviderCASHasImplementedLoginAttrs(TestCase):
    def test_ustc(self):
        v, _ = ustc_check_ticket()
        v.login_attrs()

    def test_sustech(self):
        v, _ = sustech_check_ticket()
        v.login_attrs()


class AuthProviderCASLoginTest(TestCase):
    def setUp(self) -> None:
        self.c = Client()

    @mock.patch("frontend.auth_providers.cas.urlopen", new=mock_urlopen)
    def test_ustc(self):
        self.c.logout()
        resp = self.c.get("/accounts/ustc/login/", {"ticket": "ST-1234567890"})
        self.assertRedirects(resp, reverse("hub"), target_status_code=302)
        self.assert_(auth.get_user(self.c).is_authenticated)

    @mock.patch("frontend.auth_providers.cas.urlopen", new=mock_urlopen)
    def test_sustech(self):
        self.c.logout()
        resp = self.c.get("/accounts/sustech/login/", {"ticket": "ST-1234567890"})
        self.assertRedirects(resp, reverse("hub"), target_status_code=302)
        self.assert_(auth.get_user(self.c).is_authenticated)


class AccountLogViewPermission(TestCase):
    def setUp(self) -> None:
        self.c = Client()
        self.u = User.create(Context(elevated=True), group='other')
        Account.objects.create(provider='debug', identity='root', user=self.u.user)

    def test_anonymous(self):
        resp = self.c.post(
            reverse("account"),
            data=json.dumps({"method": "accountlog", "user": self.u.pk}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        code = resp.json()["error"]['code']
        self.assertEqual(code, 'permission_required')

    @mock.patch("frontend.auth_providers.cas.urlopen", new=mock_urlopen)
    def test_low_privilege(self):
        # get a ustc account
        self.c.logout()
        resp = self.c.get("/accounts/sustech/login/", {"ticket": "ST-1234567890"})
        self.assert_(auth.get_user(self.c).is_authenticated)
        resp = self.c.post(
            reverse("account"),
            data=json.dumps({"method": "accountlog", "user": self.u.pk}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        code = resp.json()["error"]['code']
        self.assertEqual(code, 'permission_required')
