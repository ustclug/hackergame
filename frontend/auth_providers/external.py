import requests

from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect

from .base import BaseGetCodeView, BaseLoginView, ExternalProviderError


class ExternalLoginView(BaseLoginView):
    template_name = 'login_email.html'

    def post(self, request):
        if self.check_code():
            self.login(email=self.identity)
        return redirect('hub')

    def normalize_identity(self):
        return self.identity.casefold()


class ExternalGetCodeView(BaseGetCodeView):
    """
    使用该类预期 external provider 实现了以下接口：

    POST <提供的 url>
    HTTP 头部：
        Authorization: Bearer <提供的 key>
    正文 JSON 参数：
        to: 接收验证码的地址
        subject: 邮件标题
        body: 邮件正文
        ip: 请求发送邮件的客户端 IP 地址
    返回的 HTTP Code：
        200: 响应正常，邮件可能发送成功或失败
        其他: 视为邮件发送失败（可能是服务配置错误导致），response 的正文内容不会返回给用户
    返回的 HTTP 响应正文 JSON 参数：
        success: 布尔值，表示邮件是否发送成功
        msg: 字符串，表示邮件发送失败（检查不通过，或出现网络问题等时的错误信息）

    需要保证在合理的时间内完成发信，否则可能会触发超时。

    external provider 可能需要额外实现邮件地址检查（如果有更加复杂，无法被正则涵盖的检查逻辑），
    以及限流（如果有更加复杂的限流逻辑）。
    """
    provider: str

    def send(self, identity, code):
        use_smtp = settings.EXTERNAL_LOGINS[self.provider]['use_smtp']
        url = settings.EXTERNAL_LOGINS[self.provider].get('url', None)
        key = settings.EXTERNAL_LOGINS[self.provider].get('key', None)

        if settings.DEBUG or use_smtp:
            EmailMessage(
                subject=f'Hackergame 登录校验码：{code}',
                body=f'{code}\n请使用该校验码登录 Hackergame\n',
                to=[identity],
            ).send()
        else:
            response = requests.post(
                url=url,
                headers={'Authorization': 'Bearer ' + key},
                json={
                    'to': identity,
                    'subject': f'Hackergame 登录校验码：{code}',
                    'body': f'{code}\n请使用该校验码登录 Hackergame\n',
                    'ip': self.request.META['REMOTE_ADDR'],
                },
                timeout=15,
            )
            status_code = response.status_code
            if status_code != 200:
                raise ExternalProviderError("校验码邮件因未知原因发送失败。")
            response_json = response.json()
            if not response_json['success']:
                raise ExternalProviderError("校验码邮件发送失败：" + response_json['msg'])
