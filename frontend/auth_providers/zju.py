import random
import string
import json
import hmac
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

prng = random.SystemRandom()

class LoginView(BaseLoginView):
    template_name = 'login_oauth.html'
    template_context = {'provider_name': '浙江大学统一身份认证', 'info': '此次登录需要您处在一个能够访问浙江大学内网的环境；如果您不在校内，请尝试使用 RVPN 等工具访问内网；确认能访问内网后，请单击登录按钮。'}
    provider = 'zju'
    group = 'zju'
    state_key = settings.EXTERNAL_LOGINS[provider]['state_key'].encode()
    cipher_key = b64decode(settings.EXTERNAL_LOGINS[provider]['cipher_key'])
    provider_url = settings.EXTERNAL_LOGINS[provider]['provider_url']

    @method_decorator(csrf_exempt) # XXX: POST请求来源于外部，不宜外传csrf token，且反CSRF的功能已被state+proof实现
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)


    def calc_hmac(self, state):
        return hmac.new(self.state_key, state.encode(), 'sha256').hexdigest()

    def get(self, request):
        template_context = self.template_context.copy()
        state = ''.join(prng.sample(string.ascii_letters + string.digits, 32))
        proof = self.calc_hmac(state)
        redirect_uri = request.build_absolute_uri('/accounts/zju/login/?' + urlencode({'proof': proof}))
        template_context['url'] = self.provider_url + '?' + urlencode({'redirect_uri': redirect_uri, 'state': state})
        return TemplateResponse(request, self.template_name, template_context)

    def check_cipher(self):
        try:
            ciphertext = self.request.POST.get('cipher')
            proof = self.request.GET.get('proof')
            assert isinstance(ciphertext, str) and isinstance(proof, str)
            ciphertext = b64decode(ciphertext)
            cipher = AES.new(self.cipher_key, AES.MODE_GCM, ciphertext[:16])
            payload = json.loads(cipher.decrypt_and_verify(ciphertext[16:-16], ciphertext[-16:]))
            student_id = payload['student_id']
            state = payload['state']
            assert isinstance(student_id, str) and isinstance(state, str)
            assert self.calc_hmac(state) == proof
            student_id = student_id.strip()
            # XXX: 实际上的长度是 8，但作为可信内容放宽限制来避免一些特殊情况
            if not (all(char in string.digits for char in student_id) and 5 <= len(student_id) <= 26):
                messages.error(self.request, '学号非法')
                return False
            self.sno = student_id
            self.name = payload['name']
            # XXX: 能够以此学号登录应当与拥有此邮箱等价
            self.identity = student_id + '@zju.edu.cn'
            return True
        except Exception:
            messages.error(self.request, '登录失败')
            return False

    def normalize_identity(self):
        return self.identity.casefold()

    def post(self, request):
        if self.check_cipher():
            self.login(email=self.identity, sno=self.sno, name=self.name)
        return redirect('hub')


urlpatterns = [
    path('zju/login/', LoginView.as_view()),
]
