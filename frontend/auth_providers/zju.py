import secrets
import string
import json
from typing import Any
from Crypto.Cipher import AES
from base64 import b64decode
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .base import BaseLoginView


class LoginView(BaseLoginView):
    template_name = "login_info.html"
    template_context = {
        "provider_name": "浙江大学统一身份认证",
        "info": "此次登录需要您处在一个能够访问浙江大学内网的环境；如果您不在校内，请尝试使用 RVPN 等工具访问内网；确认能访问内网后，请单击登录按钮。",
    }
    provider = "zju"
    group = "zju"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # 避免 local_settings 未配置时出错
        provider = settings.EXTERNAL_LOGINS.get(self.provider)
        if not provider:
            raise RuntimeError(f"未配置{self.template_context['provider_name']}登录")
        self.state_key = provider["state_key"].encode()
        self.cipher_key = b64decode(provider["cipher_key"])
        self.provider_url = provider["provider_url"]

    # XXX: POST 请求到外部，不宜外传 csrf token，且反 CSRF 的功能已被 nonce 实现
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def normalize_identity(self):
        return self.identity.casefold()

    def check_cipher(self) -> bool:
        try:
            ciphertext = self.cipher
            nonce = self.request.session.get("auth_nonce_zju")
            assert isinstance(ciphertext, str) and isinstance(nonce, str)
            self.request.session.pop("auth_nonce_zju")
            # ciphertext:
            #  16 bytes: nonce
            #  16 bytes till end - 16 bytes: payload
            #  16 bytes from end: MAC
            ciphertext = b64decode(ciphertext)
            cipher = AES.new(self.cipher_key, AES.MODE_GCM, ciphertext[:16])
            cipher.update(nonce.encode())
            payload = json.loads(
                cipher.decrypt_and_verify(ciphertext[16:-16], ciphertext[-16:])
            )
            sno = payload["sno"]
            assert isinstance(sno, str)
            sno = sno.strip()
            # XXX: 实际上的长度是 8，但作为可信内容放宽限制来避免一些特殊情况
            if not (
                all(char in string.digits for char in sno)
                and 5 <= len(sno) <= 26
            ):
                messages.error(self.request, "学号非法")
                return False
            self.sno = sno
            self.name = payload["name"]
            # XXX: 能够以此学号登录应当与拥有此邮箱等价
            self.identity = sno + "@zju.edu.cn"
            return True
        except Exception:
            messages.error(self.request, "登录失败")
            return False

    def get(self, request):
        self.cipher = request.GET.get("cipher")
        if self.cipher:
            if self.check_cipher():
                self.login(email=self.identity, sno=self.sno, name=self.name)
            return redirect("hub")
        template_context = self.template_context.copy()
        nonce = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
        )
        request.session['auth_nonce_zju'] = nonce

        # 在登录前显示提示信息（而非直接跳转）
        redirect_uri = request.build_absolute_uri("/accounts/zju/login/")
        template_context["url"] = (
            self.provider_url
            + "?"
            + urlencode({"redirect_uri": redirect_uri, "nonce": nonce})
        )
        return TemplateResponse(request, self.template_name, template_context)


urlpatterns = [
    path("zju/login/", LoginView.as_view()),
]
